PROVIDES = []
REQUIRES = ["creds"]


def run(data, cred, args):

    import subprocess

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'
    DIM = '\033[2m'

    ip = data["ip"]

    #
    # Windows Reference
    #

    if getattr(args, "windows", False):

        print(
            f"\n{B}┌── WINDOWS REFERENCE ─────────────────────────────┐{W}"
        )

        print()

        print(f"{W}# Import helper module{W}")
        print(f"{Y}Import-Module .\\SecurityAssessment.ps1{W}")
        print()

        print(f"{W}# Check local Print Spooler{W}")
        print(f"{Y}Get-Service Spooler{W}")
        print()

        print(f"{W}# Check remote Print Spooler (HTB method){W}")
        print(
            f"{Y}Get-SpoolStatus -ComputerName "
            f"{data['hostname']}.{data['domain'].upper()}{W}"
        )
        print()

        print(f"{W}# Native PowerShell alternative{W}")
        print(
            f"{Y}Get-Service -ComputerName "
            f"{data['hostname']} Spooler{W}"
        )

        print()

        print(
            f"{B}└──────────────────────────────────────────────────┘{W}\n"
        )

        return

    #
    # Menu
    #

    print(
        f"\n{B}┌── PRINTERBUG ───────────────────────┐{W}"
    )

    print(
        f"  {B}[1]{W} Enumerate"
    )

    print(
        f"  {B}[2]{W} Exploit\n"
    )

    choice = input(
        f"{Y}Select> {W}"
    ).strip()

    #
    # Enumeration
    #

    if choice == "1":

        cmd = (
            f"impacket-rpcdump @{ip} "
            f"| egrep 'MS-RPRN|MS-PAR'"
        )

        print()

        print(f"{B}[*]{W} Checking exposed print protocols...")
        print(f"{Y}{cmd}{W}\n")

        subprocess.run(
            cmd,
            shell=True,
        )

        print()

        return

    #
    # Exploit
    #

    if choice == "2":

        print()

        print(
            f"{Y}[!]{W} PrinterBug exploitation "
            f"is not implemented yet."
        )

        print()

        print(f"{DIM}Planned workflow:{W}")
        print(f"{DIM}  • Start ntlmrelayx{W}")
        print(f"{DIM}  • Trigger PrinterBug{W}")
        print(f"{DIM}  • Relay to AD CS / LDAP{W}")
        print(f"{DIM}  • Obtain certificate or relay result{W}")

        print()

        return

    print(
        f"\n{R}[!] Invalid selection.{W}\n"
    )
