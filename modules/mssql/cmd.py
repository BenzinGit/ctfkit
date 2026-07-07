from pathlib import Path
from datetime import datetime
import subprocess

from core.target import get_current_ip
from core.paths import get_artifacts_dir


def run(data, cred, args):

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    W = '\033[0m'
    R = '\033[91m'
    BOLD = '\033[1m'

    target = get_current_ip(data)

    if not target:

        print(
            f"\n{R}[!] {W}{BOLD}NO TARGET{W}\n"
        )

        return

    if not cred:

        print(
            f"\n{R}[!] {W}{BOLD}NO CREDENTIAL SELECTED{W}\n"
        )

        return

    if not args.extra:

        print(
            f"\n{R}[!] {W}{BOLD}MISSING COMMAND{W}"
        )

        print(
            f"\n{B}Usage:{W}"
        )

        print(
            f"  {Y}ctf mssql.cmd whoami{W}"
        )

        print(
            f"  {Y}ctf mssql.cmd hostname{W}"
        )

        print(
            f"  {Y}ctf mssql.cmd \"ipconfig /all\"{W}\n"
        )

        return

    command = " ".join(args.extra)

    username = cred["user"]
    auth_type = cred["type"]
    secret = cred["secret"]

    artifact_dir = (
        get_artifacts_dir(data["name"])
        / "mssql"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    stamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    logfile = (
        artifact_dir /
        f"mssql_cmd_{stamp}.log"
    )

    cmd = [
        "netexec",
        "mssql",
        str(target),
        "-u",
        username,
        "-x",
        command,
        "--log",
        str(logfile),
        "--local-auth"
    ]

    if auth_type == "password":

        cmd.extend(
            [
                "-p",
                secret
            ]
        )

    elif auth_type == "ntlm":

        cmd.extend(
            [
                "-H",
                secret
            ]
        )

    elif auth_type == "ticket":

        cmd.append(
            "--use-kcache"
        )

    print(
        f"\n{B}┌── {BOLD}MODULE: MSSQL CMD{W}{B} ──────────────────────────┐{W}"
    )

    print(
        f"{B}│{W}  {B}Target:{W}  "
        f"{C}{target:<37}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}User:{W}    "
        f"{C}{username:<37}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}Command:{W} "
        f"{C}{command[:35]:<35}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└──────────────────────────────────────────────────────┘{W}"
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

    print(result.stdout)

    if result.stderr:

        print(result.stderr)

    logfile.write_text(
        result.stdout +
        "\n" +
        result.stderr
    )

    print(
        f"\n{G}[+] {W}Output Saved"
    )

    print(
        f"{B}  └── {C}{logfile}{W}\n"
    )

    return data
