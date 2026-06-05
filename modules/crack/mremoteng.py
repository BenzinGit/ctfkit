from pathlib import Path
import subprocess


def run(data, cred, args):
    # --- COLORS ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    secret = getattr(args, "file", None)

    if not secret:
        print(f"\n{R}[!] {W}{BOLD}MISSING ENCRYPTED STRING{W}")
        print(f"{B}  └── Usage:{W} ctf crack.mremoteng <encrypted_string>")
        return

    tool = Path(__file__).resolve().parents[2] / "tools" / "mremoteng_decrypt.py"

    if not tool.exists():
        print(f"\n{R}[!] {W}{BOLD}TOOL NOT FOUND{W}")
        print(f"{B}  └── {tool}")
        return

    print(f"\n{B}┌── {BOLD}MODULE: MREMOTENG RECOVERY{W}{B} ───────────────────────┐{W}")
    print(f"{B}│{W}  {B}Status:{W} Decrypting password...                     {B}│{W}")
    print(f"{B}└─────────────────────────────────────────────────────┘{W}")

    cmd = [
        "python3",
        str(tool),
        "-s",
        secret
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"\n{R}[!] {W}{BOLD}DECRYPTION FAILED{W}")
        print(result.stderr)
        return

    password = result.stdout.strip()

    print(f"\n{G}┌── RECOVERED PASSWORD ────────────────────────────────┐{W}")
    print(f"{G}│{W}  {BOLD}{Y}{password:<52}{W}{G}│{W}")
    print(f"{G}└──────────────────────────────────────────────────────┘{W}\n")