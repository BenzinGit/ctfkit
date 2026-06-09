import re
import subprocess

from core.paths import (
    get_artifacts_dir
)


PROVIDES = []
REQUIRES = ["domain"]


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
            f"{M}<DOMAIN>{W} "
            f"NS"
        )

        print()

        print(
            f"{Y}dig "
            f"axfr "
            f"@{M}<NS_SERVER>{W} "
            f"{M}<DOMAIN>{W}"
        )

        print(
            f"\n{B}└──────────────────────────────────────────────┘{W}\n"
        )

        return

    # -----------------------------
    # DOMAIN
    # -----------------------------

    domain = data.get(
        "domain"
    )

    if not domain:

        print(
            f"\n{R}[!]{W} "
            f"No domain loaded."
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

    zone_file = (
        artifact_dir
        / "zone_transfer.txt"
    )

    hosts_file = (
        artifact_dir
        / "hosts.txt"
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: DNS ZONE TRANSFER "
        f"──────────────────┐{W}"
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
    # GET NAMESERVERS
    # -----------------------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"DISCOVERING NAMESERVERS\n"
    )

    cmd = (
        f"dig "
        f"{domain} "
        f"NS "
        f"+short"
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

    ns_servers = [

        line.strip().rstrip(".")

        for line in result.stdout.splitlines()

        if line.strip()

    ]

    if not ns_servers:

        print(
            f"{R}[!]{W} "
            f"No nameservers found."
        )

        return

    for ns in ns_servers:

        print(
            f"{C}{ns}{W}"
        )

    print()

    # -----------------------------
    # AXFR ATTEMPTS
    # -----------------------------

    successful = False
    all_output = ""
    discovered = set()

    for ns in ns_servers:

        print(
            f"\n{B}[{W}{G}*{W}{B}]{W} "
            f"AXFR: {ns}\n"
        )

        cmd = (
            f"dig "
            f"axfr "
            f"@{ns} "
            f"{domain}"
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

        all_output += (
            f"\n"
            f"{'=' * 60}\n"
            f"{ns}\n"
            f"{'=' * 60}\n"
            f"{output}\n"
        )

        # crude success detection

        if (
            "Transfer failed"
            not in output
            and "XFR size"
            in output
        ):

            successful = True

            for line in output.splitlines():

                if domain in line:

                    host = (
                        line.split()[0]
                        .rstrip(".")
                    )

                    discovered.add(
                        host
                    )

    # -----------------------------
    # SAVE
    # -----------------------------

    zone_file.write_text(
        all_output
    )

    hosts_file.write_text(
        "\n".join(
            sorted(discovered)
        )
    )

    # -----------------------------
    # RESULTS
    # -----------------------------

    if successful:

        print(
            f"\n{G}[+]{W} "
            f"Zone transfer successful."
        )

        if discovered:

            print(
                f"\n{B}[{W}{G}*{W}{B}]{W} "
                f"DISCOVERED HOSTS\n"
            )

            for host in sorted(
                discovered
            ):

                print(
                    f"{C}{host}{W}"
                )

    else:

        print(
            f"\n{Y}[!]{W} "
            f"No zone transfers allowed."
        )

    print()

    print(
        f"{G}[+]{W} "
        f"Results saved:"
    )

    print(
        f"{C}{zone_file}{W}"
    )

    print(
        f"{C}{hosts_file}{W}"
    )

    print()
