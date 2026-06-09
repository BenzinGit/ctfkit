import subprocess
import re

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

        print(
            f"\n{B}┌── REFERENCE "
            f"──────────────────────────────────────┐{W}"
        )

        print()

        print(
            f"{Y}curl -I "
            f"{M}<URL>{W}"
        )

        print()

        print(
            f"{Y}curl -k -I "
            f"https://{M}<HOST>{W}"
        )

        print()

        print(
            f"{Y}curl -IL "
            f"{M}<URL>{W}"
        )

        print(
            f"\n{B}└──────────────────────────────────────────────┘{W}\n"
        )

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

    headers_file = (
        artifact_dir
        / "headers.txt"
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: WEB HEADERS "
        f"────────────────────────┐{W}"
    )

    print(
        f"{B}│{W} "
        f"URL: "
        f"{C}{url:<41}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└───────────────────────────────────────────────┘{W}"
    )

    # -----------------------------
    # FOLLOW REDIRECTS
    # -----------------------------

    current_url = url
    visited = []

    all_output = ""

    for i in range(5):

        print(
            f"\n{B}[{W}{G}*{W}{B}]{W} "
            f"HEADERS ({i + 1})\n"
        )

        cmd = (
            f"curl -k -I "
            f"'{current_url}'"
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

        visited.append(
            current_url
        )

        all_output += (
            f"\n"
            f"{'=' * 60}\n"
            f"{current_url}\n"
            f"{'=' * 60}\n"
            f"{output}\n"
        )

        location = None

        for line in output.splitlines():

            if line.lower().startswith(
                "location:"
            ):

                location = (
                    line.split(
                        ":",
                        1
                    )[1]
                    .strip()
                )

                break

        if not location:

            break

        if location in visited:

            break

        current_url = location

    # -----------------------------
    # SAVE
    # -----------------------------

    headers_file.write_text(
        all_output
    )

    # -----------------------------
    # SUMMARY
    # -----------------------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"FINGERPRINTS\n"
    )

    findings = set()

    patterns = [

        (
            r"^Server:\s*(.+)",
            "Server"
        ),

        (
            r"^X-Powered-By:\s*(.+)",
            "X-Powered-By"
        ),

        (
            r"^X-Redirect-By:\s*(.+)",
            "X-Redirect-By"
        ),

        (
            r"^Link:\s*(.+)",
            "Link"
        )

    ]

    for line in all_output.splitlines():

        for regex, label in patterns:

            match = re.search(
                regex,
                line,
                re.I
            )

            if match:

                findings.add(
                    (
                        label,
                        match.group(1)
                    )
                )

    if findings:

        for label, value in sorted(
            findings
        ):

            print(
                f"{C}{label:<15}{W}"
                f"{value}"
            )

    else:

        print(
            f"{Y}No notable headers found.{W}"
        )

    # -----------------------------
    # WORDPRESS HINTS
    # -----------------------------

    wordpress = False

    indicators = [

        "wordpress",
        "wp-json",
        "wp-content",
        "wp-login",
        "x-redirect-by: wordpress"

    ]

    lower = all_output.lower()

    for indicator in indicators:

        if indicator in lower:

            wordpress = True
            break

    if wordpress:

        print()

        print(
            f"{G}[+]{W} "
            f"WordPress indicators detected."
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
        f"{C}{headers_file}{W}"
    )

    print()
