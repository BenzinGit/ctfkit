PROVIDES = ["reference"]
REQUIRES = []


def run(
    data,
    cred,
    args
):

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
        f"\n{B}┌── {BOLD}AD DOMAIN ENUMERATION{W}{B} ──────────────┐{W}"
    )

    print(
        f"{B}└──────────────────────────────────────────────┘{W}\n"
    )

    #
    # WINDOWS REFERENCE
    #

    if getattr(
        args,
        "windows",
        False
    ):

        print(
            f"{B}[?]{W} Transfer PowerView / SharpView?\n"
        )

        print(
            f"  {B}[1]{W} Yes"
        )

        print(
            f"  {B}[2]{W} No\n"
        )

        choice = input(
            f"{Y}Select> {W}"
        ).strip()

        if choice == "1":
            
            windows_tools = (
                get_tools_dir() /
                "windows"
            )

            PowerView = (
                windows_tools /
                "PowerView.ps1"
            )

            SharpView = (
                windows_tools /
                "SharpView.exe"
            )

            stage_windows_files([
                SharpView,
                PowerView
            ])

        print(
            f"\n{G}[+] {W}ActiveDirectory Module\n"
        )

        print(
            f"{Y}Import-Module ActiveDirectory{W}"
        )

        print()

        print(
            f"{Y}Get-ADDomain{W}"
        )

        print(
            f"{Y}Get-ADForest{W}"
        )

        print(
            f"{Y}Get-Forest{W}"
        )

        print(
            f"{Y}Get-ADDomainController{W}"
        )

        print(
            f"{Y}Get-DomainController{W}"
        )
        print()

        print(
            f"{Y}Get-ADTrust -Filter *{W}"
        )
        print(
            f"{Y}Get-DomainTrustMapping{W}"
        )
        print(
            f"{Y}Get-DomainTrust{W}"
        )

        print()

        print(
            f"{G}[+] {W}PowerView\n"
        )

        print(
            f"{Y}. .\\PowerView.ps1{W}"
        )

        print()

        print(
            f"{Y}Get-Domain{W}"
        )

        print(
            f"{Y}Get-Forest{W}"
        )

        print(
            f"{Y}Get-DomainController{W}"
        )

        print()

        print(
            f"{G}[+] {W}SharpView\n"
        )

        print(
            f"{Y}SharpView.exe Get-Domain{W}"
        )

        print(
            f"{Y}SharpView.exe Get-Forest{W}"
        )

        print(
            f"{Y}SharpView.exe Get-DomainController{W}"
        )

        print()

        return data

    #
    # LINUX REFERENCE
    #

    print(
        f"{G}[+] {W}NetExec LDAP\n"
    )

    print(
        f"{Y}netexec ldap <DC> -u <USER> -p <PASSWORD>{W}"
    )

    print()

    print(
        f"{G}[+] {W}Windapsearch\n"
    )

    print(
        f"{Y}python3 windapsearch.py --dc-ip <DC> -u <USER>@<DOMAIN> -p <PASSWORD>{W}"
    )

    print()

    print(
        f"{G}[+] {W}LDAPSearch\n"
    )

    print(
        f"{Y}ldapsearch -x -H ldap://<DC> -D '<DOMAIN>\\\\<USER>' -w <PASSWORD>{W}"
    )

    print()

    return data