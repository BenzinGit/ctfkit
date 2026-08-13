"""Network analyzer for the CTFKit Linux privilege-escalation enumeration."""

import ipaddress
import re


MODULE = "NETWORK"

SENSITIVE_PORTS = {
    2375: "Docker API", 2376: "Docker API (TLS)", 3306: "MySQL/MariaDB",
    5432: "PostgreSQL", 6379: "Redis", 11211: "Memcached", 27017: "MongoDB",
    9200: "Elasticsearch", 5984: "CouchDB", 5000: "container registry/web service",
    6443: "Kubernetes API server", 10250: "Kubelet API", 10255: "Kubelet read-only API",
}
WEB_PORTS = {80, 443, 3000, 8000, 8080, 8081, 8443, 8888, 9000, 9090}
CONTAINER_PREFIXES = ("docker", "br-", "lxc", "lxd", "cni", "flannel", "kube")
TUNNEL_PREFIXES = ("tun", "tap", "wg", "ppp", "tailscale", "zt")


def _get_command_output(section, command):
    pattern = r">>> COMMAND: {}\n\n(.*?)(?=\n>>> COMMAND:|\Z)".format(re.escape(command))
    match = re.search(pattern, section, re.S)
    return match.group(1).strip() if match else ""


def _port_label(port):
    if port in SENSITIVE_PORTS:
        return SENSITIVE_PORTS[port]
    if port in WEB_PORTS:
        return "web/admin service"
    return None


def _service_endpoint(value):
    value = value.strip()
    if value.startswith("["):
        match = re.match(r"^\[([^]]+)\]:(\d+)$", value)
        return match.groups() if match else (None, None)
    if ":" not in value:
        return None, None
    host, port = value.rsplit(":", 1)
    return host, port


def _parse_sockets(text):
    sockets = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("Netid", "State", "Cannot")):
            continue
        parts = line.split(None, 6)
        if len(parts) < 6 or parts[0] not in ("tcp", "tcp6", "udp", "udp6"):
            continue
        host, port = _service_endpoint(parts[4])
        if not host or not port.isdigit():
            continue
        sockets.append({
            "protocol": parts[0].replace("6", ""),
            "state": parts[1],
            "host": host.split("%", 1)[0],
            "port": int(port),
            "process": parts[6] if len(parts) > 6 else "",
        })
    return sockets


def _interface_type(name):
    lowered = name.lower()
    if lowered == "lo":
        return "loopback"
    if lowered.startswith("veth"):
        return "container-peer"
    if lowered.startswith(CONTAINER_PREFIXES):
        return "container"
    if lowered.startswith(TUNNEL_PREFIXES):
        return "tunnel"
    return "network"


def _parse_interfaces(text):
    interfaces = []
    current = None
    for line in text.splitlines():
        header = re.match(r"^\d+:\s+([^:]+):", line)
        if header:
            name = header.group(1).split("@", 1)[0]
            state = re.search(r"\bstate\s+(\S+)", line)
            current = {
                "name": name,
                "type": _interface_type(name),
                "addresses": [],
                "active": bool(state and state.group(1) == "UP" and "NO-CARRIER" not in line),
            }
            interfaces.append(current)
            continue
        if not current:
            continue
        address = re.match(r"^\s+inet\s+(\S+)", line)
        if address:
            try:
                network = ipaddress.ip_interface(address.group(1))
            except ValueError:
                continue
            if not network.ip.is_loopback and not network.ip.is_link_local:
                current["addresses"].append(str(network))
    return interfaces


def _parse_routes(text):
    routes = []
    for line in text.splitlines():
        parts = line.split()
        if not parts or parts[0].startswith(("default", "blackhole", "unreachable")):
            if not parts or parts[0] != "default":
                continue
        destination = parts[0]
        gateway = parts[parts.index("via") + 1] if "via" in parts and parts.index("via") + 1 < len(parts) else None
        interface = parts[parts.index("dev") + 1] if "dev" in parts and parts.index("dev") + 1 < len(parts) else None
        if destination != "default":
            try:
                network = ipaddress.ip_network(destination, strict=False)
            except ValueError:
                continue
            if network.is_loopback or network.is_link_local:
                continue
        routes.append({"destination": destination, "gateway": gateway, "interface": interface})
    return routes


def _parse_arp(text):
    neighbors = []
    for line in text.splitlines():
        match = re.search(r"\(([^)]+)\)\s+at\s+([0-9a-f:]{17}).*?\son\s+(\S+)", line, re.I)
        if match:
            neighbors.append({"ip": match.group(1), "mac": match.group(2), "interface": match.group(3)})
    return neighbors


def _parse_resolvers(text):
    nameservers, domains = [], []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0] == "nameserver":
            nameservers.append(parts[1])
        elif len(parts) >= 2 and parts[0] in ("search", "domain"):
            domains.extend(parts[1:])
    return {"nameservers": nameservers, "domains": domains}


def _is_loopback(host):
    return host.startswith("127.") or host == "::1"


def _is_wildcard(host):
    return host in ("0.0.0.0", "::", "*")


def _is_systemd_stub(socket):
    return _is_loopback(socket["host"]) and socket["port"] == 53


def _render_report(sockets, interfaces, routes, neighbors, resolvers):
    report = []
    local = [item for item in sockets if _is_loopback(item["host"]) and not _is_systemd_stub(item)]
    interesting_local = [item for item in local if _port_label(item["port"])]
    container_interfaces = [item for item in interfaces if item["type"] == "container" and item["active"]]
    tunnel_interfaces = [item for item in interfaces if item["type"] == "tunnel" and item["active"]]

    if interesting_local:
        report.extend(["High-value localhost services", "-" * 29])
        for item in interesting_local:
            report.append("{}://{}:{}  {}".format(item["protocol"], item["host"], item["port"], _port_label(item["port"])))
        report.append("")
    elif local:
        report.extend(["Localhost-only services", "-" * 23])
        for item in local:
            report.append("{}://{}:{}".format(item["protocol"], item["host"], item["port"]))
        report.append("")

    if container_interfaces or tunnel_interfaces:
        report.extend(["Special network interfaces", "-" * 26])
        for item in container_interfaces + tunnel_interfaces:
            addresses = ", ".join(item["addresses"]) or "no IPv4 address"
            report.append("{}  [{}]  {}".format(item["name"], item["type"], addresses))
        report.append("")

    non_default_routes = [route for route in routes if route["destination"] != "default"]
    if non_default_routes:
        report.extend(["Reachable networks", "-" * 18])
        for route in non_default_routes:
            via = " via {}".format(route["gateway"]) if route["gateway"] else ""
            dev = " dev {}".format(route["interface"]) if route["interface"] else ""
            report.append("{}{}{}".format(route["destination"], via, dev))
        report.append("")

    if neighbors:
        report.extend(["ARP neighbors", "-" * 13])
        for neighbor in neighbors:
            report.append("{}  {}  ({})".format(neighbor["ip"], neighbor["interface"], neighbor["mac"]))
        report.append("")

    external_resolvers = [item for item in resolvers["nameservers"] if not item.startswith("127.") and item != "::1"]
    if external_resolvers or resolvers["domains"]:
        report.extend(["DNS clues", "-" * 9])
        if external_resolvers:
            report.append("Resolvers: {}".format(", ".join(external_resolvers)))
        if resolvers["domains"]:
            report.append("Domains: {}".format(", ".join(resolvers["domains"])))

    return "\n".join(report)


def analyze(section):
    """Analyze the NETWORK section emitted by tools/linux_enum.sh."""
    sockets = _parse_sockets(_get_command_output(section, "ss -tunlp"))
    interfaces = _parse_interfaces(_get_command_output(section, "ip addr"))
    routes = _parse_routes(_get_command_output(section, "ip route"))
    neighbors = _parse_arp(_get_command_output(section, "arp -a"))
    resolvers = _parse_resolvers(_get_command_output(section, "cat /etc/resolv.conf"))

    findings = []
    seen = set()
    for socket in sockets:
        label = _port_label(socket["port"])
        if not label:
            continue
        exposure = "localhost-only" if _is_loopback(socket["host"]) else "network-exposed" if _is_wildcard(socket["host"]) else "bound to {}".format(socket["host"])
        key = (socket["protocol"], socket["host"], socket["port"])
        if key in seen:
            continue
        seen.add(key)
        findings.append({
            "priority": "HIGH" if _is_loopback(socket["host"]) or _is_wildcard(socket["host"]) else "MEDIUM",
            "module": MODULE,
            "title": "{} {}:{}".format(label, socket["host"], socket["port"]),
            "reason": "{} is {} and may be reachable from the target host or an internal interface.".format(label, exposure),
            "recommendation": ["Review the owning process and test the service from the target host."],
        })

    active_container_names = set()
    for interface in interfaces:
        if interface["type"] not in ("container", "tunnel") or not interface["active"]:
            continue
        if interface["type"] == "container":
            active_container_names.add(interface["name"])
        findings.append({
            "priority": "MEDIUM",
            "module": MODULE,
            "title": "{} interface: {}".format(interface["type"].title(), interface["name"]),
            "reason": "This interface can expose an additional container or pivot network.",
            "recommendation": ["Review routes and enumerate hosts on its attached private network."],
        })

    for neighbor in neighbors:
        if neighbor["interface"] not in active_container_names:
            continue
        findings.append({
            "priority": "MEDIUM",
            "module": MODULE,
            "title": "Container-network neighbor: {}".format(neighbor["ip"]),
            "reason": "A live ARP neighbor is reachable through the active {} bridge.".format(neighbor["interface"]),
            "recommendation": ["Test connectivity to {} from the target host.".format(neighbor["ip"])],
        })

    if resolvers["domains"]:
        findings.append({
            "priority": "LOW",
            "module": MODULE,
            "title": "DNS search domain: {}".format(", ".join(resolvers["domains"])),
            "reason": "Internal DNS suffixes often reveal reachable hostnames or an AD domain.",
            "recommendation": ["Use the domain suffix when enumerating internal web and directory services."],
        })

    return {
        "module": MODULE,
        "summary": {
            "Listening sockets": len(sockets),
            "Localhost-only": sum(1 for item in sockets if _is_loopback(item["host"]) and not _is_systemd_stub(item)),
            "Routes": len(routes),
            "ARP neighbors": len(neighbors),
            "External DNS": sum(1 for item in resolvers["nameservers"] if not item.startswith("127.") and item != "::1"),
        },
        "findings": findings,
        "report": _render_report(sockets, interfaces, routes, neighbors, resolvers),
        "details": {"sockets": sockets, "interfaces": interfaces, "routes": routes, "neighbors": neighbors, "resolvers": resolvers},
    }
