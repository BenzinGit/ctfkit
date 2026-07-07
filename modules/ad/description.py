PROVIDES = []
REQUIRES = ["creds"]


def run(data, cred, args):

    import subprocess

    from core.paths import get_artifacts_dir

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'

    ip = data["ip"]
    target = data["name"]

    artifacts = get_artifacts_dir(target)

    outfile = artifacts / "description_users.txt"

    #
    # Windows Reference
    #

    if getattr(args, "windows", False):

        from core.paths import get_tools_dir
        from modules.upload.windows import stage_windows_files

        print(
            f"{B}[?]{W} Transfer PowerView?\n"
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
                get_tools_dir()
                / "windows"
            )

            powerview = (
                windows_tools
                / "PowerView.ps1"
            )

            stage_windows_files([
                powerview
            ])
        print(
            f"\n{B}┌── WINDOWS REFERENCE ─────────────────────────────┐{W}"
        )
        print(
            f"\n{G}[+] {W}PowerView\n"
        )

        print(
            f"{Y}Import-Module .\\PowerView.ps1{W}"
        )

        print()

        print(
            f"{Y}Get-DomainUser * | "
            f"Select samaccountname,description | "
            f"Where {{$_.Description -ne $null}}{W}"
        )

        print()
        print(
            f"{B}└──────────────────────────────────────────────────┘{W}\n"
        )

        return

    #
    # Linux Enumeration
    #

    cmd = [
        "nxc",
        "ldap",
        ip,
        "-u",
        cred["user"],
        "-p",
        cred["secret"],
        "--users",
    ]

    print()

    print(
        f"{B}[*]{W} Enumerating user description fields..."
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    outfile.write_text(result.stdout)


    #
    # Highlight interesting descriptions
    #

    print(f"{B}[*]{W} Interesting Description Fields:\n")

    for line in result.stdout.splitlines():

        if "LDAP" not in line:
            continue

        if "Description" in line:
            continue

        if "***" in line or "Password" in line or "HTB{" in line:
            print(f"{G}{line}{W}")

    print()

    print(
        f"{G}[+] Raw output saved:{W} {outfile}"
    )

    print()