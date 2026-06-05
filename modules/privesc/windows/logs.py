from pathlib import Path

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
# SEARCHES
# =========================================================

SEARCHES = {

    "1": {
        "name": "Security 4688",
        "description": "Process creation events",
        "wevtutil": (
            'wevtutil qe Security /rd:true /f:text '
            '| findstr /i "/user password pass cmdkey runas net use"'
        ),
        "powershell": (
            "Get-WinEvent -LogName Security | "
            "where { $_.ID -eq 4688 }"
        ),
    },

    "2": {
        "name": "PowerShell Operational",
        "description": "PowerShell script logging",
        "wevtutil": (
            'wevtutil qe '
            '"Microsoft-Windows-PowerShell/Operational" '
            '/rd:true /f:text'
        ),
        "powershell": (
            'Get-WinEvent -LogName '
            '"Microsoft-Windows-PowerShell/Operational"'
        ),
    },

    "3": {
        "name": "Sysmon Process Create",
        "description": "Sysmon event ID 1",
        "wevtutil": (
            'wevtutil qe '
            '"Microsoft-Windows-Sysmon/Operational" '
            '/rd:true /f:text'
        ),
        "powershell": (
            'Get-WinEvent -LogName '
            '"Microsoft-Windows-Sysmon/Operational" '
            '| where { $_.ID -eq 1 }'
        ),
    },

}

# =========================================================
# HELPERS
# =========================================================

def ask_admin():

    try:

        result = input(
            f"\n{B}admin shell? [y/N]{W}> "
        ).strip().lower()

    except (KeyboardInterrupt, EOFError):

        print()

        return False

    return result == "y"


def ask_eventlog_reader():

    try:

        result = input(
            f"{B}event log readers? [y/N]{W}> "
        ).strip().lower()

    except (KeyboardInterrupt, EOFError):

        print()

        return False

    return result == "y"


def render_menu():

    print(
        f"\n{B}[*]{W} "
        f"LOG HUNTING MODULES\n"
    )

    for idx, entry in SEARCHES.items():

        connector = (
            "└──"
            if idx == str(len(SEARCHES) + 1)
            else "├──"
        )

        print(
            f"  {B}{connector}{W} "
            f"[{idx}] {entry['name']}"
        )

    print(
        f"  {B}└──{W} [4] Generic keyword hunt"
    )


def render_targets():

    print(
        f"\n{B}[*]{W} "
        f"HIGH VALUE SEARCH TERMS\n"
    )

    targets = [

        "/user",
        "password",
        "pass",
        "cmdkey",
        "runas",
        "net use",
        "backup",
        "token",
        "creds",
        "SecureString",

    ]

    for idx, item in enumerate(targets):

        connector = (
            "└──"
            if idx == len(targets)-1
            else "├──"
        )

        print(
            f"  {B}{connector}{W} "
            f"{item}"
        )


def render_opsec():

    print(
        f"\n{Y}"
        f"┌── OPSEC NOTES "
        f"────────────────────────────────────┐{W}"
    )

    notes = [

        "large event logs may freeze consoles",
        "Get-WinEvent is slower and noisier",
        "prefer wevtutil when possible",
        "PowerShell logging may generate events",
        "EDR may monitor log access patterns",

    ]

    for note in notes:

        print(
            f"{Y}│{W} "
            f"{note}"
        )

    print(
        f"{Y}"
        f"└──────────────────────────────────────────────────┘{W}"
    )


def render_commands(entry, admin):

    print(
        f"\n{G}"
        f"┌── WEVTUTIL "
        f"──────────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"{entry['wevtutil']}"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    if admin:

        print(
            f"\n{G}"
            f"┌── POWERSHELL "
            f"────────────────────────────────────┐{W}"
        )

        print(
            f"{G}│{W} "
            f"{entry['powershell']}"
        )

        print(
            f"{G}"
            f"└──────────────────────────────────────────────────┘{W}"
        )


def generic_hunt(admin):

    try:

        keyword = input(
            f"\n{B}keyword{W}> "
        ).strip()

    except (KeyboardInterrupt, EOFError):

        print()

        return

    if not keyword:
        return

    wevtutil = (
        f'wevtutil qe Security /rd:true /f:text '
        f'| findstr /i "{keyword}"'
    )

    powershell = (
        f'Get-WinEvent -LogName Security '
        f'| Select-String "{keyword}"'
    )

    print(
        f"\n{G}"
        f"┌── WEVTUTIL "
        f"──────────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"{wevtutil}"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    if admin:

        print(
            f"\n{G}"
            f"┌── POWERSHELL "
            f"────────────────────────────────────┐{W}"
        )

        print(
            f"{G}│{W} "
            f"{powershell}"
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
        f"[*] WINDOWS EVENT LOG HUNTER{W}"
    )

    admin = ask_admin()

    if not admin:

        reader = ask_eventlog_reader()

        if not reader:

            print(
                f"\n{R}[!] "
                f"Insufficient privileges for most logs.{W}"
            )

    render_targets()

    render_menu()

    try:

        choice = input(
            f"\n{B}select{W}> "
        ).strip()

    except (KeyboardInterrupt, EOFError):

        print()

        return data

    if choice in SEARCHES:

        render_commands(
            SEARCHES[choice],
            admin,
        )

    elif choice == "4":

        generic_hunt(admin)

    render_opsec()

    return data
