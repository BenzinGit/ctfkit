import subprocess

from core.paths import get_artifacts_dir


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
            f"{Y}nmap -sV -sC -A -p 21 {M}<IP>{W}"
        )

        print()

        print(
            f"{Y}nmap -p 21 --script ftp-anon {M}<IP>{W}"
        )

        print()

        print(
            f"{Y}nmap -p 21 --script ftp* {M}<IP>{W}"
        )

        print()

        print(
            f"{Y}nc {M}<IP>{W} 21"
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

    target_name = data.get("name")

    if not target_name:

        target_name = "unknown"

    # -----------------------------
    # ARTIFACTS
    # -----------------------------

    ftp_dir = (
        get_artifacts_dir(target_name)
        / "ftp"
    )

    ftp_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        ftp_dir /
        "enum.txt"
    )

    # -----------------------------
    # COMMAND
    # -----------------------------

    cmd = (
        f"nmap "
        f"-sV "
        f"-sC "
        f"-A "
        f"-p 21 "
        f"{ip}"
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: FTP ENUMERATION "
        f"────────────────────┐{W}"
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
        f"{C}{'21':<38}{W}"
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

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    output_file.write_text(
        result.stdout
    )

    banner = subprocess.run(
        f"nc {ip} 21",
        shell=True,
        capture_output=True,
        text=True
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
        f"{G}[+]{W} Enumeration completed."
    )

    print(
        f"{G}[+]{W} Saved: "
        f"{C}{output_file}{W}"
    )

    print()

    print(
        result.stdout
        
    )
    print()
    print(banner)
