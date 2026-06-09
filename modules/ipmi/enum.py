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
            f"-sU "
            f"--script ipmi-version "
            f"-p623 "
            f"{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}msfconsole{W}"
        )

        print()

        print(
            f"{Y}use auxiliary/scanner/ipmi/ipmi_version{W}"
        )

        print()

        print(
            f"{Y}set rhosts {M}<IP>{W}"
        )

        print()

        print(
            f"{Y}run{W}"
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
        / "ipmi"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: IPMI ENUMERATION "
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

    # -----------------------------
    # COMMANDS
    # -----------------------------

    commands = [

        (
            "IPMI VERSION",

            (
                f"nmap "
                f"-sU "
                f"--script ipmi-version "
                f"-p623 "
                f"{ip}"
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
    # DEFAULT CREDS
    # -----------------------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"COMMON DEFAULT CREDENTIALS\n"
    )

    print(
        f"{C}Dell iDRAC{W}"
    )

    print(
        f"  root:calvin\n"
    )

    print(
        f"{C}Supermicro IPMI{W}"
    )

    print(
        f"  ADMIN:ADMIN\n"
    )

    print(
        f"{C}HP iLO{W}"
    )

    print(
        f"  Administrator:<factory password>\n"
    )

    print(
        f"{G}[+]{W} "
        f"Results saved:"
    )

    print(
        f"{C}{artifact_dir}{W}"
    )

    print()
