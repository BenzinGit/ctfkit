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
    # REFERENCE MODE
    # -----------------------------

    if reference:

        print(
            f"\n{B}┌── REFERENCE "
            f"──────────────────────────────────────┐{W}"
        )

        print()

        print(
            f"{Y}nmap -F {M}<IP>{W}"
        )

        print()

        print(
            f"{Y}nmap -F {M}<HOSTNAME>{W}"
        )

        print()

        print(
            f"{Y}nmap -F {M}<SUBNET>{W}"
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
    # ARTIFACTS
    # -----------------------------


    target_name = data.get("name")


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
        "fast.txt"
    )

    # -----------------------------
    # COMMAND
    # -----------------------------

    cmd = (
        f"nmap -F {ip}"
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: NMAP FAST "
        f"──────────────────────────┐{W}"
    )

    print(
        f"{B}│{W} "
        f"TARGET: "
        f"{C}{ip:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W} "
        f"OUTPUT: "
        f"{C}{'fast.txt':<38}{W}"
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
