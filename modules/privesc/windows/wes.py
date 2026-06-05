from pathlib import Path
import subprocess

BASE_DIR = Path(__file__).resolve().parents[3]

VENV_DIR = BASE_DIR / "venvs" / "wesng"
WES_BIN = VENV_DIR / "bin" / "wes"


def ensure_wesng():
    if WES_BIN.exists():
        return True

    print("[*] Installing WES-NG...")

    try:
        subprocess.run(
            ["python3", "-m", "venv", str(VENV_DIR)],
            check=True
        )

        pip = VENV_DIR / "bin" / "pip"

        subprocess.run(
            [str(pip), "install", "wesng"],
            check=True
        )

        subprocess.run(
            [str(WES_BIN), "--update"],
            check=True
        )

        return True

    except subprocess.CalledProcessError as e:
        print(f"[!] Installation failed: {e}")
        return False


def run(data, cred, args):
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    sysinfo = getattr(args, "file", None)

    if not sysinfo:
        print(
            f"\n{R}[!] {W}Usage: "
            f"ctf privesc.windows.wes <systeminfo.txt>"
        )
        return

    sysinfo = Path(sysinfo).resolve()

    if not sysinfo.exists():
        print(f"\n{R}[!] File not found:{W}")
        print(f"  {sysinfo}")
        return

    if not ensure_wesng():
        return

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"Running WES-NG against "
        f"{Y}{sysinfo.name}{W}"
    )

    subprocess.run(
        [
            str(WES_BIN),
            str(sysinfo)
        ]
    )
