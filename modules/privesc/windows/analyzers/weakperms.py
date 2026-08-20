"""
CTFKit - Windows PrivEsc
Weak Permissions Analyzer
"""

import re

from rich.console import Group
from rich.table import Table
from rich.text import Text


SECTION = "WEAKPERMS"


# ==========================================
# KNOWLEDGE BASE
# ==========================================

#
# Well-known SIDs as they appear in SDDL strings from `sc.exe sdshow`.
# DC = SERVICE_CHANGE_CONFIG — the right that lets you rewrite a service's
# binPath without touching the file itself.
#
SID_NAMES = {
    "AU": "Authenticated Users",
    "WD": "Everyone",
    "BU": "BUILTIN\\Users",
    "IU": "Interactive Users",
}


# ==========================================
# HELPERS
# ==========================================

def _get_command_output(section, command):
    #
    # Lookahead intentionally has no leading \n: when a check's output is
    # genuinely empty (e.g. no weak registry ACLs found), the marker's own
    # trailing blank line and the next marker's boundary collapse into a
    # single \n\n, leaving nothing for a \n-prefixed lookahead to anchor on
    # — it would then swallow the entire next section as "content" instead
    # of matching empty. The trailing .strip() cleans up either way.
    #
    pattern = rf">>> COMMAND: {re.escape(command)}\n\n(.*?)(?=>>> COMMAND:|\Z)"
    match = re.search(pattern, section, re.S)
    return match.group(1).strip() if match else ""


def _blocks(text):
    return [b for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]


def _parse_services(text):

    services = {}

    for block in _blocks(text):

        fields = {}

        for line in block.splitlines():

            match = re.match(r"^(\w+)\s*:\s*(.*)$", line.strip())

            if match:
                fields[match.group(1)] = match.group(2).strip()

        name = fields.get("Name")

        if name:
            services[name] = fields

    return services


def _icacls_has_write(line):

    #
    # icacls rights are comma-separated inside each paren group, e.g.
    # "(RX,W)" or "(F)" — RX/R alone can't modify the file, F/M/W can.
    #
    for token in re.findall(r"\(([^)]*)\)", line):

        parts = [p.strip() for p in token.split(",")]

        if any(p in ("F", "M", "W") for p in parts):
            return True

    return False


def _parse_weak_binaries(text):

    findings = []

    for block in _blocks(text):

        lines = block.splitlines()

        if not lines or not lines[0].strip().startswith("SERVICE:"):
            continue

        name = lines[0].split("SERVICE:", 1)[1].strip()

        path = ""
        grants = []

        for line in lines[1:]:

            line = line.strip()

            if line.startswith("PATH:"):
                path = line.split("PATH:", 1)[1].strip()
            elif line:
                grants.append(line)

        writable = [g for g in grants if _icacls_has_write(g)]

        if writable:
            findings.append({"service": name, "path": path, "grants": writable})

    return findings


def _parse_weak_service_acl(text):

    findings = []

    for block in _blocks(text):

        name = None
        sddl = None

        for line in block.splitlines():

            line = line.strip()

            if line.startswith("SERVICE:"):
                name = line.split("SERVICE:", 1)[1].strip()
            elif line.startswith("SDDL:"):
                sddl = line.split("SDDL:", 1)[1].strip()

        if not name or not sddl:
            continue

        sids = set()

        for rights, sid in re.findall(r"\(A;;([A-Z]*);;;([A-Z]+)\)", sddl):

            if "DC" in rights and sid in SID_NAMES:
                sids.add(sid)

        if sids:
            findings.append({
                "service": name,
                "principals": [SID_NAMES[s] for s in sorted(sids)],
                "sddl": sddl,
            })

    return findings


def _parse_weak_registry(text):

    weak = {}

    for line in text.strip().splitlines():

        match = re.match(r"^(\S+):\s*(.+?)\s*-\s*(\S+)$", line.strip())

        if not match:
            continue

        key, principal, rights = match.groups()

        weak.setdefault(key, []).append(f"{principal} ({rights})")

    return weak


def _parse_autorun(text):

    findings = []

    for block in _blocks(text):

        fields = {}
        weak_acls = []

        for line in block.splitlines():

            line = line.strip()

            if line.startswith("NAME:"):
                fields["name"] = line.split("NAME:", 1)[1].strip()
            elif line.startswith("COMMAND:"):
                fields["command"] = line.split("COMMAND:", 1)[1].strip()
            elif line.startswith("LOCATION:"):
                fields["location"] = line.split("LOCATION:", 1)[1].strip()
            elif line.startswith("USER:"):
                fields["user"] = line.split("USER:", 1)[1].strip()
            elif line.startswith("WEAK ACL:"):
                weak_acls.append(line.split("WEAK ACL:", 1)[1].strip())

        #
        # The PS-side filter only matches on group name (Everyone/BUILTIN
        # Users/Authenticated Users appearing anywhere), same as the icacls
        # binary check — read+execute-only grants (the common case) aren't
        # actually exploitable. Require real write rights here too.
        #
        writable = [g for g in weak_acls if _icacls_has_write(g)]

        if writable:
            fields["weak_acls"] = writable
            findings.append(fields)

    return findings


def _parse_npcap(text):

    if "NPCAP_NOT_INSTALLED" in text:
        return None

    match = re.search(r"AdminOnly=(\S+)", text)

    if not match:
        return "unknown"

    if match.group(1) == "0":
        return "unrestricted"

    if match.group(1) == "1":
        return "restricted"

    #
    # "unset" (value never written) or anything else unexpected - older
    # Npcap versions predate this option entirely, so absence isn't
    # confidently one state or the other.
    #
    return "unknown"


def _unquoted_paths(services):

    results = []

    for name, fields in services.items():

        path = fields.get("PathName", "")

        if not path or path.startswith('"'):
            continue

        if " " not in path:
            continue

        #
        # Built-in Windows binaries under C:\Windows\ are protected by
        # default ACLs — HTB's own filter excludes these too, since they
        # aren't realistically exploitable this way.
        #
        if re.match(r"^[A-Za-z]:\\Windows\\", path, re.I):
            continue

        results.append({"service": name, "path": path, "startmode": fields.get("StartMode", "")})

    return results


# ==========================================
# REPORT
# ==========================================

def _render_report(weak_binaries, weak_service_acl, weak_registry, weak_autorun, unquoted, services):

    elements = []

    if weak_binaries:

        elements.append(Text.from_markup("[bold cyan]Modifiable service binaries[/bold cyan]"))

        table = Table(box=None, show_header=False, pad_edge=False, padding=(0, 2, 0, 0))
        table.add_column(style="bold white")
        table.add_column(style="white")

        for wb in weak_binaries:
            info = services.get(wb["service"], {})
            table.add_row(wb["service"], f'{wb["path"]}  (runs as {info.get("StartName", "?")})')

        elements.append(table)
        elements.append(Text(""))

    if weak_service_acl:

        elements.append(Text.from_markup("[bold cyan]Weak service permissions[/bold cyan]"))

        table = Table(box=None, show_header=False, pad_edge=False, padding=(0, 2, 0, 0))
        table.add_column(style="bold white")
        table.add_column(style="white")

        for wa in weak_service_acl:
            table.add_row(wa["service"], ", ".join(wa["principals"]) + " have SERVICE_CHANGE_CONFIG")

        elements.append(table)
        elements.append(Text(""))

    if weak_registry:

        elements.append(Text.from_markup("[bold cyan]Permissive registry ACLs[/bold cyan]"))

        table = Table(box=None, show_header=False, pad_edge=False, padding=(0, 2, 0, 0))
        table.add_column(style="bold white")
        table.add_column(style="white")

        for key, grants in weak_registry.items():
            table.add_row(key, ", ".join(grants))

        elements.append(table)
        elements.append(Text(""))

    if weak_autorun:

        elements.append(Text.from_markup("[bold cyan]Modifiable autorun binaries[/bold cyan]"))

        table = Table(box=None, show_header=False, pad_edge=False, padding=(0, 2, 0, 0))
        table.add_column(style="bold white")
        table.add_column(style="white")

        for au in weak_autorun:
            table.add_row(au.get("name", "?"), f'{au.get("command", "")}  (user: {au.get("user", "?")})')

        elements.append(table)
        elements.append(Text(""))

    if unquoted:

        elements.append(Text.from_markup("[bold cyan]Unquoted service paths[/bold cyan]"))

        table = Table(box=None, show_header=False, pad_edge=False, padding=(0, 2, 0, 0))
        table.add_column(style="bold white")
        table.add_column(style="white")

        for uq in unquoted:
            table.add_row(uq["service"], uq["path"])

        elements.append(table)

    if not elements:
        elements.append(Text("No weak permissions found.", style="dim"))

    return Group(*elements)


# ==========================================
# PUBLIC API
# ==========================================

def analyze(section):

    services = _parse_services(
        _get_command_output(section, "enumerate all services (name, display name, state, start mode, run-as account, binary path)")
    )
    weak_binaries = _parse_weak_binaries(
        _get_command_output(section, "check each service binary for weak file-system ACLs (icacls)")
    )
    weak_service_acl = _parse_weak_service_acl(
        _get_command_output(section, "check each service's own ACL for weak SERVICE_CHANGE_CONFIG grants (sc.exe sdshow)")
    )
    weak_registry = _parse_weak_registry(
        _get_command_output(section, "check registry ACLs under HKLM\\SYSTEM\\CurrentControlSet\\Services for weak grants")
    )
    weak_autorun = _parse_autorun(
        _get_command_output(section, "enumerate autorun entries and check their binaries for weak ACLs")
    )
    unquoted = _unquoted_paths(services)
    npcap = _parse_npcap(
        _get_command_output(section, "check Npcap driver access restriction (unprivileged traffic capture)")
    )

    findings = []

    for wb in weak_binaries:

        info = services.get(wb["service"], {})

        recommendation = [
            f'Backup then overwrite {wb["path"]} with a malicious payload (reverse shell, or a one-liner that adds you to local admins)',
            f'(Re)start the service to trigger it: sc.exe start {wb["service"]} — runs as {info.get("StartName", "unknown account")}',
            f'Run: ctf privesc.windows.weakperms.binary {wb["service"]} "{wb["path"]}"',
        ]

        findings.append({
            "priority": "HIGH",
            "module": "WEAKPERMS",
            "title": f'Modifiable service binary: {wb["service"]}',
            "reason": f'{", ".join(wb["grants"])} — a low-privilege group can overwrite this binary outright, and the service runs as {info.get("StartName", "unknown")}.',
            "recommendation": recommendation,
        })

    for wa in weak_service_acl:

        recommendation = [
            f'{", ".join(wa["principals"])} can reconfigure this service directly — no file write needed',
            f'sc.exe config {wa["service"]} binpath= "cmd /c net localgroup administrators <user> /add", then sc.exe stop {wa["service"]} && sc.exe start {wa["service"]}',
            f'Run: ctf privesc.windows.weakperms.service {wa["service"]}',
        ]

        findings.append({
            "priority": "HIGH",
            "module": "WEAKPERMS",
            "title": f'Weak service permissions: {wa["service"]}',
            "reason": f'SERVICE_CHANGE_CONFIG granted to {", ".join(wa["principals"])} — full binPath hijack, no file ACL involved at all.',
            "recommendation": recommendation,
        })

    for key, grants in weak_registry.items():

        recommendation = [
            f'Set-ItemProperty -Path HKLM:\\SYSTEM\\CurrentControlSet\\Services\\{key} -Name ImagePath -Value "<payload>"',
            f'(Re)start the service to trigger it: sc.exe start {key}',
            "Run: ctf privesc.windows.weakperms.registry",
        ]

        findings.append({
            "priority": "HIGH",
            "module": "WEAKPERMS",
            "title": f'Permissive registry ACL: {key}',
            "reason": f'{", ".join(grants)} on the service\'s registry key — ImagePath is writable, same end result as a binPath hijack.',
            "recommendation": recommendation,
        })

    for au in weak_autorun:

        recommendation = [
            f'Overwrite the binary — it runs as whichever user next triggers this autorun entry ({au.get("user", "unknown")})',
            "If USER is Public (HKLM Run), it fires for the next user to log in at all, not just you — could be an admin",
            "Run: ctf privesc.windows.weakperms.autorun",
        ]

        findings.append({
            "priority": "MEDIUM",
            "module": "WEAKPERMS",
            "title": f'Modifiable autorun binary: {au.get("name", "?")}',
            "reason": f'{", ".join(au["weak_acls"])} — {au.get("command", "")}',
            "recommendation": recommendation,
        })

    for uq in unquoted:

        findings.append({
            "priority": "LOW",
            "module": "WEAKPERMS",
            "title": f'Unquoted service path: {uq["service"]}',
            "reason": f'{uq["path"]} is unquoted and contains spaces — Windows will probe C:\\Program.exe etc. before reaching the real target.',
            "recommendation": [
                "Rarely exploitable in practice — planting a file at drive root or in Program Files usually needs admin already",
                "Worth noting for a writeup, but don't expect a privesc path from this alone",
            ],
        })

    if npcap == "unrestricted":

        findings.append({
            "priority": "MEDIUM",
            "module": "WEAKPERMS",
            "title": "Npcap driver accessible to non-admin users (unprivileged packet capture)",
            "reason": "Npcap is installed with AdminOnly=0 (or never restricted) — any authenticated user can open the capture device, no admin/UAC prompt needed, same as not requiring root to sniff on Linux.",
            "recommendation": [
                "Capture for a while (Wireshark, dumpcap, or tcpdump-for-Windows if present) and watch for another user's session",
                "Look specifically for cleartext auth crossing the wire — FTP, HTTP Basic, Telnet, SMTP/POP3/IMAP without TLS",
            ],
        })

    elif npcap == "unknown":

        findings.append({
            "priority": "LOW",
            "module": "WEAKPERMS",
            "title": "Npcap installed — access restriction could not be determined",
            "reason": "Npcap is present but the AdminOnly value wasn't in the expected shape — likely an older Npcap version predating this setting.",
            "recommendation": [
                "Try actually capturing as the current (low-priv) user to confirm one way or the other",
            ],
        })

    findings.sort(key=lambda f: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[f["priority"]])

    return {

        "module": "WEAKPERMS",

        "summary": {

            "Npcap Capture": {"unrestricted": "Unrestricted", "restricted": "Restricted", "unknown": "Unknown"}.get(npcap, "Not installed"),
            "Modifiable Binaries": len(weak_binaries),
            "Weak Service ACLs": len(weak_service_acl),
            "Weak Registry ACLs": len(weak_registry),
            "Modifiable Autorun": len(weak_autorun),
            "Unquoted Paths": len(unquoted),

        },

        "findings": findings,

        "report": _render_report(weak_binaries, weak_service_acl, weak_registry, weak_autorun, unquoted, services),

        "details": {

            "services": services,
            "weak_binaries": weak_binaries,
            "weak_service_acl": weak_service_acl,
            "weak_registry": weak_registry,
            "weak_autorun": weak_autorun,
            "unquoted": unquoted,

        },

    }
