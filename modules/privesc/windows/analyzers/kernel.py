"""
CTFKit - Windows PrivEsc
Kernel Exploits Analyzer
"""

import re
from datetime import datetime, timezone

from rich.console import Group
from rich.table import Table
from rich.text import Text


SECTION = "KERNEL"

#
# Known patch-release date for the actual PrintNightmare RCE code fix
# (the July 2021 out-of-band update, KB5004945+) — used as an independent
# vulnerability signal when the newest installed patch predates it,
# regardless of the Point & Print workaround's registry state.
#
PRINTNIGHTMARE_PATCH_DATE = datetime(2021, 7, 6)

#
# MS17-010 / EternalBlue — fixed in the March 14, 2017 Patch Tuesday for
# every OS still realistically in scope today (7, 8.1, 10, 2008 R2, 2012,
# 2012 R2, 2016). Unlike the giant historical MS-XX-XXX table, this is a
# single frozen date for one named CVE — it never grows, so it doesn't
# have the "goes stale immediately" problem a broader table would.
#
MS17_010_PATCH_DATE = datetime(2017, 3, 14)

#
# CVE-2020-0668 — Windows Kernel arbitrary file move via Service Tracing,
# fixed in the February 2020 Patch Tuesday.
#
CVE_2020_0668_PATCH_DATE = datetime(2020, 2, 11)


# ==========================================
# HELPERS
# ==========================================

def _get_command_output(section, command):
    #
    # See modules/privesc/windows/analyzers/weakperms.py for why the
    # lookahead has no leading \n — genuinely empty command output would
    # otherwise swallow the entire next section.
    #
    pattern = rf">>> COMMAND: {re.escape(command)}\n\n(.*?)(?=>>> COMMAND:|\Z)"
    match = re.search(pattern, section, re.S)
    return match.group(1).strip() if match else ""


def _blocks(text):
    return [b for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]


def _parse_hotfixes(text):

    hotfixes = []

    for block in _blocks(text):

        fields = {}

        for line in block.splitlines():

            match = re.match(r"^(\w+)\s*:\s*(.*)$", line.strip())

            if match:
                fields[match.group(1)] = match.group(2).strip()

        if fields.get("HotFixID"):
            hotfixes.append(fields)

    return hotfixes


def _latest_hotfix_date(hotfixes):

    latest = None

    for hf in hotfixes:

        raw = hf.get("InstalledOn", "")

        for fmt in ("%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y", "%d/%m/%Y"):

            try:
                dt = datetime.strptime(raw, fmt)
            except ValueError:
                continue

            if latest is None or dt > latest:
                latest = dt

            break

    return latest


def _parse_os_version(text):

    match = re.search(r"NT (\d+)\.(\d+)\.(\d+)", text)

    if not match:
        return None, None, None

    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def _parse_smb1(text):

    match = re.search(r"^SMB1\s*:\s*(\d+)", text, re.M)

    return int(match.group(1)) if match else None


def _icacls_grants_read(line):

    for token in re.findall(r"\(([^)]*)\)", line):

        parts = [p.strip() for p in token.split(",")]

        if any(p in ("F", "M", "W", "R", "RX") for p in parts):
            return True

    return False


def _sam_acl_weak(text):

    for line in text.splitlines():

        if re.search(r"Everyone|BUILTIN\\Users|Authenticated Users", line) and _icacls_grants_read(line):
            return True

    return False


def _parse_shadow_copies(text):
    return [int(n) for n in re.findall(r"FOUND: HarddiskVolumeShadowCopy(\d+)", text)]


def _parse_spooler_status(text):

    match = re.search(r"^Status\s*:\s*(\w+)", text, re.M)

    return match.group(1) if match else None


def _parse_reg_dwords(text):

    values = {}

    for match in re.finditer(r"^\s*(\w+)\s+REG_DWORD\s+0x([0-9a-fA-F]+)", text, re.M):
        values[match.group(1)] = int(match.group(2), 16)

    return values


# ==========================================
# REPORT
# ==========================================

def _render_report(hotfixes, latest_date, os_major, os_minor, os_build, smb1, sam_weak, shadow_copies, spooler_status, reg_values):

    table = Table(box=None, show_header=False, pad_edge=False, padding=(0, 2, 0, 0))
    table.add_column(style="bold cyan")
    table.add_column(style="white")

    os_str = f"NT {os_major}.{os_minor}.{os_build}" if os_major is not None else "Unknown"

    table.add_row("OS Version", os_str)
    table.add_row("Hotfixes Found", str(len(hotfixes)))
    table.add_row("Most Recent Patch", latest_date.strftime("%Y-%m-%d") if latest_date else "Unknown")
    table.add_row("SMB1 Enabled", "Yes" if smb1 == 1 else "No" if smb1 == 0 else "Unknown (not set)")
    table.add_row("SAM Readable by Low-Priv Group", "Yes" if sam_weak else "No")
    table.add_row("Accessible Shadow Copies", str(len(shadow_copies)) if shadow_copies else "0")
    table.add_row("Spooler Service", spooler_status or "Unknown")

    if reg_values:
        table.add_row("PointAndPrint NoWarningNoElevationOnInstall", str(reg_values.get("NoWarningNoElevationOnInstall", "Not set")))
        table.add_row("PointAndPrint UpdatePromptSettings", str(reg_values.get("UpdatePromptSettings", "Not set")))

    elements = [table]

    if hotfixes:

        elements.append(Text(""))
        elements.append(Text.from_markup("[bold cyan]Installed hotfixes (most recent last)[/bold cyan]"))

        hf_table = Table(box=None, show_header=False, pad_edge=False, padding=(0, 2, 0, 0))
        hf_table.add_column(style="white")
        hf_table.add_column(style="dim")

        for hf in hotfixes[-15:]:
            hf_table.add_row(hf.get("HotFixID", "?"), hf.get("InstalledOn", "?"))

        elements.append(hf_table)

    return Group(*elements)


# ==========================================
# PUBLIC API
# ==========================================

def analyze(section):

    hotfixes = _parse_hotfixes(
        _get_command_output(section, "list installed hotfixes")
    )
    latest_date = _latest_hotfix_date(hotfixes)

    os_major, os_minor, os_build = _parse_os_version(
        _get_command_output(section, "[System.Environment]::OSVersion.VersionString")
    )

    smb1 = _parse_smb1(
        _get_command_output(section, "check SMB1 protocol status")
    )

    sam_weak = _sam_acl_weak(
        _get_command_output(section, "icacls C:\\Windows\\System32\\config\\SAM")
    )

    shadow_copies = _parse_shadow_copies(
        _get_command_output(section, "check for accessible shadow copies (HiveNightmare)")
    )

    spooler_status = _parse_spooler_status(
        _get_command_output(section, "check Print Spooler service status")
    )

    reg_values = _parse_reg_dwords(
        _get_command_output(section, "check Point and Print registry policy")
    )

    findings = []

    #
    # Always surfaced, regardless of whether we can pin a specific CVE —
    # patch level is worth a human (or Watson/Sherlock) look either way.
    # HIGH if the OS predates Windows 10/Server 2016, or if the newest
    # installed patch is over a year old; MEDIUM otherwise as a nudge.
    #
    very_old_os = os_major is not None and os_major < 10
    stale_patches = latest_date is not None and (datetime.now() - latest_date).days > 365

    priority = "HIGH" if (very_old_os or stale_patches) else "MEDIUM"

    reason_bits = [f"Running NT {os_major}.{os_minor}.{os_build}." if os_major is not None else "Could not determine OS build."]

    if very_old_os:
        reason_bits.append("This major version predates Windows 10/Server 2016 — almost certainly past its support lifecycle.")

    if latest_date:
        reason_bits.append(f"Most recent installed patch is from {latest_date.strftime('%Y-%m-%d')}" + (" — over a year old." if stale_patches else "."))
    else:
        reason_bits.append("No hotfix install dates could be parsed — verify patch level manually.")

    findings.append({
        "priority": priority,
        "module": "KERNEL",
        "title": "OS build / patch level — cross-reference for known LPE/RCE vulnerabilities",
        "reason": " ".join(reason_bits),
        "recommendation": [
            f"{len(hotfixes)} hotfix(es) enumerated — see report for the full list",
            "Cross-reference the build and installed KBs against Watson, Sherlock, or the Windows kernel-exploit CVE table — we don't maintain that mapping locally since it goes stale immediately",
        ],
    })

    #
    # HiveNightmare / CVE-2021-36934 — locally confirmable: SAM readable by
    # a low-privilege group, and at least one shadow copy exposes a second
    # (unrestricted) copy of it.
    #
    if sam_weak and shadow_copies:

        findings.append({
            "priority": "HIGH",
            "module": "KERNEL",
            "title": "HiveNightmare / SeriousSam (CVE-2021-36934)",
            "reason": f"SAM is readable by a low-privilege group, and {len(shadow_copies)} volume shadow copy(ies) expose an unrestricted second copy of it — full SAM/SYSTEM/SECURITY hive dump without admin rights.",
            "recommendation": [
                "Dump the hives via HiveNightmare.exe and crack offline with secretsdump",
                "Run: ctf privesc.windows.kernel.hivenightmare",
            ],
        })

    elif sam_weak:

        #
        # ACL half of the bug is confirmed, but the second precondition
        # (an accessible shadow copy) isn't right now — surface this
        # instead of going silent, since "half exploitable" is a very
        # different fact from "not exploitable" and shadow copies get
        # created periodically (System Protection), so it's worth
        # rechecking rather than writing the box off.
        #
        findings.append({
            "priority": "LOW",
            "module": "KERNEL",
            "title": "SAM readable by low-privilege group (HiveNightmare precondition, no shadow copy yet)",
            "reason": "The ACL misconfiguration behind CVE-2021-36934 is present, but no accessible volume shadow copy was found — HiveNightmare needs both. This can change as System Protection creates new restore points.",
            "recommendation": [
                "Recheck periodically, or trigger a restore point yourself if you have the rights to do so",
                "Confirm independently with the real HiveNightmare.exe PoC if you want certainty beyond this probe",
            ],
        })

    #
    # PrintNightmare / CVE-2021-1675 & CVE-2021-34527 — Spooler running is
    # the hard precondition. Beyond that there are two independent signals,
    # either is sufficient: (a) Point & Print explicitly misconfigured to
    # skip the warning/elevation prompt — HTB's own guidance says 0/undefined
    # is the safe state, so an explicit permissive value is real signal; or
    # (b) the newest installed patch predates the July 2021 out-of-band fix
    # (KB5004945+), in which case the registry workaround is irrelevant —
    # the underlying RCE is almost certainly still there regardless of it.
    #
    if spooler_status == "Running":

        no_warning = reg_values.get("NoWarningNoElevationOnInstall", 0)
        update_prompt = reg_values.get("UpdatePromptSettings", 0)

        workaround_misconfigured = no_warning == 1 or update_prompt in (1, 2)
        patch_missing = latest_date is not None and latest_date < PRINTNIGHTMARE_PATCH_DATE

        if workaround_misconfigured or patch_missing:

            if workaround_misconfigured:
                reason = "Print Spooler is running and Point & Print restrictions are explicitly set to skip the warning/elevation prompt for driver installs."
            else:
                reason = (
                    f"Print Spooler is running and the most recent installed patch ({latest_date:%Y-%m-%d}) predates "
                    "the July 2021 out-of-band fix (KB5004945+) — the underlying RCE is almost certainly still present, "
                    "independent of the Point & Print registry state."
                )

            findings.append({
                "priority": "HIGH",
                "module": "KERNEL",
                "title": "PrintNightmare (CVE-2021-1675 / CVE-2021-34527)",
                "reason": reason,
                "recommendation": [
                    "Use a known PoC (e.g. the PowerShell Invoke-Nightmare or cube0x0's implementation) to add a local admin or load a payload DLL",
                    "Run: ctf privesc.windows.kernel.printnightmare",
                ],
            })

    #
    # MS17-010 / EternalBlue — SMB1 explicitly enabled is the hard
    # precondition (the vulnerable driver isn't even reachable without
    # it). Compound with the patch date for a real HIGH-confidence call;
    # SMB1-on-alone with no confirmable patch date drops to MEDIUM.
    #
    if smb1 == 1:

        if latest_date is not None and latest_date < MS17_010_PATCH_DATE:

            findings.append({
                "priority": "HIGH",
                "module": "KERNEL",
                "title": "MS17-010 / EternalBlue",
                "reason": f"SMB1 is explicitly enabled and the most recent installed patch ({latest_date:%Y-%m-%d}) predates the March 2017 MS17-010 fix — this build is almost certainly vulnerable.",
                "recommendation": [
                    "If port 445 isn't reachable externally, port-forward it back to your attack box",
                    "Use a known MS17-010 exploit — standalone or Metasploit's exploit/windows/smb/ms17_010_eternalblue/psexec — for a SYSTEM shell",
                    "Run: ctf privesc.windows.kernel.eternalblue",
                ],
            })

        else:

            findings.append({
                "priority": "MEDIUM",
                "module": "KERNEL",
                "title": "SMB1 protocol enabled",
                "reason": "SMBv1 is explicitly enabled — a precondition for MS17-010/EternalBlue and other legacy SMB RCE flaws, though the patch date doesn't confirm it's missing.",
                "recommendation": [
                    "If port 445 isn't reachable externally, port-forward it back to your attack box and check with a known MS17-010 detection script",
                    "A public MS17-010 exploit (standalone or Metasploit's exploit/windows/smb/ms17_010_eternalblue) can be used if the target is confirmed unpatched",
                ],
            })

    #
    # CVE-2020-0668 — Service Tracing arbitrary file move. Only a
    # patch-date signal, deliberately kept at MEDIUM: actual exploitation
    # needs an external compiled tool, a suitable third-party SYSTEM
    # service to chain into (see the WEAKPERMS section for candidates —
    # even an (RX)-only one qualifies, this primitive doesn't care about
    # the target's current ACL), and a working DLL-hijack follow-up
    # (UsoDllLoader/DiagHub) that HTB's own material admits isn't reliable.
    #
    if latest_date is not None and latest_date < CVE_2020_0668_PATCH_DATE:

        findings.append({
            "priority": "MEDIUM",
            "module": "KERNEL",
            "title": "CVE-2020-0668 — Service Tracing arbitrary file move",
            "reason": f"Most recent installed patch ({latest_date:%Y-%m-%d}) predates the February 2020 fix — the arbitrary file-move primitive is likely still present, though exploitation needs more than just this.",
            "recommendation": [
                "Needs the external CVE-2020-0668.exe PoC (build from source) — this isn't a self-contained scripted technique",
                "Chain it into a third-party LocalSystem service binary outside C:\\Windows\\ (see WEAKPERMS section for candidates) — WFP-protected system binaries can't be targeted this way",
                "The DLL-hijack follow-up (UsoDllLoader/DiagHub) isn't always available — treat this as worth trying, not guaranteed",
            ],
        })

    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    findings.sort(key=lambda f: priority_order[f["priority"]])

    return {

        "module": "KERNEL",

        "summary": {

            "OS Version": f"NT {os_major}.{os_minor}.{os_build}" if os_major is not None else "Unknown",
            "Hotfixes": len(hotfixes),
            "HiveNightmare": "Yes" if (sam_weak and shadow_copies) else "No",
            "PrintNightmare": "Yes" if findings and any(f["title"].startswith("PrintNightmare") for f in findings) else "No",
            "MS17-010": "Yes" if findings and any(f["title"] == "MS17-010 / EternalBlue" for f in findings) else "No",

        },

        "findings": findings,

        "report": _render_report(hotfixes, latest_date, os_major, os_minor, os_build, smb1, sam_weak, shadow_copies, spooler_status, reg_values),

        "details": {

            "hotfixes": hotfixes,
            "latest_date": latest_date,
            "os_version": (os_major, os_minor, os_build),
            "smb1": smb1,
            "sam_weak": sam_weak,
            "shadow_copies": shadow_copies,
            "spooler_status": spooler_status,
            "reg_values": reg_values,

        },

    }
