PROVIDES = []
REQUIRES = ["creds"]


def run(data, cred, args):

    import subprocess

    from core.paths import get_artifacts_dir
    from core.paths import get_tools_dir
    from modules.upload.windows import stage_windows_files

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'

    ip = data["ip"]
    target = data["name"]

    artifacts = get_artifacts_dir(target)

    outfile = (
        artifacts /
        "password_not_required.txt"
    )

    #
    # Windows Reference
    #

    if getattr(args, "windows", False):

        print(
            f"\n{B}┌── WINDOWS REFERENCE ─────────────────────────────┐{W}"
        )

        print()

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

        print()

        print(
            f"{W}# Import PowerView{W}"
        )

        print(
            f"{Y}Import-Module .\\PowerView.ps1{W}"
        )

        print()

        print(
            f"{W}# Enumerate PASSWD_NOTREQD accounts{W}"
        )

        print(
            f"{Y}"
            f"Get-DomainUser "
            f"-UACFilter PASSWD_NOTREQD | "
            f"Select samaccountname,useraccountcontrol"
            f"{W}"
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
        "--password-not-required",
    ]

    print()

    print(
        f"{B}[*]{W} Enumerating PASSWD_NOTREQD accounts..."
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    result = subprocess.run(
        cmd
    )

