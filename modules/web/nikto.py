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
            f"{Y}nikto "
            f"-h {M}<URL>{W}"
        )

        print()

        print(
            f"{Y}nikto "
            f"-h {M}<URL>{W} "
            f"-Tuning b"
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
        / "nikto.txt"
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: NIKTO "
        f"──────────────────────────────┐{W}"
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
        f"nikto "
        f"-h '{url}' "
        f"-Tuning b"
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"SOFTWARE IDENTIFICATION\n"
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
        f"QUICK HINTS\n"
    )

    lower = output.lower()

    technologies = [

        "wordpress",
        "drupal",
        "joomla",
        "apache",
        "nginx",
        "iis",
        "php",
        "tomcat"

    ]

    found = False

    for tech in technologies:

        if tech in lower:

            found = True

            print(
                f"{G}[+]{W} "
                f"{tech.title()}"
            )

    if not found:

        print(
            f"{Y}[!]{W} "
            f"No obvious technologies identified."
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
