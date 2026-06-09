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

    ip = data.get("ip")

    if not ip:

        print(
            f"\n{R}[!]{W} No target IP loaded."
        )

        return

    target_name = data.get(
        "name",
        "unknown"
    )

    artifact_dir = (
        get_artifacts_dir(
            target_name
        )
        / "mysql"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # -------------------------
    # AUTH
    # -------------------------

    creds = data.get(
        "creds",
        []
    )

    current_index = data.get(
        "current_cred"
    )

    if (
        current_index is None
        or current_index >= len(creds)
    ):

        print(
            f"\n{R}[!]{W} "
            f"No credential selected."
        )

        return

    cred = creds[
        current_index
    ]

    if cred.get(
        "type"
    ) != "password":

        print(
            f"\n{R}[!]{W} "
            f"MySQL requires a password credential."
        )

        return

    user = cred.get(
        "user"
    )

    password = cred.get(
        "secret"
    )

    # -------------------------
    # QUERY HELPER
    # -------------------------

    def mysql_query(query):

        cmd = (
            f"mysql "
            f"-u '{user}' "
            f"-p'{password}' "
            f"-h {ip} "
            f"--skip-ssl "
            f"-N "
            f"-e \"{query}\""
        )

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )

        return result.stdout

    # -------------------------
    # DATABASES
    # -------------------------

    output = mysql_query(
        "show databases;"
    )

    databases = [

        x.strip()

        for x in output.splitlines()

        if x.strip()
    ]

    if not databases:

        print(
            f"\n{R}[!]{W} "
            f"No databases found."
        )

        return

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} DATABASES\n"
    )

    for i, db in enumerate(
        databases,
        1
    ):

        print(
            f"{C}[{i}]{W} {db}"
        )

    print(
        f"\n[0] Exit\n"
    )

    choice = input(
        "> "
    ).strip()

    if choice == "0":

        return

    try:

        database = databases[
            int(choice) - 1
        ]

    except:

        return

    # -------------------------
    # TABLES
    # -------------------------

    output = mysql_query(
        f"use {database}; "
        f"show tables;"
    )

    tables = [

        x.strip()

        for x in output.splitlines()

        if x.strip()
    ]

    if not tables:

        print(
            f"\n{R}[!]{W} "
            f"No tables found."
        )

        return

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"TABLES "
        f"({database})\n"
    )

    for i, table in enumerate(
        tables,
        1
    ):

        print(
            f"{C}[{i}]{W} {table}"
        )

    print(
        f"\n[0] Exit\n"
    )

    choice = input(
        "> "
    ).strip()

    if choice == "0":

        return

    try:

        table = tables[
            int(choice) - 1
        ]

    except:

        return

    # -------------------------
    # DUMP TABLE
    # -------------------------

    query = (
        f"use {database}; "
        f"select * from {table} limit 50;"
    )

    output = mysql_query(
        query
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"{database}.{table}\n"
    )

    print(
        output
    )

    outfile = (
        artifact_dir
        / f"{database}_{table}.txt"
    )

    outfile.write_text(
        output
    )

    print()

    print(
        f"{G}[+]{W} "
        f"Saved:"
    )

    print(
        f"{C}{outfile}{W}"
    )

    print()
