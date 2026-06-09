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
            f"{Y}nmap "
            f"-sV -sC "
            f"-p5985,5986 "
            f"--disable-arp-ping "
            f"-n "
            f"{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}curl -I "
            f"http://{M}<IP>{W}:5985/wsman"
        )

        print()

        print(
            f"{Y}curl -k -I "
            f"https://{M}<IP>{W}:5986/wsman"
        )

        print()

        print(
            f"{Y}evil-winrm "
            f"-i {M}<IP>{W} "
            f"-u {M}<USER>{W} "
            f"-p {M}<PASS>{W}"
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
        / "winrm"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: WINRM ENUMERATION "
        f"──────────────────┐{W}"
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
                f"nmap "
                f"-sV -sC "
                f"-p5985,5986 "
                f"--disable-arp-ping "
                f"-n "
                f"{ip}"
            ),

            (
                artifact_dir
                / "service_detection.txt"
            )
        ),

        (
            "HTTP WSMAN",

            (
                f"curl -I "
                f"http://{ip}:5985/wsman"
            ),

            (
                artifact_dir
                / "http.txt"
            )
        ),

        (
            "HTTPS WSMAN",

            (
                f"curl -k -I "
                f"https://{ip}:5986/wsman"
            ),

            (
                artifact_dir
                / "https.txt"
            )
        )

    ]

    # -----------------------------
    # EXECUTE
    # -----------------------------

    for title, cmd, outfile in commands:

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

        outfile.write_text(
            output
        )

    # -----------------------------
    # NEXT STEPS
    # -----------------------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"NEXT STEPS\n"
    )

    print(
        f"{Y}evilwi{W}"
    )

    print()

    # -----------------------------
    # RESULTS
    # -----------------------------

    print(
        f"{G}[+]{W} "
        f"Results saved:"
    )

    print(
        f"{C}{artifact_dir}{W}"
    )

    print()
