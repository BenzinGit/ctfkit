from core.paths import get_chain_artifacts_dir
from datetime import datetime
import subprocess


def run(data, cred, args):

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'
    BOLD = '\033[1m'

    if getattr(args, "reference", False):

        P = '\033[95m'

        print(
            f"\n{B}AD GROUP ADD MEMBER{W}\n"
        )

        print(
            f"{B}Windows{W}\n"
        )

        print(
            f"{Y}net group "
            f"\"{P}<GROUP>{Y}\" "
            f"{P}<USER>{Y} "
            f"/add /domain{W}"
        )

        print()

        print(
            f"{B}Linux (bloodyAD){W}\n"
        )

        print(
            f"{Y}bloodyAD "
            f"add groupMember "
            f"\"{P}<GROUP>{Y}\" "
            f"{P}<USER>{W}"
        )

        print()

        return data


    if not cred:

        print(
            f"\n{R}[!] {W}{BOLD}NO CREDENTIAL SELECTED{W}\n"
        )

        return data

    if not getattr(args, "extra", None):

        print(
            f"\n{R}[!] {W}Missing arguments\n"
        )

        print(
            f"{B}Usage:{W} "
            f"{Y}ctf ad.group-add-member USER GROUP{W}\n"
        )

        return data

    if len(args.extra) < 2:

        print(
            f"\n{R}[!] {W}Need user and group\n"
        )

        return data

    username = args.extra[0]

    group = " ".join(
        args.extra[1:]
    )

    target = data.get("ip")
    domain = data.get("domain")

    current_user = cred["user"]
    current_secret = cred["secret"]

    if cred["type"] != "password":

        print(
            f"\n{R}[!] {W}bloodyAD requires a password credential\n"
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

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    logfile = (
        artifact_dir /
        f"group_add_member_{timestamp}.log"
    )

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
        "groupMember",
        group,
        username
    ]

    print(
        f"\n{B}┌── {BOLD}MODULE: AD GROUP ADD MEMBER{W}{B} ──────┐{W}"
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
        f"{B}│{W}  {B}Group:{W}  "
        f"{C}{group:<28}{W}"
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

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    logfile.write_text(
        result.stdout +
        result.stderr
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    if result.returncode == 0:

        print(
            f"\n{G}[+] {W}Member added"
        )

    else:

        print(
            f"\n{R}[-] {W}Failed"
        )

    print(
        f"{B}  └── {C}{logfile}{W}\n"
    )

    return data