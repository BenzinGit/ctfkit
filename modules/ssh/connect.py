import os
import subprocess
from pathlib import Path


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
            f"{Y}ssh "
            f"{M}<USER>{W}@{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}ssh "
            f"-i {M}<KEY>{W} "
            f"{M}<USER>{W}@{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}chmod 600 "
            f"{M}<KEY>{W}"
        )

        print()

        print(
            f"{Y}scp "
            f"{M}<FILE>{W} "
            f"{M}<USER>{W}@{M}<IP>{W}:/tmp/{W}"
        )

        print()

        print(
            f"{Y}sftp "
            f"{M}<USER>{W}@{M}<IP>{W}"
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
    # PRIVATE KEY MODE
    # -----------------------------

    if getattr(
        args,
        "extra",
        None
    ):

        if len(args.extra) >= 1:

            key_file = Path(
                args.extra[0]
            )

            if key_file.exists():

                if len(args.extra) >= 2:

                    user = args.extra[1]

                else:

                    user = input(
                        "\nUSER [root]: "
                    ).strip()

                    if not user:

                        user = "root"

                try:

                    os.chmod(
                        key_file,
                        0o600
                    )

                except Exception:
                    pass

                cmd = (
                    f"ssh "
                    f"-i '{key_file}' "
                    f"{user}@{ip}"
                )

                auth_label = (
                    f"{user} (private key)"
                )

                print(
                    f"\n{B}┌── MODULE: SSH CONNECT "
                    f"────────────────────────┐{W}"
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

                try:

                    subprocess.run(
                        cmd,
                        shell=True
                    )

                except KeyboardInterrupt:

                    print(
                        f"\n{R}[!]{W} "
                        f"Connection closed."
                    )

                print()

                return

    # -----------------------------
    # CURRENT CREDENTIAL
    # -----------------------------

    creds = data.get(
        "creds",
        []
    )

    current_index = data.get(
        "current_cred"
    )

    if (
        current_index is None
        or current_index >= len(creds)
    ):

        print(
            f"\n{R}[!]{W} "
            f"No credential selected."
        )

        print()

        print(
            f"{Y}Examples:{W}"
        )

        print()

        print(
            f"{C}ctf ssh.connect{W}"
        )

        print(
            f"{C}ctf ssh.connect id_rsa{W}"
        )

        print(
            f"{C}ctf ssh.connect id_rsa root{W}"
        )

        print()

        return

    current = creds[
        current_index
    ]

    user = current.get(
        "user"
    )

    cred_type = current.get(
        "type"
    )

    auth_label = (
        f"{user} ({cred_type})"
    )

    # -----------------------------
    # PASSWORD
    # -----------------------------

    if cred_type == "password":

        cmd = (
            f"ssh "
            f"{user}@{ip}"
        )

    # -----------------------------
    # KERBEROS
    # -----------------------------

    elif cred_type == "ticket":

        cmd = (
            f"ssh "
            f"{user}@{ip}"
        )

    # -----------------------------
    # UNSUPPORTED
    # -----------------------------

    else:

        print(
            f"\n{R}[!]{W} "
            f"SSH does not support "
            f"credential type:"
            f" {cred_type}"
        )

        print()

        print(
            f"{Y}Use:{W}"
        )

        print(
            f"{C}ctf ssh.connect id_rsa{W}"
        )

        print()

        return

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: SSH CONNECT "
        f"────────────────────────┐{W}"
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

    try:

        subprocess.run(
            cmd,
            shell=True
        )

    except KeyboardInterrupt:

        print(
            f"\n{R}[!]{W} "
            f"Connection closed."
        )

    print()
