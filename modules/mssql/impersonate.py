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

    artifact_dir = (
        get_chain_artifacts_dir(
            data["name"],
            "mssql"
        )
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
        f"mssql_impersonate_{timestamp}.log"
    )

    query = (
        "SELECT distinct b.name "
        "FROM sys.server_permissions a "
        "INNER JOIN sys.server_principals b "
        "ON a.grantor_principal_id = b.principal_id "
        "WHERE a.permission_name = 'IMPERSONATE'"
    )

    cmd = [
        "netexec",
        "mssql",
        target,
        "-u",
        username,
        "--local-auth",
        f'-q "{query}" '
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
        f"\n{B}┌── {BOLD}MODULE: MSSQL IMPERSONATION{W}{B} ─────────────┐{W}"
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
        f"{B}└────────────────────────────────────────────────┘{W}"
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

    logfile.write_text(
        result.stdout +
        "\n" +
        result.stderr
    )

    candidates = []

    for line in result.stdout.splitlines():

        line = line.strip()

        if not line:
            continue

        if line.lower() in [
            "name",
            "rows affected"
        ]:
            continue

        if "MSSQL" in line:
            continue

        if len(line) > 50:
            continue

        if (
            line.isalnum()
            or "\\" in line
            or "_" in line
        ):
            candidates.append(
                line
            )

    candidates = sorted(
        set(candidates)
    )

    if candidates:

        print(
            f"\n{G}[+] {W}Impersonation Targets\n"
        )

        for user in candidates:

            print(
                f"  {B}├──{W} "
                f"{C}{user}{W}"
            )

        print()

    else:

        print(
            f"\n{Y}[-]{W} No impersonation "
            f"targets identified\n"
        )

    print(
        f"{G}[+] {W}Output Saved"
    )

    print(
        f"{B}  └── {C}{logfile}{W}\n"
    )

    return data
