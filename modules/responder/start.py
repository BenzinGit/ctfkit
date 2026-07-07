from core.attacker import get_current_interface
import subprocess


def run(data, cred, args):

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'
    BOLD = '\033[1m'

    #
    # REFERENCE MODE
    #

    if getattr(args, "reference", False):

        print()

        print(
            f"{Y}sudo responder -I <INTERFACE> -v{W}"
        )

        print()

        print(
            f"{Y}sudo responder -I <INTERFACE> -A{W}"
        )

        print()

        return data

    #
    # INTERFACE
    #

    interface = None

    try:

        interface = get_current_interface()

    except Exception:

        pass

    if not interface:

        interface = input(
            f"\n{B}[?]{W} Interface > "
        ).strip()

    if not interface:

        print(
            f"\n{R}[!] {W}No interface selected\n"
        )

        return data

    #
    # COMMAND
    #

    cmd = [
        "sudo",
        "responder",
        "-I",
        interface,
        "-v"
    ]

    print(
        f"\n{B}┌── {BOLD}MODULE: RESPONDER{W}{B} ──────────────┐{W}"
    )

    print(
        f"{B}│{W}  {B}Interface:{W} "
        f"{C}{interface:<25}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└─────────────────────────────────────┘{W}"
    )

    print(
        f"\n{B}[*]{W} Starting Responder\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    print(
        f"{G}[+] {W}Logs:"
    )

    print(
        f"{B}  └── {C}/usr/share/responder/logs/{W}\n"
    )

    subprocess.run(
        cmd
    )

    return data
