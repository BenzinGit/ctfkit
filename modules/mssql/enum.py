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
            f"{Y}nmap "
            f"--script "
            f"ms-sql-info,"
            f"ms-sql-ntlm-info,"
            f"ms-sql-config,"
            f"ms-sql-dac "
            f"-sV "
            f"-p1433 "
            f"{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}nmap "
            f"--script "
            f"ms-sql-tables,"
            f"ms-sql-hasdbaccess,"
            f"ms-sql-dump-hashes,"
            f"ms-sql-xp-cmdshell "
            f"--script-args "
            f"mssql.username={M}<USER>{W},"
            f"mssql.password={M}<PASS>{W} "
            f"-p1433 "
            f"{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}impacket-mssqlclient "
            f"{M}<USER>{W}:{M}<PASS>{W}@{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}impacket-mssqlclient "
            f"{M}<DOMAIN>{W}/{M}<USER>{W}:{M}<PASS>{W}@{M}<IP>{W} "
            f"-windows-auth"
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

    domain = data.get(
        "domain"
    )

    # -----------------------------
    # ARTIFACTS
    # -----------------------------

    artifact_dir = (
        get_artifacts_dir(
            target_name
        )
        / "mssql"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------
    # AUTH
    # -----------------------------

    auth_label = "anonymous"
    mode = "RECON"

    creds = data.get(
        "creds",
        []
    )

    current_index = data.get(
        "current_cred"
    )

    have_creds = False
    script_args = ""

    if (
        current_index is not None
        and current_index < len(creds)
    ):

        current = creds[
            current_index
        ]

        if (
            current.get("type")
            == "password"
        ):

            user = current.get(
                "user"
            )

            password = current.get(
                "secret"
            )

            have_creds = True
            mode = "AUTHENTICATED"

            auth_label = (
                f"{user} (password)"
            )

            if domain:

                username = (
                    f"{domain}\\{user}"
                )

            else:

                username = user

            script_args = (
                f"--script-args "
                f"mssql.username='{username}',"
                f"mssql.password='{password}'"
            )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: MSSQL ENUMERATION "
        f"──────────────────┐{W}"
    )

    print(
        f"{B}│{W} "
        f"TARGET: "
        f"{C}{ip:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W} "
        f"AUTH:   "
        f"{C}{auth_label:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W} "
        f"MODE:   "
        f"{C}{mode:<38}{W}"
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
                f"-p1433 "
                f"{ip}"
            )
        )

    ]

    if have_creds:

        commands.append(

            (
                "AUTHENTICATED ENUMERATION",

                (
                    f"nmap "
                    f"--script "
                    f"ms-sql-info,"
                    f"ms-sql-ntlm-info,"
                    f"ms-sql-config,"
                    f"ms-sql-dac,"
                    f"ms-sql-tables,"
                    f"ms-sql-hasdbaccess,"
                    f"ms-sql-dump-hashes,"
                    f"ms-sql-xp-cmdshell "
                    f"{script_args} "
                    f"-sV "
                    f"-p1433 "
                    f"{ip}"
                )
            )

        )

    else:

        commands.append(

            (
                "RECON ENUMERATION",

                (
                    f"nmap "
                    f"--script "
                    f"ms-sql-info,"
                    f"ms-sql-ntlm-info,"
                    f"ms-sql-config,"
                    f"ms-sql-dac,"
                    f"ms-sql-empty-password "
                    f"-sV "
                    f"-p1433 "
                    f"{ip}"
                )
            )

        )

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
    # RESULTS
    # -----------------------------

    print()

    print(
        f"{G}[+]{W} "
        f"Results saved:"
    )

    print(
        f"{C}{artifact_dir}{W}"
    )

    print()