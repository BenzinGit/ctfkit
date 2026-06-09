import subprocess

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
            f"{Y}whatweb "
            f"{M}<URL>{W}"
        )

        print()

        print(
            f"{Y}whatweb "
            f"-a 3 "
            f"{M}<URL>{W}"
        )

        print()

        print(
            f"{Y}whatweb "
            f"--log-verbose=whatweb.txt "
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

    output_file = (
        artifact_dir
        / "whatweb.txt"
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: WHATWEB "
        f"────────────────────────────┐{W}"
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
    # SCAN
    # -----------------------------

    cmd = (
        f"whatweb "
        f"-a 3 "
        f"'{url}'"
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"TECHNOLOGY FINGERPRINTING\n"
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

    # -----------------------------
    # SAVE
    # -----------------------------

    output_file.write_text(
        output
    )

    # -----------------------------
    # QUICK HINTS
    # -----------------------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"COMMON FINDINGS\n"
    )

    hints = [

        ("WordPress", "wpscan"),
        ("Drupal", "droopescan"),
        ("Joomla", "joomscan"),
        ("Apache", "Check modules and versions"),
        ("Nginx", "Check reverse proxy behavior"),
        ("PHP", "Look for LFI/RFI/upload issues"),
        ("Tomcat", "Check manager interfaces"),
        ("IIS", "Check ASP.NET applications")

    ]

    lower = output.lower()

    found = False

    for keyword, hint in hints:

        if keyword.lower() in lower:

            found = True

            print(
                f"{C}{keyword:<15}{W}"
                f"{hint}"
            )

    if not found:

        print(
            f"{Y}No common technologies identified.{W}"
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
        f"{C}{output_file}{W}"
    )

    print()
