import subprocess

from urllib.parse import urlparse

from core.paths import (
    get_artifacts_dir
)

from core.target import (
    get_current_url
)


PROVIDES = []
REQUIRES = []


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

        print()

        print(
            f"{Y}whois "
            f"{M}<DOMAIN>{W}"
        )

        print()

        return

    # -----------------------------
    # URL
    # -----------------------------

    url = get_current_url(
        data
    )

    if not url:

        print(
            f"\n{R}[!]{W} "
            f"No URL selected."
        )

        return

    parsed = urlparse(
        url
    )

    domain = (
        parsed.hostname
        or url
    )

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
        / "web"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        artifact_dir
        / "whois.txt"
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: WHOIS "
        f"──────────────────────────────┐{W}"
    )

    print(
        f"{B}│{W} "
        f"DOMAIN: "
        f"{C}{domain:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└───────────────────────────────────────────────┘{W}"
    )

    # -----------------------------
    # WHOIS
    # -----------------------------

    cmd = (
        f"whois "
        f"'{domain}'"
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"WHOIS LOOKUP\n"
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

    output_file.write_text(
        output
    )

    print()

    print(
        f"{G}[+]{W} "
        f"Results saved:"
    )

    print(
        f"{C}{output_file}{W}"
    )

    print()
