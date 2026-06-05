from pathlib import Path
import subprocess

from core.paths import get_tool_path


def run(data, cred, args):
    # --- COLORS ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    db = getattr(args, "file", None)

    if not db:
        print(f"\n{R}[!] {W}{BOLD}MISSING SQLITE DATABASE{W}")
        print(f"{B}  └── Usage:{W} ctf parse.cookie <cookies.sqlite>")
        return

    db_path = Path(db).expanduser().resolve()

    if not db_path.exists():
        print(f"\n{R}[!] {W}{BOLD}FILE NOT FOUND{W}")
        print(f"{B}  └── {db_path}")
        return

    host = getattr(args, "host", None)
    cookie = getattr(args, "cookie", None)

    if not host:
        print(f"\n{R}[!] {W}{BOLD}MISSING HOST{W}")
        print(f"{B}  └── Example:{W} --host slack")
        return

    if not cookie:
        print(f"\n{R}[!] {W}{BOLD}MISSING COOKIE NAME{W}")
        print(f"{B}  └── Example:{W} --cookie d")
        return

    tool = get_tool_path("cookieextractor.py")

    if not tool.exists():
        print(f"\n{R}[!] {W}{BOLD}TOOL NOT FOUND{W}")
        print(f"{B}  └── {tool}")
        return

    print(f"\n{B}┌── {BOLD}MODULE: COOKIE EXTRACTION{W}{B} ──────────────────────┐{W}")
    print(f"{B}│{W}  {B}Database:{W} {db_path.name:<37}{B}│{W}")
    print(f"{B}│{W}  {B}Host:{W}     {host:<37}{B}│{W}")
    print(f"{B}│{W}  {B}Cookie:{W}   {cookie:<37}{B}│{W}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{W}")

    cmd = [
        "python3",
        str(tool),
        "--dbpath",
        str(db_path),
        "--host",
        host,
        "--cookie",
        cookie,
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"\n{R}[!] {W}{BOLD}EXTRACTION FAILED{W}")
        print(result.stderr)
        return

    output = result.stdout.strip()

    if not output:
        print(f"\n{Y}[!] No cookie found.")
        return

    print(f"\n{G}┌── COOKIE VALUE ─────────────────────────────────────────┐{W}")
    print(output)
    print(f"{G}└──────────────────────────────────────────────────────────┘{W}\n")
