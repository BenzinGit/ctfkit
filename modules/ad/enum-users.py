from pathlib import Path
from datetime import datetime
import subprocess

from core.paths import get_artifacts_dir
from core.target import get_current_ip


def run(data, cred, args):

    # =========================================================
    # COLORS
    # =========================================================

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    W = '\033[0m'
    R = '\033[91m'
    BOLD = '\033[1m'

    # =========================================================
    # TARGET
    # =========================================================

    target = (
        getattr(args, "target", None)
        or data.get("ip")
        or get_current_ip(data)
    )

    domain = data.get(
        "domain",
        "UNKNOWN"
    )

    if not target:

        print(
            f"\n{R}[!] {W}{BOLD}NO TARGET{W}\n"
        )

        return

    # =========================================================
    # USERLIST
    # =========================================================

    userlist = None

    if hasattr(args, "extra") and args.extra:
        userlist = args.extra[0]

    userlist_path = None

    if userlist:

        userlist_path = Path(
            userlist
        ).expanduser().resolve()

        if not userlist_path.exists():

            print(
                f"\n{R}[!] {W}{BOLD}USERLIST NOT FOUND{W}"
            )

            print(
                f"{B}  └── {C}{userlist_path}{W}\n"
            )

            return

    # =========================================================
    # METHOD SELECTION
    # =========================================================

    current = None

    try:
        current = cred.current()
    except Exception:
        pass

    if current:

        method = "LDAP"

    elif userlist_path:

        method = "KERBRUTE"

    else:

        method = "RID"

    # =========================================================
    # ARTIFACTS
    # =========================================================

    artifact_dir = (
        get_artifacts_dir(
            data["name"]
        )
        / "ad"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    users_file = (
        artifact_dir /
        "users.txt"
    )

    stamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    logfile = (
        artifact_dir /
        f"userenum_{stamp}.log"
    )

    # =========================================================
    # HUD
    # =========================================================

    print(
        f"\n{B}┌── {BOLD}MODULE: AD USER ENUMERATION{W}{B} ─────────────┐{W}"
    )

    print(
        f"{B}│{W}  {B}Domain:{W} "
        f"{C}{domain:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}Target:{W} "
        f"{C}{target:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}Method:{W} "
        f"{C}{method:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└──────────────────────────────────────────────────────┘{W}"
    )

    # =========================================================
    # LDAP
    # =========================================================

    if method == "LDAP":

        cmd = [
            "netexec",
            "ldap",
            str(target)
        ]

        if current["type"] == "password":

            cmd.extend([
                "-u",
                current["user"],
                "-p",
                current["secret"]
            ])

        elif current["type"] == "ntlm":

            cmd.extend([
                "-u",
                current["user"],
                "-H",
                current["secret"]
            ])

        cmd.extend([
            "--users",
            "--log",
            str(logfile)
        ])

    # =========================================================
    # KERBRUTE
    # =========================================================

    elif method == "KERBRUTE":

        cmd = [
            "kerbrute",
            "userenum",
            "-d",
            domain,
            "--dc",
            str(target),
            str(userlist_path)
        ]

    # =========================================================
    # RID CYCLING
    # =========================================================

    else:

        cmd = [
            "netexec",
            "smb",
            str(target),
            "--rid-brute"
        ]

        logfile = (
            artifact_dir /
            f"rid_{stamp}.log"
        )

        cmd.extend([
            "--log",
            str(logfile)
        ])

    # =========================================================
    # COMMAND
    # =========================================================

    print(
        f"\n{B}[*]{W} Running\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    # =========================================================
    # EXECUTE
    # =========================================================

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    print(result.stdout)

    # =========================================================
    # PARSE USERS
    # =========================================================

    users = set()

    # ---------------- KERBRUTE ----------------

    if method == "KERBRUTE":

        for line in result.stdout.splitlines():

            if "VALID USERNAME" not in line:
                continue

            try:

                username = (
                    line.split()[-1]
                    .split("@")[0]
                    .strip()
                )

                users.add(
                    username
                )

            except Exception:
                pass

    # ---------------- LDAP ----------------

    elif method == "LDAP":

        if logfile.exists():

            lines = logfile.read_text(
                errors="ignore"
            ).splitlines()

            for line in lines:

                if "LDAP" not in line:
                    continue

                if "Username" not in line:
                    continue

                parts = line.split()

                if len(parts) < 5:
                    continue

                username = parts[-1]

                if username.endswith("$"):
                    continue

                users.add(
                    username
                )

    # ---------------- RID ----------------

    else:

        if logfile.exists():

            lines = logfile.read_text(
                errors="ignore"
            ).splitlines()

            for line in lines:

                if "SidTypeUser" not in line:
                    continue

                try:

                    username = (
                        line.split("\\")[-1]
                        .strip()
                    )

                    users.add(
                        username
                    )

                except Exception:
                    pass

    # =========================================================
    # RESULTS
    # =========================================================

    users = sorted(
        list(users)
    )

    if not users:

        print(
            f"\n{Y}[-] {W}No users recovered\n"
        )

        return

    users_file.write_text(
        "\n".join(users)
    )

    print(
        f"\n{G}[+] {W}Recovered "
        f"{C}{len(users)}{W} user(s)\n"
    )

    for user in users[:20]:

        print(
            f"  {B}├──{W} "
            f"{C}{user}{W}"
        )

    if len(users) > 20:

        print(
            f"\n  {B}└──{W} "
            f"{C}+{len(users)-20}{W} more"
        )

    print()

    print(
        f"{G}[+] {W}Users Saved"
    )

    print(
        f"{B}  └── {C}{users_file}{W}\n"
    )

    return {
        "users": users
    }