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
            f"{Y}lftp -u anonymous,anonymous ftp://{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}lftp -u {M}<USER>{W},{M}<PASS>{W} ftp://{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}ls{W}"
        )

        print()

        print(
            f"{Y}find{W}"
        )

        print()

        print(
            f"{Y}mirror .{W}"
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
    # AUTH
    # -----------------------------

    if cred:

        user = cred.get("user")
        secret = cred.get("secret")

        if user and secret:

            auth_type = user

            cmd = (
                f"lftp -u "
                f"{user},{secret} "
                f"ftp://{ip}"
            )

        else:

            auth_type = "anonymous"

            cmd = (
                f"lftp -u "
                f"anonymous,anonymous "
                f"ftp://{ip}"
            )

    else:

        auth_type = "anonymous"

        cmd = (
            f"lftp -u "
            f"anonymous,anonymous "
            f"ftp://{ip}"
        )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: FTP CONNECT "
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
        f"{C}{auth_type:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└───────────────────────────────────────────────┘{W}"
    )

    # -----------------------------
    # COMMAND
    # -----------------------------

    print(
        f"\n{B}[*]{W} COMMAND\n"
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
