from pathlib import Path
import subprocess

from core.runner import run_module_by_name


def run(data, cred, args):

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    W = '\033[0m'
    R = '\033[91m'
    BOLD = '\033[1m'

    # ---------------------------------------------------------
    # TARGET FILE
    # ---------------------------------------------------------

    target = None

    if hasattr(args, "extra") and args.extra:
        target = args.extra[0]

    if not target:

        print(f"\n{R}[!] {W}Missing VHD/VHDX file\n")
        return

    target = Path(target).expanduser().resolve()

    if not target.exists():

        print(
            f"\n{R}[!] {W}File not found: "
            f"{C}{target}{W}\n"
        )

        return

    # ---------------------------------------------------------
    # WORDLIST
    # ---------------------------------------------------------

    wordlist = (
        getattr(args, "wordlist", None)
        or "/usr/share/wordlists/rockyou.txt"
    )

    # ---------------------------------------------------------
    # REFERENCE MODE
    # ---------------------------------------------------------

    if getattr(args, "ref", False):

        print(f"\n{B}┌── MODULE: BITLOCKER RECOVERY ─────────────────────┐{W}")
        print(f"{B}└───────────────────────────────────────────────────┘{W}")

        print(f"\n{B}[*]{W} Extract Hashes\n")

        print(
            f"{Y}bitlocker2john -i {M}<VHD>{W} "
            f"> backup.hashes"
        )

        print(
            f"{Y}grep '$bitlocker$0' "
            f"backup.hashes > backup.hash{W}"
        )

        print(f"\n{B}[*]{W} Crack\n")

        print(
            f"{Y}hashcat -m 22100 "
            f"backup.hash "
            f"{M}<WORDLIST>{W}"
        )

        print()

        return

    # ---------------------------------------------------------
    # ARTIFACTS
    # ---------------------------------------------------------

    artifact_dir = Path(
        "artifacts/bitlocker"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    hashes_file = (
        artifact_dir / "bitlocker.hashes"
    )

    hash_file = (
        artifact_dir / "bitlocker.hash"
    )

    # ---------------------------------------------------------
    # HUD
    # ---------------------------------------------------------

    print(
        f"\n{B}┌── {BOLD}MODULE: BITLOCKER RECOVERY{W}{B} "
        f"{'─' * 24}┐{W}"
    )

    print(
        f"{B}│{W}  {B}FILE:{W} "
        f"{C}{target.name:<46}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}WORDLIST:{W} "
        f"{C}{Path(wordlist).name:<42}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└{'─' * 56}┘{W}"
    )

    # ---------------------------------------------------------
    # EXTRACT HASHES
    # ---------------------------------------------------------

    extract_cmd = [
        "bitlocker2john",
        "-i",
        str(target)
    ]

    print(
        f"\n{B}[*]{W} Extracting BitLocker hashes\n"
    )

    print(
        f"{Y}{' '.join(extract_cmd)}{W}\n"
    )

    result = subprocess.run(
        extract_cmd,
        capture_output=True,
        text=True
    )

    if not result.stdout.strip():

        print(
            f"{R}[!] {W}Failed to extract hashes\n"
        )

        return

    hashes_file.write_text(
        result.stdout
    )

    # ---------------------------------------------------------
    # EXTRACT PASSWORD HASH
    # ---------------------------------------------------------

    password_hashes = []

    for line in result.stdout.splitlines():

        if "$bitlocker$0" in line:
            password_hashes.append(line)

    if not password_hashes:

        print(
            f"{R}[!] {W}No password hashes found\n"
        )

        return

    hash_file.write_text(
        "\n".join(password_hashes)
    )

    print(
        f"{G}[+] {W}Hash extracted: "
        f"{C}{hash_file}{W}"
    )

    # ---------------------------------------------------------
    # HASHCAT
    # ---------------------------------------------------------

    crack_cmd = [
        "hashcat",
        "-a",
        "0",
        "-m",
        "22100",
        str(hash_file),
        wordlist
    ]

    print(
        f"\n{B}[*]{W} Cracking BitLocker password\n"
    )

    print(
        f"{Y}{' '.join(crack_cmd)}{W}\n"
    )

    subprocess.run(crack_cmd)

    # ---------------------------------------------------------
    # SHOW RESULTS
    # ---------------------------------------------------------

    show_cmd = [
        "hashcat",
        "-m",
        "22100",
        str(hash_file),
        "--show"
    ]

    print(
        f"{B}[*]{W} Showing results\n"
    )

    print(
        f"{Y}{' '.join(show_cmd)}{W}\n"
    )

    result = subprocess.run(
        show_cmd,
        capture_output=True,
        text=True
    )

    lines = [
        x.strip()
        for x in result.stdout.splitlines()
        if x.strip()
    ]

    if not lines:

        print(
            f"{Y}[-] {W}No password recovered\n"
        )

        return

    recovered_password = None

    for line in lines:

        if ":" in line:

            recovered_password = (
                line.rsplit(":", 1)[1]
            )

            break

    if not recovered_password:

        return

    print(
        f"\n{G}[+] {W}Password recovered: "
        f"{C}{recovered_password}{W}\n"
    )

    # ---------------------------------------------------------
    # MOUNT PROMPT
    # ---------------------------------------------------------

    answer = input(
        "Mount drive now? [Y/n]: "
    ).strip().lower()

    if answer in ("", "y", "yes"):

        run_module_by_name(
            "mount.vhd",
            [
                str(target),
                "--password",
                recovered_password
            ],
            data=data
        )

    return [
        {
            "type": "credential",
            "data": {
                "service": "bitlocker",
                "password": recovered_password
            }
        }
    ]
