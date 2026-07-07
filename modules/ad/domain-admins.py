from datetime import datetime
import subprocess
from core.paths import get_artifacts_dir
from core.paths import get_tools_dir


def run(
    data,
    cred,
    args,
):

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'

    if not cred:

        print(
            f"\n{R}[!] {W}Credentials required\n"
        )

        return set()

    if cred["type"] != "password":

        print(
            f"\n{R}[!] {W}Windapsearch requires password authentication\n"
        )

        return set()

    target = data.get("ip")
    domain = data.get("domain")
    target_name = data.get("name")

    current_user = cred["user"]
    current_secret = cred["secret"]

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    logfile = (
        get_artifacts_dir(target_name) /
        f"domain_admins_{timestamp}.log"
    )

    cmd = [
        "python3",
        str(
            get_tools_dir() /
            "windapsearch.py"
        ),
        "--dc-ip",
        target,
        "-u",
        f"{current_user}@{domain}",
        "-p",
        current_secret,
        "--da"
    ]

    print(
        f"\n{B}[*]{W} Domain Admin Enumeration\n"
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

    admins = set()

    current_cn = None
    current_has_upn = False

    for line in result.stdout.splitlines():

        line = line.strip()

        #
        # New entry
        #

        if line.startswith("cn:"):

            #
            # Previous entry had no UPN
            #

            if current_cn and not current_has_upn:

                admins.add(
                    current_cn
                )

            current_cn = (
                line.split(
                    ":",
                    1
                )[1]
                .strip()
            )

            current_has_upn = False

            continue

        #
        # Prefer UPN
        #

        if line.startswith("userPrincipalName:"):

            username = (
                line.split(
                    ":",
                    1
                )[1]
                .strip()
                .split("@")[0]
            )

            admins.add(
                username
            )

            current_has_upn = True

            continue

    #
    # Last entry in file
    #

    if current_cn and not current_has_upn:

        admins.add(
            current_cn
        )

    admins = sorted(
        admins
    )

    outfile = (
        get_artifacts_dir(target_name) /
        "domain_admins.txt"
    )

    outfile.write_text(
        "\n".join(admins)
    )

    print(
        f"{G}[+] {W}"
        f"{len(admins)} Domain Admin(s)\n"
    )

    for user in admins:

        print(
            f"  {B}├──{W} "
            f"{C}{user}{W}"
        )

    print()

    print(
        f"{G}[+] {W}Saved"
    )

    print(
        f"{B}  ├── {C}{outfile}{W}"
    )

    print(
        f"{B}  └── {C}{logfile}{W}\n"
    )

    return set(
        admins
    )