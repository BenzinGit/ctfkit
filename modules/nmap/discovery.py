import subprocess


PROVIDES = []
REQUIRES = []


def run(data, cred, args):

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    W = '\033[0m'
    R = '\033[91m'
    M = '\033[95m'


    ref = getattr(
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
    # REFERENCE MODE
    # -----------------------------

    if ref:

        print(
            f"\n{B}┌── REFERENCE "
            f"──────────────────────────────────────┐{W}"
        )

        print()

        print(
            f"{Y}fping -as {M}<SUBNET>{W}"
        )

        print()

        print(
            f"{Y}nmap -sn {M}<SUBNET>{W}"
        )

        print()

        print(
            f"{Y}nmap -sn -iL {M}<HOSTLIST>{W}"
        )

        print(
            f"\n{B}└──────────────────────────────────────────────┘{W}\n"
        )

        return

    # -----------------------------
    # MENU
    # -----------------------------

    method = "fping"

    if menu:

        print(
            f"\n[1] fping subnet"
        )

        print(
            f"[2] nmap subnet"
        )

        print(
            f"[3] nmap host file\n"
        )

        choice = input("> ").strip()

        if choice == "2":

            method = "nmap"

        elif choice == "3":

            method = "file"

    # -----------------------------
    # TARGET
    # -----------------------------

    ip = data.get("ip")

    if ip:

        default_subnet = (
            ".".join(
                ip.split(".")[:3]
            )
            + ".0/24"
        )

    else:

        default_subnet = ""

    subnet = input(
        f"\nSubnet "
        f"[{default_subnet}]: "
    ).strip()

    if not subnet:

        subnet = default_subnet

    # -----------------------------
    # BUILD COMMAND
    # -----------------------------

    if method == "fping":

        cmd = (
            f"fping -as {subnet}"
        )

    elif method == "nmap":

        cmd = (
            f"nmap -sn {subnet}"
        )

    else:

        hostfile = input(
            "\nHost file: "
        ).strip()

        cmd = (
            f"nmap -sn -iL {hostfile}"
        )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: HOST DISCOVERY "
        f"─────────────────────┐{W}"
    )

    print(
        f"{B}│{W} "
        f"SUBNET: "
        f"{C}{subnet:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W} "
        f"METHOD: "
        f"{C}{method.upper():<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└───────────────────────────────────────────────┘{W}"
    )

    # -----------------------------
    # COMMAND
    # -----------------------------

    print(
        f"\n{B}[*]{W} "
        f"COMMAND\n"
    )

    print(
        f"{Y}{cmd}{W}\n"
    )

    # -----------------------------
    # EXECUTE
    # -----------------------------

    subprocess.run(
        cmd,
        shell=True
    )

    print()