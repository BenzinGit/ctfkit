import subprocess

from core.paths import get_artifacts_dir


PROVIDES = []
REQUIRES = ["ip"]


PORT_SCRIPTS = {

    "21": "ftp*",
    "22": "ssh*",
    "25": "smtp*",
    "53": "dns*",
    "80": "http*",
    "110": "pop3*",
    "111": "rpc*",
    "139": "smb*",
    "143": "imap*",
    "443": "http*",
    "445": "smb*",
    "1433": "ms-sql*",
    "1521": "oracle*",
    "2049": "nfs*",
    "3306": "mysql*",
    "3389": "rdp*",
    "5432": "pgsql*",
    "5985": "http*",
    "5986": "http*",
    "6379": "redis*",
    "8080": "http*",
    "8443": "http*"
}


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
            f"{Y}nmap -A -p {M}<PORT>{W} {M}<IP>{W}"
        )

        print()

        print(
            f"{Y}nmap -sC -sV -A -p 445 --script smb* {M}<IP>{W}"
        )

        print()

        print(
            f"{Y}nmap -sC -sV -A -p 53 --script dns* {M}<IP>{W}"
        )

        print()

        print(
            f"{Y}nmap -sC -sV -A -p 1433 --script ms-sql* {M}<IP>{W}"
        )

        print()

        print(
            f"{Y}nmap -sC -sV -A -p 3306 --script mysql* {M}<IP>{W}"
        )

        print()

        print(
            f"{Y}nmap -sC -sV -A -p 2049 --script nfs* {M}<IP>{W}"
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

    target_name = data.get("name")

    if not target_name:

        target_name = "unknown"

    # -----------------------------
    # PORT
    # -----------------------------

    port = None

    if getattr(args, "extra", None):

        if args.extra:

            port = args.extra[0]

    while not port:

        port = input(
            "\nPort: "
        ).strip()

    # -----------------------------
    # NSE
    # -----------------------------

    script = PORT_SCRIPTS.get(
        str(port)
    )

    # -----------------------------
    # ARTIFACTS
    # -----------------------------

    nmap_dir = (
        get_artifacts_dir(target_name)
        / "nmap"
    )

    nmap_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        nmap_dir /
        f"port-{port}.txt"
    )

    # -----------------------------
    # COMMAND
    # -----------------------------

    cmd = (
        f"nmap "
        f"-sC "
        f"-sV "
        f"-A "
        f"-p {port} "
    )

    if script:

        cmd += (
            f"--script {script} "
        )

    cmd += ip

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: PORT ENUMERATION "
        f"──────────────────┐{W}"
    )

    print(
        f"{B}│{W} "
        f"TARGET: "
        f"{C}{ip:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W} "
        f"PORT:   "
        f"{C}{port:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W} "
        f"SCRIPT: "
        f"{C}{script or 'none':<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└───────────────────────────────────────────────┘{W}"
    )

    # -----------------------------
    # COMMAND DISPLAY
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

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    output_file.write_text(
        result.stdout
    )

    # -----------------------------
    # RESULTS
    # -----------------------------

    if result.returncode != 0:

        print(
            f"{R}[!]{W} Scan failed."
        )

        if result.stderr:

            print(
                f"\n{R}{result.stderr}{W}"
            )

        return

    print(
        f"{G}[+]{W} Scan completed."
    )

    print(
        f"{G}[+]{W} Saved: "
        f"{C}{output_file}{W}"
    )

    print()

    print(
        result.stdout
    )
