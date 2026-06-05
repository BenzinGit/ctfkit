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
            f"{Y}nxc smb {M}<IP>{W}"
        )

        print()

        print(
            f"{Y}nxc smb {M}<IP>{W} --shares{W}"
        )

        print()

        print(
            f"{Y}nmap -sV -sC -p139,445 {M}<IP>{W}"
        )

        print()

        print(
            f"{Y}enum4linux-ng -A {M}<IP>{W}"
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
    # COMMANDS
    # -----------------------------

    commands = [

        (
            "SMB INFO",
            f"nxc smb {ip}"
        ),

        (
            "SMB SHARES",
            f"nxc smb {ip} --shares"
        ),

        (
            "NMAP SMB",
            f"nmap -sV -sC -p139,445 {ip}"
        )

    ]

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: SMB ENUMERATION "
        f"────────────────────┐{W}"
    )

    print(
        f"{B}│{W} "
        f"TARGET: "
        f"{C}{ip:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└───────────────────────────────────────────────┘{W}"
    )

    # -----------------------------
    # EXECUTE
    # -----------------------------

    for title, cmd in commands:

        print(
            f"\n{B}[{W}{G}*{W}{B}]{W} "
            f"{title}\n"
        )

        print(
            f"{Y}{cmd}{W}\n"
        )

        subprocess.run(
            cmd,
            shell=True
        )

        print()