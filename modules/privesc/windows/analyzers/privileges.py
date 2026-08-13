"""
CTFKit - Windows PrivEsc
Token Privileges Analyzer
"""

import re


SECTION = "PRIVILEGES"


# ==========================================
# KNOWLEDGE BASE
# ==========================================

PRIVILEGES = {

    "SeImpersonatePrivilege": {
        "priority": "HIGH",
        "reason": "Can impersonate a client token — a SYSTEM-triggered connection can be coerced into handing over a SYSTEM token (\"Potato\" family).",
        "recommendation": [
            "PrintSpoofer / RoguePotato on Win10 1809+ / Server 2019+ (JuicyPotato is patched there)",
            "JuicyPotato on older builds (pre Win10 1809 / Server 2019)",
        ]
    },

    "SeAssignPrimaryTokenPrivilege": {
        "priority": "HIGH",
        "reason": "Can assign a primary token to a new process via CreateProcessAsUser — same Potato-family abuse path as SeImpersonate.",
        "recommendation": [
            "JuicyPotato (CreateProcessAsUser path) on older builds",
            "RoguePotato on Win10 1809+ / Server 2019+",
        ]
    },

    "SeDebugPrivilege": {
        "priority": "HIGH",
        "reason": "Can open a handle to any process, including SYSTEM ones — enables credential dumping or token theft.",
        "recommendation": [
            "procdump -accepteula -ma lsass.exe lsass.dmp, then parse offline with mimikatz sekurlsa::minidump",
            "Steal/inherit the token of a SYSTEM process (e.g. winlogon.exe) via a CreateProcessFromParent-style PoC",
        ]
    },

    "SeTakeOwnershipPrivilege": {
        "priority": "HIGH",
        "reason": "Grants WRITE_OWNER over any securable object — take ownership, then re-ACL it for full access.",
        "recommendation": [
            "takeown /f <path>",
            "icacls <path> /grant <user>:F",
        ]
    },

    "SeBackupPrivilege": {
        "priority": "HIGH",
        "reason": "Bypasses file/registry read ACLs entirely — can read the SAM/SYSTEM hives or any protected file.",
        "recommendation": [
            "reg save HKLM\\SAM sam.hive && reg save HKLM\\SYSTEM system.hive, then extract hashes offline",
            "robocopy /b to copy files that are otherwise access-denied",
        ]
    },

    "SeRestorePrivilege": {
        "priority": "HIGH",
        "reason": "Bypasses file/registry write ACLs entirely — can overwrite any file, including service binaries.",
        "recommendation": [
            "Overwrite a SYSTEM-run service binary or DLL, then restart the service",
            "Replace utilman.exe/sethc.exe for a SYSTEM shell at the logon screen",
        ]
    },

    "SeLoadDriverPrivilege": {
        "priority": "HIGH",
        "reason": "Can load a kernel-mode driver — including a vulnerable signed driver for a bring-your-own-vulnerable-driver LPE.",
        "recommendation": [
            "Load a known-vulnerable signed driver (e.g. Capcom.sys) and exploit it for SYSTEM",
        ]
    },

    "SeTcbPrivilege": {
        "priority": "HIGH",
        "reason": "\"Act as part of the operating system\" — one of the most powerful privileges, can create/forge arbitrary tokens.",
        "recommendation": [
            "Rare to see outside of service accounts — review what granted it, likely allows direct SYSTEM token creation",
        ]
    },

    "SeCreateTokenPrivilege": {
        "priority": "HIGH",
        "reason": "Can create arbitrary tokens, including ones with SYSTEM privileges.",
        "recommendation": [
            "Craft a token with elevated privileges and apply it to the current process",
        ]
    },

    "SeManageVolumePrivilege": {
        "priority": "MEDIUM",
        "reason": "Raw volume access — mainly useful combined with SeBackup/SeRestore for ACL-bypassing disk tricks.",
        "recommendation": [
            "Review in combination with SeBackup/SeRestore for raw disk read/write primitives",
        ]
    },

    "SeCreateSymbolicLinkPrivilege": {
        "priority": "MEDIUM",
        "reason": "Can create symbolic links — useful for object-manager symlink/junction privesc primitives.",
        "recommendation": [
            "Consider symlink attacks against a service/task that writes to a predictable path",
        ]
    },

}

#
# Privileges handled by the Potato-family follow-up module
#
POTATO_PRIVILEGES = {
    "SeImpersonatePrivilege",
    "SeAssignPrimaryTokenPrivilege",
}


# ==========================================
# PARSER
# ==========================================

def _parse(section):

    enabled = []
    disabled = []

    for line in section.splitlines():

        line = line.strip()

        if not line or line.startswith(">>>"):
            continue

        match = re.match(r"^(Se[A-Za-z]+Privilege)\s+.+?\s+(Enabled|Disabled)\s*$", line)

        if not match:
            continue

        name, state = match.groups()

        if state == "Enabled":
            enabled.append(name)
        else:
            disabled.append(name)

    return enabled, disabled


def _parse_build(section):

    #
    # [System.Environment]::OSVersion.Version -> "10.0.17763.0"
    #
    for line in section.splitlines():

        line = line.strip()

        match = re.match(r"^\d+\.\d+\.(\d+)(?:\.\d+)?$", line)

        if match:
            return int(match.group(1))

    return None


# ==========================================
# REPORT
# ==========================================

def _render_report(enabled, disabled, detected):

    report = []

    if enabled:

        report.append("Enabled Privileges")
        report.append("-" * 19)

        for name in enabled:

            if name in detected:
                report.append(f"{name}  [{PRIVILEGES[name]['priority']}]")
            else:
                report.append(name)

        report.append("")

    if disabled:

        report.append("Disabled Privileges")
        report.append("-" * 20)
        report.append(", ".join(disabled))

    return "\n".join(report)


# ==========================================
# PUBLIC API
# ==========================================

def analyze(section):

    enabled, disabled = _parse(section)
    build = _parse_build(section)

    findings = []

    detected = []

    for name in enabled:

        if name not in PRIVILEGES:
            continue

        info = PRIVILEGES[name]

        detected.append(name)

        recommendation = list(info["recommendation"])

        if name in POTATO_PRIVILEGES:
            potato_cmd = "ctf privesc.windows.privileges.potato"
            if build:
                potato_cmd += f" {build}"
            recommendation = [f"Run: {potato_cmd}"] + recommendation

        findings.append({

            "priority": info["priority"],
            "module": "PRIVILEGES",
            "title": name,
            "reason": info["reason"],
            "recommendation": recommendation

        })

    return {

        "module": "PRIVILEGES",

        "summary": {

            "Enabled": len(enabled),
            "Abusable": len(detected),
            "OS Build": build if build else "Unknown",

        },

        "findings": findings,

        "report": _render_report(enabled, disabled, detected),

        "details": {

            "enabled": enabled,
            "disabled": disabled,
            "abusable": detected,
            "build": build,

        }

    }
