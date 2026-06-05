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
            f"{Y}nxc smb {M}<IP>{W} --shares"
        )

        print()

        print(
            f"{Y}nxc smb {M}<IP>{W} -u {M}<USER>{W} -p {M}<PASS>{W} --shares"
        )

        print()

        print(
            f"{Y}nxc smb {M}<IP>{W} -u {M}<USER>{W} -H {M}<NTLM>{W} --shares"
        )

        print()

        print(
            f"{Y}KRB5CCNAME={M}<CCACHE>{W} nxc smb {M}<IP>{W} -k --shares"
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

    # -----------------------------
    # AUTH
    # -----------------------------

    auth_label = "anonymous"
    cmd = f"nxc smb {ip} -u '' -p '' --shares"
    
    creds = data.get("creds", [])
    current_index = data.get("current_cred")

    if (
        current_index is not None
        and current_index < len(creds)
    ):
        
        current = creds[current_index]

        user = current.get("user")
        cred_type = current.get("type")

        if cred_type == "password":
            print("aa")
            secret = current.get("secret")

            auth_label = (
                f"{user} (password)"
            )

            cmd = (
                f'nxc smb {ip} '
                f'-u "{user}" '
                f'-p "{secret}" '
                f'--shares'
            )

        elif cred_type == "ntlm":

            secret = current.get("secret")

            auth_label = (
                f"{user} (ntlm)"
            )

            cmd = (
                f'nxc smb {ip} '
                f'-u "{user}" '
                f'-H "{secret}" '
                f'--shares'
            )

        elif cred_type == "ticket":

            ccache = current.get("ccache")

            if ccache:

                os.environ[
                    "KRB5CCNAME"
                ] = ccache

                auth_label = (
                    f"{user} (kerberos)"
                )

                cmd = (
                    f'nxc smb {ip} '
                    f'-k '
                    f'--shares'
                )
      
    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: SMB SHARES "
        f"─────────────────────────┐{W}"
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

    # -----------------------------
    # COMMAND
    # -----------------------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"SHARE ENUMERATION\n"
    )

    print(
        f"{Y}{cmd}{W}\n"
    )

    # -----------------------------
    # EXECUTE
    # -----------------------------


    # -----------------------------
    # PARSE SHARES
    # -----------------------------

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    shares = []

    in_share_table = False

    for line in result.stdout.splitlines():

        if "Share" in line and "Permissions" in line:
            in_share_table = True
            continue

        if not in_share_table:
            continue

        if "-----" in line:
            continue

        if not line.strip():
            continue

        if "SMB" not in line:
            continue

        parts = line.split()

        if len(parts) < 6:
            continue

        share = parts[4]

        if share not in shares:
            shares.append(share)

    

    # -----------------------------
    # GUEST WARNING
    # -----------------------------

    if "Guest" in result.stdout:

        print(
            f"\n{R}[!]{W} "
            f"Authenticated as "
            f"{Y}Guest{W}"
        )

    # -----------------------------
    # SHARE MENU
    # -----------------------------

    if shares:

        print(
            f"\n{B}[{W}{G}*{W}{B}]{W} "
            f"CONNECT TO SHARE\n"
        )

        for i, share in enumerate(
            shares,
            start=1
        ):

             print(
                f"{B}[{W}{Y}{i}{W}{B}]{W} "
                f"{C}{share}{W}"
            )


        print(
            f"{B}[{W}{R}0{W}{B}]{W} "
            f"{W}No"
        )

        choice = input(
            "\n> "
        ).strip()

        if (
            choice.isdigit()
            and int(choice) > 0
            and int(choice) <= len(shares)
        ):

            share = shares[
                int(choice) - 1
            ]

            print(
                f"\n{G}[+]{W} "
                f"Selected: "
                f"{C}{share}{W}"
            )

            subprocess.run(
                f"ctf smb.connect {share}",
                shell=True
            )
