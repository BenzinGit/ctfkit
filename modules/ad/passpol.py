PROVIDES = ["passpol"]
REQUIRES = []


from core.paths import get_artifacts_dir

def run(
    data,
    cred,
    args
):

    from pathlib import Path
    from datetime import datetime
    import subprocess

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'
    BOLD = '\033[1m'

    target = data.get("ip")

    if not target:

        print(
            f"\n{R}[!] {W}No target selected\n"
        )

        return data

    #
    # WINDOWS REFERENCE
    #

    if getattr(args, "windows", False):

        print(
            f"\n{G}[+] {W}Windows\n"
        )

        print(
            f"{Y}net accounts{W}\n"
        )

        print(
            f"{Y}Import-Module .\\PowerView.ps1{W}"
        )

        print(
            f"{Y}Get-DomainPolicy{W}\n"
        )

        return data

    #
    # ARTIFACTS
    #

    artifact_dir = get_artifacts_dir(
        "ad"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    logfile = (
        artifact_dir /
        f"passpol_{timestamp}.log"
    )

    #
    # MENU
    #

    print(
        f"\n{B}┌── {BOLD}MODULE: PASSWORD POLICY{W}{B} ───────────┐{W}"
    )

    print(
        f"{B}│{W}  {B}Target:{W} "
        f"{C}{target:<30}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└──────────────────────────────────────────┘{W}\n"
    )

    print(
        f"  {B}[1]{W} NetExec"
    )

    print(
        f"  {B}[2]{W} rpcclient (NULL)"
    )

    print(
        f"  {B}[3]{W} enum4linux"
    )

    print(
        f"  {B}[4]{W} enum4linux-ng"
    )

    print(
        f"  {B}[5]{W} All\n"
    )

    choice = input(
        f"{C}Select> {W}"
    ).strip()

    #
    # NETEXEC
    #

    if choice == "1":

        if not cred:

            print(
                f"\n{R}[!] {W}Need credentials\n"
            )

            return data

        if cred["type"] != "password":

            print(
                f"\n{R}[!] {W}NetExec requires password auth\n"
            )

            return data

        cmd = [
            "netexec",
            "smb",
            target,
            "-u",
            cred["user"],
            "-p",
            cred["secret"],
            "--pass-pol"
        ]

    #
    # RPCCLIENT
    #

    elif choice == "2":

        cmd = [
            "rpcclient",
            "-U",
            "",
            "-N",
            target,
            "-c",
            "getdompwinfo"
        ]

    #
    # ENUM4LINUX
    #

    elif choice == "3":

        cmd = [
            "enum4linux",
            "-P",
            target
        ]

    #
    # ENUM4LINUX-NG
    #

    elif choice == "4":

        cmd = [
            "enum4linux-ng",
            "-P",
            target
        ]

    #
    # ALL
    #

    elif choice == "5":

        commands = [
            [
                "rpcclient",
                "-U",
                "",
                "-N",
                target,
                "-c",
                "getdompwinfo"
            ],
            [
                "enum4linux",
                "-P",
                target
            ],
            [
                "enum4linux-ng",
                "-P",
                target
            ]
        ]

        if cred and cred["type"] == "password":

            commands.insert(
                0,
                [
                    "netexec",
                    "smb",
                    target,
                    "-u",
                    cred["user"],
                    "-p",
                    cred["secret"],
                    "--pass-pol"
                ]
            )

        output = ""

        for cmd in commands:

            print(
                f"\n{Y}{' '.join(cmd)}{W}\n"
            )

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            output += (
                f"\n{'=' * 80}\n"
                f"{' '.join(cmd)}\n"
                f"{'=' * 80}\n"
            )

            output += result.stdout
            output += result.stderr

        logfile.write_text(
            output
        )

        print(
            f"\n{G}[+] {W}Saved"
        )

        print(
            f"{B}  └── {C}{logfile}{W}\n"
        )

        return data

    else:

        return data

    #
    # RUN
    #

    print(
        f"\n{B}[*]{W} Running\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    logfile.write_text(
        result.stdout +
        result.stderr
    )

    print(
        result.stdout
    )

    #
    # SPRAY RECOMMENDATION
    #

    text = (
        result.stdout +
        result.stderr
    ).lower()

    if (
        "threshold: 5" in text or
        "lockout threshold: 5" in text
    ):

        print(
            f"\n{G}[+] {W}Spraying Recommendation\n"
        )

        print(
            f"  {B}Attempts:{W} "
            f"{C}2{W}"
        )

        print(
            f"  {B}Wait:{W} "
            f"{C}31 minutes{W}\n"
        )

    print(
        f"{G}[+] {W}Artifact"
    )

    print(
        f"{B}  └── {C}{logfile}{W}\n"
    )

    return data
