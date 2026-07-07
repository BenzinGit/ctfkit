def run(
    data,
    cred,
    args,
):

    from datetime import datetime
    import subprocess
    from core.paths import get_artifacts_dir

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'


    if getattr(
        args,
        "windows",
        False
    ):

        G = '\033[92m'
        C = '\033[96m'
        B = '\033[94m'
        Y = '\033[93m'
        R = '\033[91m'
        W = '\033[0m'

        BOLD = '\033[1m'

        from core.paths import get_tools_dir
        from modules.upload.windows import stage_windows_files

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

        #
        # ActiveDirectory
        #

        print(
            f"\n{G}[+] {W}ActiveDirectory Module\n"
        )

        print(
            f"{Y}Import-Module ActiveDirectory{W}"
        )

        print()

        print(
            f"{Y}Get-ADGroup -Filter * | select name{W}"
        )

        print(
            f"{Y}Get-ADGroup -Identity {C}<group>{W}"
        )

        print(
            f"{Y}Get-ADGroupMember -Identity {C}<group>{W}"
        )

        print()

        #
        # PowerView
        #

        print(
            f"{G}[+] {W}PowerView\n"
        )

        print(
            f"{Y}. .\\PowerView.ps1{W}"
        )

        print()

        print(
            f"{Y}Get-DomainGroup{W}"
        )

        print(
            f"{Y}Get-DomainGroupMember -Identity {C}<group>{W}"
        )

        print(
            f"{Y}Get-DomainGroupMember -Identity {C}<group>{W} -Recurse"
        )

        print()

        #
        # SharpView
        #

        print(
            f"{G}[+] {W}SharpView\n"
        )

        print(
            f"{Y}SharpView.exe Get-DomainGroup{W}"
        )

        print(
            f"{Y}SharpView.exe Get-DomainGroupMember --Identity {C}<group>{W}"
        )

        print()

        return


    if not cred:

        print(
            f"\n{R}[!] {W}LDAP requires credentials\n"
        )

        return set()

    target = data.get("ip")
    domain = data.get("domain")
    target_name = data.get("name")
    current_user = cred["user"]
    current_secret = cred["secret"]
    cred_type = cred["type"]

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    logfile = (
        get_artifacts_dir(target_name) /
        f"ldap_groups_{timestamp}.log"
    )

    cmd = [
        "netexec",
        "ldap",
        str(target)
    ]

    if domain:

        cmd.extend([
            "-d",
            domain
        ])

    if cred_type == "password":

        cmd.extend([
            "-u",
            current_user,
            "-p",
            current_secret
        ])

    elif cred_type == "ntlm":

        cmd.extend([
            "-u",
            current_user,
            "-H",
            current_secret
        ])

    elif cred_type == "ticket":

        cmd.extend([
            "--use-kcache"
        ])

    cmd.extend([
        "--groups",
        "--log",
        str(logfile)
    ])

    print(
        f"\n{B}[*]{W} LDAP Group Enumeration\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    subprocess.run(
        cmd
    )

    if not logfile.exists():

        print(
            f"{R}[!] {W}No logfile created\n"
        )

        return set()

    groups = set()

    header_found = False
    lines = logfile.read_text(
        errors="ignore"
    ).splitlines()
    for line in lines:

        if "-Group-" in line:
            header_found = True
            continue

        if not header_found:
            continue

        if "LDAP" not in line:
            continue

        try:

            #
            # Strip logger prefix
            #

            ldap_idx = line.index("LDAP")

            row = line[ldap_idx:]

            #
            # LDAP IP PORT HOSTNAME GROUPNAME MEMBERS DESC
            #

            parts = row.split()

            if len(parts) < 5:
                continue

            #
            # Skip LDAP IP PORT HOSTNAME
            #

            group = parts[4]

            if (
                group.startswith("-")
                or group.startswith("[")
            ):
                continue

            groups.add(group)

        except Exception:
            pass

    groups = sorted(
        groups
    )

    print(
        f"{G}[+] {W}"
        f"{len(groups)} group(s) recovered\n"
    )

    interesting = {

        "Domain Admins",
        "Enterprise Admins",
        "Schema Admins",
        "Administrators",
        "Backup Operators",
        "Account Operators",
        "Server Operators",
        "Print Operators",
        "DnsAdmins",
        "Exchange Windows Permissions",
        "Remote Management Users"
    }

    found = [
        g for g in groups
        if g in interesting
    ]

    if found:

        print(
            f"{G}[+] {W}Interesting Groups\n"
        )

        for group in found[:20]:

            print(
                f"  {B}├──{W} "
                f"{C}{group}{W}"
            )

        print()

    groups_file = (
        get_artifacts_dir(target_name) /
        "groups.txt"
    )

    groups_file.write_text(
        "\n".join(groups)
    )

    print(
        f"{G}[+] {W}Groups Saved"
    )

    print(
        f"{B}  └── {C}{groups_file}{W}\n"
    )

    return set(
        groups
    )
