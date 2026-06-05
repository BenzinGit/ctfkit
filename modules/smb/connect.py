import os
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

    if reference:

        print(
            f"\n{B}┌── REFERENCE "
            f"──────────────────────────────────────┐{W}"
        )

        print()

        print(
            f"{Y}smbclient -N //{M}<IP>{W}/{M}<SHARE>{W}"
        )

        print()

        print(
            f"{Y}smbclient //{M}<IP>{W}/{M}<SHARE>{W} "
            f"-U {M}<USER>%<PASS>{W}"
        )

        print()

        print(
            f"{Y}smbclient -k //{M}<IP>{W}/{M}<SHARE>{W}"
        )

        print(
            f"\n{B}└──────────────────────────────────────────────┘{W}\n"
        )

        return

    ip = data.get("ip")

    if not ip:

        print(
            f"\n{R}[!]{W} "
            f"No target IP loaded."
        )

        return

    # -----------------------------
    # SHARE
    # -----------------------------

    share = None

    if getattr(args, "extra", None):

        if args.extra:

            share = args.extra[0]

    # -----------------------------
    # MENU
    # -----------------------------

    if not share:

        print(
            f"\n{B}[{W}{G}*{W}{B}]{W} "
            f"Launching share enumeration...\n"
        )

        subprocess.run(
            "ctf smb.shares",
            shell=True
        )

        return

    # -----------------------------
    # AUTH
    # -----------------------------

    auth_label = "anonymous"

    creds = data.get(
        "creds",
        []
    )

    current_index = data.get(
        "current_cred"
    )

    cmd = (
        f"smbclient "
        f"-N "
        f"//{ip}/{share}"
    )

    if (
        current_index is not None
        and current_index < len(creds)
    ):

        current = creds[
            current_index
        ]

        user = current.get(
            "user"
        )

        cred_type = current.get(
            "type"
        )

        # -------------------------
        # PASSWORD
        # -------------------------

        if cred_type == "password":

            secret = current.get(
                "secret"
            )

            auth_label = (
                f"{user} (password)"
            )

            cmd = (
                f"smbclient "
                f"//{ip}/{share} "
                f"-U "
                f"'{user}%{secret}'"
            )

        # -------------------------
        # NTLM
        # -------------------------

        elif cred_type == "ntlm":

            secret = current.get(
                "secret"
            )

            auth_label = (
                f"{user} (ntlm)"
            )

            cmd = (
                f"smbclient "
                f"//{ip}/{share} "
                f"-U '{user}' "
                f"--pw-nt-hash"
            )

        # -------------------------
        # KERBEROS
        # -------------------------

        elif cred_type == "ticket":

            ccache = current.get(
                "ccache"
            )

            if ccache:

                os.environ[
                    "KRB5CCNAME"
                ] = ccache

                auth_label = (
                    f"{user} (kerberos)"
                )

                cmd = (
                    f"smbclient "
                    f"-k "
                    f"//{ip}/{share}"
                )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: SMB CONNECT "
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
        f"SHARE:  "
        f"{C}{share:<38}{W}"
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

    subprocess.run(
        cmd,
        shell=True
    )

    print()
