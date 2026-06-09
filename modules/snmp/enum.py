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
            f"{Y}nmap -sU "
            f"-p161,162 "
            f"{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}onesixtyone "
            f"-c "
            f"/usr/share/seclists/Discovery/SNMP/snmp.txt "
            f"{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}snmpwalk "
            f"-v2c "
            f"-c public "
            f"{M}<IP>{W}"
        )

        print(
            f"\n{B}└──────────────────────────────────────────────┘{W}\n"
        )

        return

    # -----------------------------
    # TARGET
    # -----------------------------

    ip = data.get("ip")

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
        / "snmp"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: SNMP ENUMERATION "
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

    commands = [

        (
            "SERVICE DETECTION",
            (
                f"nmap -sU "
                f"-p161,162 "
                f"{ip}"
            )
        ),

        (
            "COMMUNITY ENUMERATION",
            (
                f"onesixtyone "
                f"-c "
                f"/usr/share/seclists/Discovery/SNMP/snmp.txt "
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
    # PARSE COMMUNITIES
    # -----------------------------

    communities = set()

    community_file = (
        artifact_dir
        / "community_enumeration.txt"
    )

    if community_file.exists():

        for line in (
            community_file
            .read_text()
            .splitlines()
        ):

            if "[" not in line:
                continue

            if "]" not in line:
                continue

            try:

                community = (
                    line
                    .split("[", 1)[1]
                    .split("]", 1)[0]
                    .strip()
                )

                if community:

                    communities.add(
                        community
                    )

            except:

                pass

    communities = sorted(
        communities
    )

    community_out = (
        artifact_dir
        / "communities.txt"
    )

    community_out.write_text(
        "\n".join(
            communities
        )
    )

    # -----------------------------
    # RESULTS
    # -----------------------------

    print()

    if communities:

        print(
            f"{G}[+]{W} "
            f"Discovered communities:\n"
        )

        for community in communities:

            print(
                f"{C}{community}{W}"
            )

        print()

        print(
            f"{G}[+]{W} "
            f"Saved:"
        )

        print(
            f"{C}{community_out}{W}"
        )

    else:

        print(
            f"{R}[!]{W} "
            f"No communities found."
        )

    print()

    print(
        f"{G}[+]{W} "
        f"Artifacts:"
    )

    print(
        f"{C}{artifact_dir}{W}"
    )

    print()
