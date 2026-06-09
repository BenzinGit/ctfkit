import subprocess


PROVIDES = []
REQUIRES = ["ip"]


def run(data, cred, args):

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    W = '\033[0m'
    R = '\033[91m'
    M = '\033[95m'

    reference = getattr(
        args,
        "reference",
        False
    )

    menu = getattr(
        args,
        "menu",
        False
    )

    # -----------------------------
    # REFERENCE
    # -----------------------------

    if reference:

        print(
            f"\n{B}┌── REFERENCE "
            f"──────────────────────────────────────┐{W}"
        )

        print()

        print(
            f"{Y}smtp-user-enum "
            f"-M VRFY "
            f"-U {M}<WORDLIST>{W} "
            f"-t {M}<IP>{W}"
        )

        print()

        print(
            f"{Y}nc {M}<IP>{W} 25{W}"
        )

        print()

        print(
            f"{Y}VRFY root{W}"
        )

        print()

        print(
            f"{Y}VRFY admin{W}"
        )

        print()

        print(
            f"{Y}VRFY postmaster{W}"
        )

        print(
            f"\n{B}└──────────────────────────────────────────────┘{W}\n"
        )

        return

    # -----------------------------
    # TARGET
    # -----------------------------

    ip = data.get("ip")

    if not ip:

        print(
            f"\n{R}[!]{W} "
            f"No target IP loaded."
        )

        return

    # -----------------------------
    # MENU
    # -----------------------------

    mode = "enum"

    if menu:

        print()

        print(
            "[1] smtp-user-enum"
        )

        print(
            "[2] Manual VRFY"
        )

        print()

        choice = input(
            "> "
        ).strip()

        if choice == "2":

            mode = "vrfy"

    # -----------------------------
    # WORDLIST
    # -----------------------------

    wordlist = (
        "/usr/share/seclists/"
        "Usernames/"
        "Names/"
        "names.txt"
    )

    custom = input(
        f"\nWordlist [{wordlist}]: "
    ).strip()

    if custom:

        wordlist = custom

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: SMTP USER ENUM "
        f"────────────────────┐{W}"
    )

    print(
        f"{B}│{W} "
        f"TARGET:   "
        f"{C}{ip:<36}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W} "
        f"WORDLIST: "
        f"{C}{wordlist[:36]:<36}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└───────────────────────────────────────────────┘{W}"
    )

    # -----------------------------
    # MANUAL VRFY
    # -----------------------------

    if mode == "vrfy":

        print(
            f"\n{B}[{W}{G}*{W}{B}]{W} "
            f"COMMON USERS\n"
        )

        users = [

            "root",
            "admin",
            "administrator",
            "postmaster",
            "backup",
            "svc_backup"

        ]

        for user in users:

            print(
                f"{Y}VRFY {user}{W}"
            )

        print()

        print(
            f"{Y}nc {ip} 25{W}"
        )

        print()

        return

    # -----------------------------
    # ENUMERATION
    # -----------------------------

    cmd = (
        f"smtp-user-enum "
        f"-M VRFY "
        f"-U {wordlist} "
        f"-t {ip}"
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"COMMAND\n"
    )

    print(
        f"{Y}{cmd}{W}\n"
    )

    subprocess.run(
        cmd,
        shell=True
    )

    print()
