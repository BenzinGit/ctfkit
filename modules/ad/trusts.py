PROVIDES = []
REQUIRES = ["creds"]


def run(data, cred, args):

    import subprocess

    from core.paths import (
        get_artifacts_dir,
        get_tools_dir,
    )
    from modules.upload.windows import stage_windows_files

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'

    ip = data["ip"]
    domain = data["domain"]
    target = data["name"]

    artifacts = get_artifacts_dir(target)

    #
    # Windows Reference
    #

    if getattr(args, "windows", False):

        print(
            f"\n{B}[?]{W} Transfer PowerView?\n"
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

            stage_windows_files([
                get_tools_dir() / "windows" / "PowerView.ps1"
            ])

        print()

        print(
            f"{G}[+] ActiveDirectory Module{W}\n"
        )

        print(
            f"{Y}Import-Module ActiveDirectory{W}"
        )

        print()

        print(
            f"{Y}Get-ADTrust -Filter *{W}"
        )

        print()

        print(
            f"{G}[+] PowerView{W}\n"
        )

        print(
            f"{Y}. .\\PowerView.ps1{W}"
        )

        print()

        print(
            f"{Y}Get-DomainTrust{W}"
        )

        print(
            f"{Y}Get-DomainTrustMapping{W}"
        )

        print()

        print(
            f"{Y}Get-DomainUser -Domain {C}<domain>{W}"
        )

        print()

        print(
            f"{G}[+] netdom{W}\n"
        )

        print(
            f"{Y}netdom query trust{W}"
        )

        print(
            f"{Y}netdom query dc{W}"
        )

        print(
            f"{Y}netdom query workstation{W}"
        )

        print()

        return

    #
    # Linux
    #

    outfile = artifacts / "trusts.txt"

    base_dn = ",".join(
        f"DC={x}"
        for x in domain.split(".")
    )

    cmd = [
        "ldapsearch",
        "-x",
        "-H",
        f"ldap://{ip}",
        "-D",
        f"{domain}\\{cred['user']}",
        "-w",
        cred["secret"],
        "-b",
        f"CN=System,{base_dn}",
        "(objectClass=trustedDomain)",
    ]

    print()

    print(
        f"{B}[*]{W} Enumerating domain trusts..."
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    cmd.extend([
        "-o",
        str(outfile),
    ])

    subprocess.run(cmd)

    print()

    print(
        f"{G}[+] Output saved:{W} {outfile}"
    )

    print()
