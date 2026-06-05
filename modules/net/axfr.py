PROVIDES = []
REQUIRES = ["domain"]


def run(data, cred, args):
    import re
    import subprocess
    from pathlib import Path

    from core.target import (
        load_current_profile,
        save_profile
    )

    # --- ANSI ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    domain = data.get("domain")
    target_ip = data.get("ip")

    if not domain:
        print(f"\n{R}[!] {W}{BOLD}NO DOMAIN CONFIGURED{W}")
        return

    if not target_ip:
        print(f"\n{R}[!] {W}{BOLD}NO TARGET IP CONFIGURED{W}")
        return

    print(f"\n{B}[{W}{G}*{W}{B}]{W} Running AXFR against {Y}{domain}{W}")

    result = subprocess.run(
        [
            "dig",
            "axfr",
            domain,
            f"@{target_ip}"
        ],
        capture_output=True,
        text=True
    )

    output = result.stdout

    if not output.strip():
        print(f"\n{R}[!] Zone transfer failed{W}")
        return

    # ------------------------------------------
    # PASS 1 - A RECORDS
    # ------------------------------------------

    records = {}

    for line in output.splitlines():

        match = re.search(
            r"^(\S+)\s+\d+\s+IN\s+A\s+(\d+\.\d+\.\d+\.\d+)$",
            line.strip()
        )

        if not match:
            continue

        fqdn = match.group(1).rstrip(".").lower()
        ip = match.group(2)

        # HTB virtual host fix
        if ip.startswith("127."):
            ip = target_ip

        records[fqdn] = ip

    # ------------------------------------------
    # PASS 2 - CNAME RECORDS
    # ------------------------------------------

    for line in output.splitlines():

        match = re.search(
            r"^(\S+)\s+\d+\s+IN\s+CNAME\s+(\S+)$",
            line.strip()
        )

        if not match:
            continue

        source = match.group(1).rstrip(".").lower()
        destination = match.group(2).rstrip(".").lower()

        if destination in records:
            records[source] = records[destination]

    if not records:
        print(f"\n{R}[!] No useful DNS records discovered{W}")
        return

    hosts_entries = []

    for fqdn, ip in sorted(records.items()):

        hostname = fqdn.split(".")[0]

        hosts_entries.append(
            f"{ip} {fqdn} {hostname}"
        )

    # ------------------------------------------
    # UPDATE /etc/hosts
    # ------------------------------------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} Updating /etc/hosts"
    )

    try:

        hosts_path = Path("/etc/hosts")
        existing = hosts_path.read_text()

        new_entries = [
            entry
            for entry in hosts_entries
            if entry not in existing
        ]

        if new_entries:

            temp = Path("/tmp/ctf_axfr_hosts.txt")

            temp.write_text(
                "\n".join(new_entries) + "\n"
            )

            subprocess.run(
                f"sudo sh -c 'cat {temp} >> /etc/hosts'",
                shell=True
            )

            print(
                f"{G}[+]{W} Added "
                f"{Y}{len(new_entries)}{W} "
                f"host entries"
            )

        else:

            print(
                f"{B}[*]{W} Hosts already synchronized"
            )

    except Exception as e:

        print(
            f"{Y}[!]{W} Failed updating hosts file: {e}"
        )

    # ------------------------------------------
    # PROFILE UPDATE
    # ------------------------------------------

    profile, profile_path = load_current_profile()

    for fqdn in records:

        hostname = fqdn.split(".")[0]

        if hostname.lower().startswith("dc"):

            profile["hostname"] = hostname
            profile["dc"] = records[fqdn]
            break

    save_profile(
        profile,
        profile_path
    )

    # ------------------------------------------
    # RESULTS
    # ------------------------------------------

    print(
        f"\n{G}┌── AXFR COMPLETE ────────────────────────────────────────┐{W}"
    )
    print(
        f"{G}│{W} {B}Records:{W} {C}{len(records):<46}{W}{G}│{W}"
    )
  
    print(
        f"{G}└─────────────────────────────────────────────────────────┘{W}\n"
    )

    for fqdn, ip in sorted(records.items()):
        print(
            f"{C}{ip:<16}{W} {fqdn}"
        )

    print()