"""
CTFKit - Windows PrivEsc
DLL Hijacking Analyzer
"""

import re

from rich.console import Group
from rich.table import Table
from rich.text import Text


SECTION = "DLL HIJACKING"


# ==========================================
# HELPERS
# ==========================================

def _get_command_output(section, command):
    pattern = rf">>> COMMAND: {re.escape(command)}\n\n(.*?)(?=>>> COMMAND:|\Z)"
    match = re.search(pattern, section, re.S)
    return match.group(1).strip() if match else ""


def _blocks(text):
    return [b for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]


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


def _parse_weak_dlls(text):

    weak = []
    current = None
    grants = []

    def _flush():
        if current and any(_icacls_has_write(g) for g in grants):
            weak.append(current)

    for line in text.splitlines():

        stripped = line.strip()

        if stripped.startswith("WEAK:"):
            _flush()
            current = stripped.split("WEAK:", 1)[1].strip()
            grants = []
        elif current and stripped:
            grants.append(stripped)

    _flush()

    return weak


TRUSTED_PREFIXES = ("c:\\windows\\", "c:\\program files\\", "c:\\program files (x86)\\")


def _parse_nonstandard_modules(text):

    flagged = {}
    current_process = None

    for line in text.splitlines():

        match = re.match(r"^PROCESS: (.+) \((\d+)\)$", line.strip())

        if match:
            current_process = f"{match.group(1)} ({match.group(2)})"
            continue

        if not current_process or not line.startswith("  "):
            continue

        path = line.strip()

        #
        # Get-Process .Modules includes the process's own main executable
        # as the first entry, not just its DLLs — a non-standard-path EXE
        # is a real signal, but it's an autorun/weak-binary concern, not a
        # DLL hijack one, and it's already covered (with proper ACL
        # write-filtering) by the WEAKPERMS autorun check. Keep this
        # finding scoped to actual DLLs so it doesn't duplicate/mislabel.
        #
        if not path.lower().endswith(".dll"):
            continue

        if not path.lower().startswith(TRUSTED_PREFIXES):
            flagged.setdefault(path, set()).add(current_process)

    return flagged


# ==========================================
# ANALYSIS
# ==========================================

def analyze(section):
    """
    DLL Hijacking Analysis:
    - Check if Safe DLL Search Mode is enabled
    - Identify DLLs with weak permissions
    """

    findings = []

    # Check Safe DLL Search Mode
    safe_dll_output = _get_command_output(section, "check Safe DLL Search Mode setting")

    safe_dll_state = "Unknown"

    hex_match = re.search(r"SafeDllSearchMode\s+REG_DWORD\s+0x([0-9a-fA-F]+)", safe_dll_output)
    not_configured = "Value not found" in safe_dll_output

    if hex_match or not_configured:
        if hex_match and int(hex_match.group(1), 16) == 0:
            safe_dll_state = "Disabled"
            findings.append({
                "priority": "HIGH",
                "module": "DLL_HIJACK",
                "title": "Safe DLL Search Mode is DISABLED",
                "reason": (
                    "Safe DLL Search Mode allows DLL hijacking attacks. "
                    "With it disabled, the current directory is searched before System32, "
                    "allowing an attacker to place a malicious DLL in the application directory "
                    "to be loaded instead of the legitimate one."
                ),
                "recommendation": [
                    "Enable Safe DLL Search Mode via: "
                    "reg add 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager' /v SafeDllSearchMode /t REG_DWORD /d 1"
                ],
            })
        else:
            safe_dll_state = "Enabled"
            findings.append({
                "priority": "LOW",
                "module": "DLL_HIJACK",
                "title": "Safe DLL Search Mode is enabled",
                "reason": (
                    "Safe DLL Search Mode is enabled (default), which mitigates DLL search order hijacking "
                    "by placing the System32 directory earlier in the search path."
                ),
                "recommendation": [],
            })
    else:
        findings.append({
            "priority": "MEDIUM",
            "module": "DLL_HIJACK",
            "title": "Safe DLL Search Mode status unknown",
            "reason": (
                "Could not determine Safe DLL Search Mode setting. "
                "If not explicitly enabled, it defaults to enabled on modern Windows systems."
            ),
            "recommendation": [],
        })

    # Check for weak DLL permissions (write-level grants only, not mere Read)
    weak_dlls_output = _get_command_output(section, "check common DLL locations and their permissions")

    weak_dlls = _parse_weak_dlls(weak_dlls_output)

    if weak_dlls:
        findings.append({
            "priority": "HIGH",
            "module": "DLL_HIJACK",
            "title": f"DLLs with write-level permissions for low-priv users ({len(weak_dlls)})",
            "reason": (
                f"The following DLLs grant Write/Modify/FullControl to Everyone, Authenticated Users, "
                f"or BUILTIN\\Users: {', '.join(weak_dlls)}. An attacker with write access to these DLLs "
                "could modify them for code execution by whatever process loads them."
            ),
            "recommendation": [
                "Review and restrict file permissions on these DLLs to admin/system only.",
                "Use icacls or Set-Acl to remove write permissions for Users, Everyone, and Authenticated Users.",
            ],
        })

    # Check for processes loading DLLs from outside C:\Windows / Program Files
    modules_output = _get_command_output(section, "enumerate loaded DLLs by system processes")

    nonstandard_modules = _parse_nonstandard_modules(modules_output)

    if nonstandard_modules:

        sample = sorted(nonstandard_modules)[:15]

        findings.append({
            "priority": "MEDIUM",
            "module": "DLL_HIJACK",
            "title": f"Processes loading DLLs from non-standard paths ({len(nonstandard_modules)})",
            "reason": (
                f"{len(nonstandard_modules)} unique DLL path(s) loaded by running processes are outside "
                "C:\\Windows and Program Files. This alone doesn't mean they're hijackable — check whether "
                "the containing directory is writable by a low-privilege user — but these are the concrete "
                "candidates worth checking rather than a blind scan of system directories."
            ),
            "recommendation": [
                f"Check directory write access for each path below, e.g.: icacls \"{sample[0]}\"",
                "Cross-reference against the WEAKPERMS section for directories already flagged as writable.",
                "Sample: " + "; ".join(f"{p} (loaded by {', '.join(sorted(nonstandard_modules[p]))})" for p in sample),
            ],
        })

    return {

        "module": "DLL_HIJACK",

        "summary": {
            "Safe DLL Search Mode": safe_dll_state,
            "Weak DLL permissions": len(weak_dlls),
            "Non-standard loaded DLLs": len(nonstandard_modules),
        },

        "findings": findings,

        "report": display(findings),

    }


# ==========================================
# DISPLAY
# ==========================================

def display(findings):
    """Render DLL hijacking findings as a Rich panel."""

    if not findings:
        return None

    rows = []

    for finding in findings:

        priority_style = {
            "HIGH": "bold red",
            "MEDIUM": "bold yellow",
            "LOW": "bold cyan",
        }.get(finding["priority"], "white")

        rows.append([
            Text(finding["priority"], style=priority_style),
            Text(finding["title"], style="white"),
        ])

    table = Table(show_header=True, header_style="bold magenta", box=None, padding=(0, 1))
    table.add_column("Priority", width=10)
    table.add_column("Finding")

    for row in rows:
        table.add_row(*row)

    return Group(table)
