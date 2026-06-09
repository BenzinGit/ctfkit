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
            f"{Y}dig {M}<DOMAIN>{W} A{W}"
        )

        print()

        print(
            f"{Y}dig {M}<DOMAIN>{W} AAAA{W}"
        )

        print()

        print(
            f"{Y}dig {M}<DOMAIN>{W} MX{W}"
        )

        print()

        print(
            f"{Y}dig {M}<DOMAIN>{W} NS{W}"
        )

        print()

        print(
            f"{Y}dig {M}<DOMAIN>{W} TXT{W}"
        )

        print()

        print(
            f"{Y}dig {M}<DOMAIN>{W} SOA{W}"
        )

        print()

        print(
            f"{Y}dig {M}<DOMAIN>{W} CNAME{W}"
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

    records_file = (
        artifact_dir
        / "records.txt"
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: DNS RECORD ENUMERATION "
        f"───────────────┐{W}"
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
    # RECORD TYPES
    # -----------------------------

    record_types = [

        "A",
        "AAAA",
        "MX",
        "NS",
        "TXT",
        "SOA",
        "CNAME"

    ]

    all_output = ""

    # -----------------------------
    # ENUMERATION
    # -----------------------------

    for record in record_types:

        print(
            f"\n{B}[{W}{G}*{W}{B}]{W} "
            f"{record} RECORDS\n"
        )

        cmd = (
            f"dig "
            f"{domain} "
            f"{record} "
            f"+noall +answer"
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
            result.stdout.strip()
        )

        if not output:

            output = (
                "[No records found]"
            )

        print(
            output
        )

        print()

        all_output += (

            f"\n"
            f"{'=' * 60}\n"
            f"{record}\n"
            f"{'=' * 60}\n"
            f"{output}\n"

        )

    # -----------------------------
    # SAVE
    # -----------------------------

    records_file.write_text(
        all_output
    )

    # -----------------------------
    # QUICK NOTES
    # -----------------------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"QUICK NOTES\n"
    )

    print(
        f"{C}A{W}      IPv4 addresses"
    )

    print(
        f"{C}AAAA{W}   IPv6 addresses"
    )

    print(
        f"{C}MX{W}     Mail servers"
    )

    print(
        f"{C}NS{W}     Name servers"
    )

    print(
        f"{C}TXT{W}    SPF / DMARC / Verification records"
    )

    print(
        f"{C}SOA{W}    Zone authority information"
    )

    print(
        f"{C}CNAME{W}  Aliases"
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
        f"{C}{records_file}{W}"
    )

    print()
