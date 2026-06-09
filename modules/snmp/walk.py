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
            f"{Y}snmpwalk "
            f"-v2c "
            f"-c public "
            f"{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}snmpwalk "
            f"-v1 "
            f"-c public "
            f"{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}braa "
            f"public@{M}<IP>{W}:.1.3.6.*"
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
        / "snmp"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------
    # COMMUNITY
    # -----------------------------

    community_file = (
        artifact_dir
        / "communities.txt"
    )

    community = None

    if community_file.exists():

        communities = [

            x.strip()

            for x in
            community_file
            .read_text()
            .splitlines()

            if x.strip()
        ]

        if len(
            communities
        ) == 1:

            community = (
                communities[0]
            )

        elif len(
            communities
        ) > 1:

            print(
                f"\n{B}[{W}{G}*{W}{B}]{W} "
                f"COMMUNITIES\n"
            )

            for i, c in enumerate(
                communities,
                1
            ):

                print(
                    f"{C}[{i}]{W} "
                    f"{c}"
                )

            print()

            choice = input(
                "> "
            ).strip()

            try:

                community = (
                    communities[
                        int(choice) - 1
                    ]
                )

            except:

                return

    if not community:

        community = input(
            "\nCommunity: "
        ).strip()

    if not community:

        print(
            f"\n{R}[!]{W} "
            f"Community required."
        )

        return

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: SNMP WALK "
        f"──────────────────────────┐{W}"
    )

    print(
        f"{B}│{W} "
        f"TARGET: "
        f"{C}{ip:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W} "
        f"COMMUNITY: "
        f"{C}{community:<35}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└───────────────────────────────────────────────┘{W}"
    )

    # -----------------------------
    # COMMAND
    # -----------------------------

    cmd = (
        f"snmpwalk "
        f"-v2c "
        f"-c '{community}' "
        f"{ip}"
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"COMMAND\n"
    )

    print(
        f"{Y}{cmd}{W}\n"
    )

    # -----------------------------
    # EXECUTE
    # -----------------------------

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
    # SAVE RAW
    # -----------------------------

    raw_file = (
        artifact_dir
        / "snmpwalk.txt"
    )

    raw_file.write_text(
        output
    )

    # -----------------------------
    # PARSE STRINGS
    # -----------------------------

    strings = []

    for line in output.splitlines():

        if "STRING:" not in line:
            continue

        try:

            value = (
                line
                .split(
                    "STRING:",
                    1
                )[1]
                .strip()
            )

            if value:

                strings.append(
                    value
                )

        except:

            pass

    strings = sorted(
        set(strings)
    )

    strings_file = (
        artifact_dir
        / "strings.txt"
    )

    strings_file.write_text(
        "\n".join(
            strings
        )
    )

    # -----------------------------
    # RESULTS
    # -----------------------------

    print()

    if strings:

        print(
            f"{G}[+]{W} "
            f"Interesting Strings\n"
        )

        for value in strings:

            print(
                f"{C}{value}{W}"
            )

        print()

    print(
        f"{G}[+]{W} "
        f"Saved:"
    )

    print(
        f"{C}{raw_file}{W}"
    )

    print(
        f"{C}{strings_file}{W}"
    )

    print()
