import re
import subprocess

from core.paths import (
    get_artifacts_dir,
    get_tool_path
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
            f"-sV "
            f"-p22 "
            f"{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}ssh "
            f"-v "
            f"-o PreferredAuthentications=password "
            f"-o PubkeyAuthentication=no "
            f"{M}<USER>{W}@{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}python3 "
            f"tools/ssh-audit/ssh-audit.py "
            f"{M}<IP>{W}"
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
    # SSH AUDIT
    # -----------------------------

    ssh_audit = get_tool_path(
        "ssh-audit/ssh-audit.py"
    )

    if not ssh_audit.exists():

        print(
            f"\n{Y}[!]{W} "
            f"ssh-audit.py not found:"
        )

        print(
            f"{C}{ssh_audit}{W}\n"
        )

        return

    # -----------------------------
    # ARTIFACTS
    # -----------------------------

    artifact_dir = (
        get_artifacts_dir(
            target_name
        )
        / "ssh"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: SSH ENUMERATION "
        f"────────────────────┐{W}"
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
            "SERVICE DETECTION",

            (
                f"nmap "
                f"-sV "
                f"-p22 "
                f"{ip}"
            ),

            (
                artifact_dir
                / "service_detection.txt"
            )
        ),

        (
            "AUTHENTICATION METHODS",

            (
                f"timeout 5 "
                f"ssh "
                f"-v "
                f"-o PreferredAuthentications=password "
                f"-o PubkeyAuthentication=no "
                f"-o StrictHostKeyChecking=no "
                f"fakeuser@{ip}"
            ),

            (
                artifact_dir
                / "authentication.txt"
            )
        ),

        (
            "SSH AUDIT",

            (
                f"python3 "
                f"{ssh_audit} "
                f"{ip}"
            ),

            (
                artifact_dir
                / "audit.txt"
            )
        )

    ]

    auth_output = ""
    audit_output = ""

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

        if title == "AUTHENTICATION METHODS":

            auth_output = output

        elif title == "SSH AUDIT":

            audit_output = output

    # -----------------------------
    # SUMMARY
    # -----------------------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"SUMMARY\n"
    )

    # VERSION

    version_match = re.search(
        r"SSH-2\.0-([^\s]+)",
        audit_output
    )

    if version_match:

        print(
            f"{G}[+]{W} "
            f"Version:"
        )

        print(
            f"    {C}{version_match.group(1)}{W}"
        )

        print()

    # AUTH METHODS

    auth_match = re.search(
        r"Authentications that can continue:\s*(.+)",
        auth_output
    )

    if auth_match:

        methods = [

            x.strip()

            for x in auth_match
            .group(1)
            .split(",")
        ]

        print(
            f"{G}[+]{W} "
            f"Authentication Methods:"
        )

        print()

        for method in methods:

            print(
                f"    {C}{method}{W}"
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
