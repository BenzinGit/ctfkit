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
            f"{Y}mysql "
            f"-u {M}<USER>{W} "
            f"-p{M}<PASSWORD>{W} "
            f"-h {M}<IP>{W}"
            f"--skip-ssl"
        )

        print()

        print(
            f"{Y}mysql "
            f"-u root "
            f"-h {M}<IP>{W}"
            f"--skip-ssl"

        )

        print()

        print(
            f"{Y}show databases;{W}"
        )

        print()

        print(
            f"{Y}use mysql;{W}"
        )

        print()

        print(
            f"{Y}show tables;{W}"
        )

        print()

        print(
            f"{Y}select version();{W}"
        )

        print(
            f"\n{B}└──────────────────────────────────────────────┘{W}\n"
        )

        return

    # -----------------------------
    # TARGET
    # -----------------------------

    ip = data.get(
        "ip"
    )

    if not ip:

        print(
            f"\n{R}[!]{W} "
            f"No target IP loaded."
        )

        return

    # -----------------------------
    # AUTH
    # -----------------------------

    auth_label = "root (no password)"
    cmd = (
        f"mysql "
        f"-u root "
        f"-h {ip}"
    )

    creds = data.get(
        "creds",
        []
    )

    current_index = data.get(
        "current_cred"
    )

    if (
        current_index is not None
        and current_index < len(creds)
    ):

        current = creds[
            current_index
        ]

        cred_type = current.get(
            "type"
        )

        if cred_type == "password":

            user = current.get(
                "user"
            )

            secret = current.get(
                "secret"
            )

            auth_label = (
                f"{user} (password)"
            )

            cmd = (
                f"mysql "
                f"-u '{user}' "
                f"-p'{secret}' "
                f"-h {ip} "
                f"--skip-ssl"

            )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: MYSQL CONNECT "
        f"──────────────────────┐{W}"
    )

    print(
        f"{B}│{W} "
        f"TARGET: "
        f"{C}{ip:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W} "
        f"AUTH:   "
        f"{C}{auth_label:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└───────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"COMMAND\n"
    )

    print(
        f"{Y}{cmd}{W}\n"
    )

    # -----------------------------
    # CONNECT
    # -----------------------------

    try:

        subprocess.run(
            cmd,
            shell=True
        )

    except KeyboardInterrupt:

        print(
            f"\n{R}[!]{W} "
            f"Connection interrupted."
        )

    print()
