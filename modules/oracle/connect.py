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
            f"{Y}sqlplus "
            f"{M}<USER>{W}/{M}<PASS>{W}@{M}<IP>{W}/{M}<SID>{W}"
        )

        print()

        print(
            f"{Y}sqlplus "
            f"{M}<USER>{W}/{M}<PASS>{W}@{M}<IP>{W}/{M}<SID>{W} "
            f"as sysdba{W}"
        )

        print()

        print(
            f"{Y}select table_name "
            f"from all_tables;{W}"
        )

        print()

        print(
            f"{Y}select username "
            f"from all_users;{W}"
        )

        print()

        print(
            f"{Y}select * "
            f"from user_role_privs;{W}"
        )

        print()

        print(
            f"{Y}select name,password "
            f"from sys.user$;{W}"
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
    # CREDENTIAL
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

        return

    current = creds[
        current_index
    ]

    if current.get(
        "type"
    ) != "password":

        print(
            f"\n{R}[!]{W} "
            f"Oracle requires a password credential."
        )

        return

    user = current.get(
        "user"
    )

    password = current.get(
        "secret"
    )

    # -----------------------------
    # SID
    # -----------------------------

    sid = input(
        "\nSID [XE]: "
    ).strip()

    if not sid:

        sid = "XE"

    # -----------------------------
    # SYSDBA
    # -----------------------------

    sysdba = input(
        "\nConnect as SYSDBA? [y/N]: "
    ).strip().lower()

    cmd = (
        f"sqlplus "
        f"{user}/{password}"
        f"@{ip}/{sid}"
    )

    if sysdba == "y":

        cmd += (
            " as sysdba"
        )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: ORACLE CONNECT "
        f"─────────────────────┐{W}"
    )

    print(
        f"{B}│{W} "
        f"TARGET: "
        f"{C}{ip:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W} "
        f"USER:   "
        f"{C}{user:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W} "
        f"SID:    "
        f"{C}{sid:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└───────────────────────────────────────────────┘{W}"
    )

    # -----------------------------
    # CHEATSHEET
    # -----------------------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"COMMON QUERIES\n"
    )

    print(
        f"{Y}select table_name from all_tables;{W}"
    )

    print()

    print(
        f"{Y}select username from all_users;{W}"
    )

    print()

    print(
        f"{Y}select * from user_role_privs;{W}"
    )

    print()

    print(
        f"{Y}select name,password from sys.user$;{W}"
    )

    print()

    print(
        f"{B}[{W}{G}*{W}{B}]{W} "
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
