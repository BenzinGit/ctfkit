"""
CTFKit - Windows PrivEsc
UAC Analyzer
"""

import re

from rich.console import Group
from rich.table import Table
from rich.text import Text


SECTION = "UAC"


# ==========================================
# KNOWLEDGE BASE
# ==========================================

#
# ConsentPromptBehaviorAdmin — documented registry values under
# Policies\System. 5 is the DEFAULT out-of-box slider position, not the
# top one — it only prompts for non-Windows binaries, which is exactly
# why Windows-signed auto-elevating binaries (fodhelper.exe, sdclt.exe,
# eventvwr.exe, computerdefaults.exe, SystemPropertiesAdvanced.exe, ...)
# still silently elevate and why most UACMe techniques target them.
# 2 is the true top "Always notify" position — it removes that silent
# path entirely by prompting even for Windows binaries.
#
CONSENT_PROMPT = {
    0: ("Elevate without prompting", "Silent elevation for any admin action — trivial, no bypass technique even needed."),
    1: ("Prompt for credentials on the secure desktop", "Even Windows-signed binaries prompt — auto-elevate bypasses won't work, look elsewhere (AlwaysInstallElevated, scheduled tasks, COM)."),
    2: ("Prompt for consent on the secure desktop (\"Always notify\", the true top slider position)", "Even Windows-signed binaries prompt — auto-elevate bypasses won't work, look elsewhere (AlwaysInstallElevated, scheduled tasks, COM)."),
    3: ("Prompt for credentials", "Not on the secure desktop, but still prompts — auto-elevate bypasses less likely to help."),
    4: ("Prompt for consent", "Not on the secure desktop, but still prompts — auto-elevate bypasses less likely to help."),
    5: ("Prompt for consent for non-Windows binaries (default)", "Windows-signed auto-elevating binaries still elevate silently — this is what almost every UACMe technique relies on."),
}


# ==========================================
# HELPERS
# ==========================================

def _get_command_output(section, command):
    #
    # No leading \n in the lookahead: if a command's output is genuinely
    # empty, the marker's trailing blank line and the next marker's
    # boundary collapse into one \n\n, leaving nothing for a \n-prefixed
    # lookahead to match — it would swallow the whole next section instead.
    # See modules/privesc/windows/analyzers/weakperms.py for where this bit.
    #
    pattern = rf">>> COMMAND: {re.escape(command)}\n\n(.*?)(?=>>> COMMAND:|\Z)"
    match = re.search(pattern, section, re.S)
    return match.group(1).strip() if match else ""


def _parse_reg_dwords(text):

    values = {}

    for match in re.finditer(r"^\s*(\w+)\s+REG_DWORD\s+0x([0-9a-fA-F]+)", text, re.M):
        values[match.group(1)] = int(match.group(2), 16)

    return values


def _parse_integrity(section):

    match = re.search(r"Mandatory Label\\(\w+) Mandatory Level", section)

    return match.group(1) if match else None


def _is_admin(section):
    return bool(re.search(r"^Group Name:\s*BUILTIN\\Administrators\s*$", section, re.M))


def _parse_build(section):

    for line in section.splitlines():

        line = line.strip()
        match = re.match(r"^\d+\.\d+\.(\d+)(?:\.\d+)?$", line)

        if match:
            return int(match.group(1))

    return None


def _writable_path_entries(section):

    path_text = _get_command_output(section, "cmd /c echo %PATH%")

    entries = [p.strip() for p in path_text.replace("\n", "").split(";") if p.strip()]

    return [p for p in entries if re.match(r"^[A-Za-z]:\\Users\\", p)]


# ==========================================
# REPORT
# ==========================================

def _render_report(is_admin, integrity, enable_lua, consent_admin, filter_admin_token, build, writable_paths):

    table = Table(box=None, show_header=False, pad_edge=False, padding=(0, 2, 0, 0))
    table.add_column(style="bold cyan")
    table.add_column(style="white")

    table.add_row("Local Administrator", "Yes" if is_admin else "No")
    table.add_row("Integrity Level", integrity or "Unknown")
    table.add_row("EnableLUA", "Enabled" if enable_lua else "Disabled" if enable_lua is not None else "Unknown")

    if consent_admin is not None:
        label = CONSENT_PROMPT.get(consent_admin, ("Unrecognized value", ""))[0]
        table.add_row("ConsentPromptBehaviorAdmin", f"{consent_admin} — {label}")

    table.add_row(
        "FilterAdministratorToken",
        "Enabled — RID-500 Administrator is also filtered" if filter_admin_token else "Disabled (default) — RID-500 Administrator exempt from filtering",
    )

    table.add_row("OS Build", str(build) if build else "Unknown")

    elements = [table]

    if writable_paths:

        elements.append(Text(""))
        elements.append(Text.from_markup("[bold cyan]User-writable PATH entries[/bold cyan]"))

        for p in writable_paths:
            elements.append(Text.from_markup(f"  {p}"))

    return Group(*elements)


# ==========================================
# PUBLIC API
# ==========================================

def analyze(section):

    is_admin = _is_admin(section)
    integrity = _parse_integrity(section)
    build = _parse_build(section)
    writable_paths = _writable_path_entries(section)

    reg_values = _parse_reg_dwords(_get_command_output(section, 'reg query "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"'))

    enable_lua = bool(reg_values["EnableLUA"]) if "EnableLUA" in reg_values else None
    consent_admin = reg_values.get("ConsentPromptBehaviorAdmin")
    filter_admin_token = bool(reg_values.get("FilterAdministratorToken", 0))

    findings = []

    #
    # Only relevant if we're both a local admin AND currently running with
    # a filtered (Medium) token — otherwise there's nothing to bypass.
    #
    if is_admin and integrity == "Medium" and enable_lua:

        reason = (
            "You're a member of Administrators but running at Medium integrity — UAC is filtering your "
            "token. Bypassing it gets a full admin (High integrity) token without a fresh elevated logon."
        )

        recommendation = []

        if consent_admin is not None:
            _, note = CONSENT_PROMPT.get(consent_admin, ("", "Unrecognized ConsentPromptBehaviorAdmin value — check manually."))
            recommendation.append(note)

        recommendation.append(
            f"Match the OS build ({build or 'unknown, see report'}) against UACMe's technique list "
            "and run the matching one — it catalogs and maintains dozens against current builds"
        )

        if writable_paths:
            recommendation.append(
                f"Also: {len(writable_paths)} user-writable PATH entry(ies) found (e.g. WindowsApps) — "
                "a DLL search-order hijack against an auto-elevating binary is viable here too, see report"
            )

        recommendation.append("Run: ctf privesc.windows.privileges.uac")

        findings.append({

            "priority": "HIGH",
            "module": "UAC",
            "title": "Admin token filtered by UAC (Medium integrity)",
            "reason": reason,
            "recommendation": recommendation,

        })

    return {

        "module": "UAC",

        "summary": {

            "Local Admin": "Yes" if is_admin else "No",
            "Integrity": integrity or "Unknown",
            "Bypass Relevant": "Yes" if findings else "No",

        },

        "findings": findings,

        "report": _render_report(is_admin, integrity, enable_lua, consent_admin, filter_admin_token, build, writable_paths),

        "details": {

            "is_admin": is_admin,
            "integrity": integrity,
            "enable_lua": enable_lua,
            "consent_admin": consent_admin,
            "filter_admin_token": filter_admin_token,
            "build": build,
            "writable_paths": writable_paths,

        }

    }
