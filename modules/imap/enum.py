import subprocess
from pathlib import Path
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
            f"{Y}nmap -sV -sC "
            f"-p143,993 "
            f"{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}openssl s_client "
            f"-connect "
            f"{M}<IP>{W}:993"
        )

        print()

        print(
            f"{Y}curl -k "
            f"'imaps://{M}<IP>{W}' "
            f"--user "
            f"{M}<USER>{W}:{M}<PASS>{W}"
        )

        print()

        print(
            f"{Y}nc {M}<IP>{W} 143"
        )

        print()

        print(
            f"{Y}A001 CAPABILITY{W}"
        )

        print()

        print(
            f"{Y}A002 LOGOUT{W}"
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

    target_name = data.get(
        "name",
        "unknown"
    )

    # -----------------------------
    # ARTIFACTS
    # -----------------------------

    artifact_dir = (
        get_artifacts_dir(target_name)
        / "imap"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: IMAP ENUMERATION "
        f"───────────────────┐{W}"
    )

    print(
        f"{B}│{W} "
        f"TARGET: "
        f"{C}{ip:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└───────────────────────────────────────────────┘{W}"
    )

    commands = [

        (
            "SERVICE DETECTION",
            f"nmap -sV -sC "
            f"-p143,993 "
            f"{ip}"
        ),

        (
            "IMAP CAPABILITIES",
            f"nmap "
            f"--script imap-capabilities "
            f"-p143,993 "
            f"{ip}"
        ),

        (
            "TLS CERTIFICATE",
            f"timeout 10 "
            f"openssl s_client "
            f"-connect {ip}:993"
        ),

        (
            "BANNER GRAB",
            f"timeout 5 bash -c "
            f"'echo A001 CAPABILITY | nc {ip} 143'"
        )

    ]

    # -----------------------------
    # EXECUTE
    # -----------------------------

    for title, cmd in commands:

        print(
            f"\n{B}[{W}{G}*{W}{B}]{W} "
            f"{title}\n"
        )

        print(
            f"{Y}{cmd}{W}\n"
        )

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )

        print(
            result.stdout
        )

        outfile = (
            artifact_dir
            / f"{title.lower().replace(' ', '_')}.txt"
        )

        outfile.write_text(
            result.stdout
        )

    # -----------------------------
    # RESULTS
    # -----------------------------

    print(
        f"\n{G}[+]{W} "
        f"Saved results:"
    )

    print(
        f"{C}{artifact_dir}{W}"
    )

    print()
