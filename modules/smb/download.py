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

    if reference:

        print(
            f"\n{B}┌── REFERENCE "
            f"──────────────────────────────────────┐{W}"
        )

        print()

        print(
            f"{Y}smbclient //{M}<IP>{W}/{M}<SHARE>{W} -N{W}"
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

        print()

        print(
            f"{Y}prompt OFF; recurse ON; mget *{W}"
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
            f"\n{R}[!]{W} No target IP loaded."
        )

        return

    target_name = data.get(
        "name",
        "unknown"
    )

    # -----------------------------
    # SHARE
    # -----------------------------

    share = None

    if getattr(
        args,
        "extra",
        None
    ):

        if args.extra:

            share = args.extra[0]

    if not share:

        print(
            f"\n{B}[{W}{G}*{W}{B}]{W} "
            f"No share specified."
        )

        print(
            f"{B}[{W}{G}*{W}{B}]{W} "
            f"Run:"
        )

        print(
            f"\n{Y}ctf smb.shares{W}\n"
        )

        return

    share = (
        share
        .replace("/", "_")
        .replace("\\", "_")
    )

    # -----------------------------
    # LOOT DIR
    # -----------------------------

    loot_dir = (
        Path("artifacts")
        / target_name
        / "smb"
        / share
    )

    loot_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------
    # AUTH
    # -----------------------------

    auth_label = "anonymous"
    auth = "-N"

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

            auth = (
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

            auth = (
                f"-U '{user}' "
                f"--pw-nt-hash"
            )

            print(
                f"\n{Y}[!]{W} "
                f"NTLM authentication "
                f"may not work on all smbclient versions."
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

                auth = "-k"

    # -----------------------------
    # SMB COMMANDS
    # -----------------------------

    smb_cmd = (
        f"prompt OFF;"
        f"recurse ON;"
        f"lcd {loot_dir};"
        f"mget *"
    )

    cmd = (
        f"smbclient "
        f"//{ip}/{share} "
        f"{auth} "
        f"-c "
        f"'{smb_cmd}'"
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: SMB DOWNLOAD "
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

    # -----------------------------
    # INFO
    # -----------------------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"DESTINATION\n"
    )

    print(
        f"{C}{loot_dir}{W}"
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"COMMAND\n"
    )

    print(
        f"{Y}{cmd}{W}\n"
    )

    # -----------------------------
    # EXECUTE
    # -----------------------------

    try:

        subprocess.run(
            cmd,
            shell=True
        )

        print(
            f"\n{G}[+]{W} "
            f"Download completed."
        )

        print(
            f"{G}[+]{W} "
            f"Saved to: "
            f"{C}{loot_dir}{W}"
        )

    except KeyboardInterrupt:

        print(
            f"\n{R}[!]{W} "
            f"Download interrupted."
        )

    print()
