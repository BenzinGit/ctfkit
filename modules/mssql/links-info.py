from pathlib import Path
from datetime import datetime
import subprocess

from core.paths import get_chain_artifacts_dir


def run(data, cred, args):
    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'
    BOLD = '\033[1m'

    if not cred:

        print(
            f"\n{R}[!] {W}{BOLD}NO CREDENTIAL SELECTED{W}\n"
        )

        return data

    if not getattr(args, "extra", None):

        print(
            f"\n{R}[!] {W}Missing linked server name\n"
        )

        print(
            f"{B}Usage:{W} "
            f"{Y}ctf mssql.link-info SERVER{W}\n"
        )

        return data

    

    target = data.get("ip")

    username = cred["user"]
    auth_type = cred["type"]
    secret = cred["secret"]
    
    linked_server = args.extra

    if isinstance(linked_server, list):
        linked_server = " ".join(linked_server)
    artifact_dir = get_chain_artifacts_dir(
        data["name"],
        "mssql"
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
        f"mssql_link_info_{timestamp}.log"
    )

    query = (
        "EXECUTE("
        "'SELECT @@servername,"
        "SYSTEM_USER,"
        "IS_SRVROLEMEMBER(''sysadmin'')'"
        f") AT [{linked_server}]"
    )

    cmd = [
        "netexec",
        "mssql",
        target,
        "-u",
        username,
        "--local-auth",
        "-q",
        query,
        "--log",
        str(logfile)
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
        f"\n{B}┌── {BOLD}MODULE: MSSQL LINK INFO{W}{B} ───────────────────┐{W}"
    )

    print(
        f"{B}│{W}  {B}Target:{W} "
        f"{C}{target:<32}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}Link:{W}   "
        f"{C}{linked_server:<32}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└────────────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{B}[*]{W} Running\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    subprocess.run(cmd)

    if not logfile.exists():

        print(
            f"\n{R}[!] {W}No log file created\n"
        )

        return data

    log_text = logfile.read_text(
        errors="ignore"
    )

    #
    # SHOW RAW RESULTS
    #
    print(
        f"\n{B}[*]{W} Results\n"
    )

    interesting = []

    for line in log_text.splitlines():

        if "mssql.py:294" in line:

            interesting.append(
                line.split("INFO - ", 1)[1]
            )

    if interesting:

        for line in interesting:

            print(line)

    else:

        print(
            f"{Y}[-]{W} No linked server data returned"
        )

    print()

    print(
        f"{G}[+] {W}Log Saved"
    )

    print(
        f"{B}  └── {C}{logfile}{W}\n"
    )

    return data
