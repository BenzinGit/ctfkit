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
            f"{Y}dig "
            f"-x "
            f"{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}host "
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
    # ARTIFACTS
    # -----------------------------

    artifact_dir = (
        get_artifacts_dir(
            target_name
        )
        / "dns"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    reverse_file = (
        artifact_dir
        / "reverse_lookup.txt"
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: DNS REVERSE LOOKUP "
        f"────────────────┐{W}"
    )

    print(
        f"{B}│{W} "
        f"IP: "
        f"{C}{ip:<42}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└───────────────────────────────────────────────┘{W}"
    )

    # -----------------------------
    # DIG
    # -----------------------------

    cmd = (
        f"dig "
        f"-x "
        f"{ip}"
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"REVERSE LOOKUP\n"
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

    reverse_file.write_text(
        output
    )

    # -----------------------------
    # HOST LOOKUP
    # -----------------------------

    cmd = (
        f"host "
        f"{ip}"
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"HOST LOOKUP\n"
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

    host_output = (
        result.stdout
        + result.stderr
    )

    print(
        host_output
    )

    with open(
        reverse_file,
        "a"
    ) as f:

        f.write(
            "\n\n"
            + "=" * 60
            + "\nHOST LOOKUP\n"
            + "=" * 60
            + "\n"
            + host_output
        )

    # -----------------------------
    # RESULTS
    # -----------------------------

    print(
        f"\n{G}[+]{W} "
        f"Results saved:"
    )

    print(
        f"{C}{reverse_file}{W}"
    )

    print()
