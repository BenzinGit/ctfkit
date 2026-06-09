import subprocess

from core.paths import (
    get_artifacts_dir
)


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
            f"-p110,995 "
            f"{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}openssl s_client "
            f"-connect "
            f"{M}<IP>{W}:995"
        )

        print()

        print(
            f"{Y}nc {M}<IP>{W} 110{W}"
        )

        print()

        print(
            f"{Y}USER {M}<USER>{W}"
        )

        print()

        print(
            f"{Y}PASS {M}<PASS>{W}"
        )

        print()

        print(
            f"{Y}STAT{W}"
        )

        print()

        print(
            f"{Y}LIST{W}"
        )

        print()

        print(
            f"{Y}RETR 1{W}"
        )

        print()

        print(
            f"{Y}QUIT{W}"
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
        get_artifacts_dir(
            target_name
        )
        / "pop3"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: POP3 ENUMERATION "
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
            (
                f"nmap -sV -sC "
                f"-p110,995 "
                f"{ip}"
            )
        ),

        (
            "TLS CERTIFICATE",
            (
                f"timeout 10 "
                f"openssl s_client "
                f"-connect {ip}:995"
            )
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

        output = (
            result.stdout
            + result.stderr
        )

        print(
            output
        )

        outfile = (
            artifact_dir
            / (
                title
                .lower()
                .replace(
                    " ",
                    "_"
                )
                + ".txt"
            )
        )

        outfile.write_text(
            output
        )

    # -----------------------------
    # RESULTS
    # -----------------------------

    print()

    print(
        f"{G}[+]{W} "
        f"Results saved:"
    )

    print(
        f"{C}{artifact_dir}{W}"
    )

    print()
