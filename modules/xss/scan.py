import subprocess

from core.paths import get_tools_dir
from core.target import get_current_url

PROVIDES = []
REQUIRES = []

# =========================================================
# COLORS
# =========================================================

G = "\033[92m"
C = "\033[96m"
B = "\033[94m"
Y = "\033[93m"
R = "\033[91m"
W = "\033[0m"
BOLD = "\033[1m"

# =========================================================
# MAIN
# =========================================================

def run(data, cred, args):

    #
    # ---------------------------------------------------------
    # TARGET
    # ---------------------------------------------------------
    #

    ip = get_current_url(data)

    if not ip:

        print(
            f"\n{R}[!] No target selected.{W}\n"
        )

        return

    url = input(
        f"{Y}Base URL [{ip}]> {W}"
    ).strip() or ip

    print()

    #
    # ---------------------------------------------------------
    # XSSTRIKE
    # ---------------------------------------------------------
    #

    xsstrike = (
        get_tools_dir()
        /
        "XSStrike"
        /
        "xsstrike.py"
    )

    if not xsstrike.exists():

        print(
            f"{R}[!] XSStrike not found:{W}"
        )

        print(
            f"    {C}{xsstrike}{W}\n"
        )

        return

    #
    # ---------------------------------------------------------
    # HUD
    # ---------------------------------------------------------
    #

    print(
        f"{B}┌── {BOLD}MODULE: XSSTRIKE{W}{B} ───────────────────────┐{W}"
    )

    print(
        f"{B}│{W} URL:{C} {url:<44}{W}{B}│{W}"
    )

    print(
        f"{B}└──────────────────────────────────────────────────┘{W}"
    )

    print()

    cmd = [
        "python3",
        str(xsstrike),
        "-u",
        url,
    ]

    print(
        f"{G}[+] Running{W}\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    subprocess.run(cmd)

    return data
