PROVIDES = ["security"]
REQUIRES = []

def run(
    data,
    cred,
    args
):

    Y = '\033[93m'
    B = '\033[94m'
    C = '\033[96m'
    G = '\033[92m'
    W = '\033[0m'
    BOLD = '\033[1m'

    print(
        f"\n{B}┌── {BOLD}MODULE: AD SECURITY ENUMERATION{W}{B} ───────┐{W}"
    )

    print(
        f"{B}└──────────────────────────────────────────────────┘{W}\n"
    )

    #
    # DEFENDER
    #

    print(
        f"{G}[+] {W}Windows Defender\n"
    )

    print(
        f"{Y}Get-MpComputerStatus{W}\n"
    )

    #
    # APPLOCKER
    #

    print(
        f"{G}[+] {W}AppLocker\n"
    )

    print(
        f"{Y}"
        f"Get-AppLockerPolicy -Effective | "
        f"select -ExpandProperty RuleCollections"
        f"{W}\n"
    )

    #
    # LANGUAGE MODE
    #

    print(
        f"{G}[+] {W}PowerShell Language Mode\n"
    )

    print(
        f"{Y}$ExecutionContext.SessionState.LanguageMode{W}\n"
    )

    #
    # LAPS
    #

    print(
        f"{G}[+] {W}LAPS Delegated Groups\n"
    )

    print(
        f"{Y}Find-LAPSDelegatedGroups{W}\n"
    )

    print(
        f"{G}[+] {W}LAPS Extended Rights\n"
    )

    print(
        f"{Y}Find-AdmPwdExtendedRights{W}\n"
    )

    print(
        f"{G}[+] {W}LAPS Passwords\n"
    )

    print(
        f"{Y}Get-LAPSComputers{W}\n"
    )

    #
    # AV / EDR
    #

    print(
        f"{G}[+] {W}Installed Security Products\n"
    )

    print(
        f"{Y}"
        f"Get-CimInstance Win32_Product"
        f"{W}\n"
    )

    print(
        f"{Y}"
        f"Get-ItemProperty "
        f"HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*"
        f"{W}\n"
    )

    #
    # SERVICES
    #

    print(
        f"{G}[+] {W}Services\n"
    )

    print(
        f"{Y}Get-Service{W}\n"
    )

    print(
        f"{Y}sc query{W}\n"
    )

    #
    # QUICK ENUM
    #

    print(
        f"{G}[+] {W}Quick Checks\n"
    )

    print(
        f"{Y}whoami /priv{W}"
    )

    print(
        f"{Y}whoami /groups{W}"
    )

    print(
        f"{Y}net localgroup administrators{W}"
    )

    print(
        f"{Y}net user %USERNAME%{W}\n"
    )

    return data
