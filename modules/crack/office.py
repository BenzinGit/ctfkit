from pathlib import Path
import subprocess

from core.paths import get_artifacts_dir


def run(data, cred, args):

    # ---------------------------------------------------------
    # COLORS
    # ---------------------------------------------------------

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    W = '\033[0m'
    R = '\033[91m'
    BOLD = '\033[1m'

    # ---------------------------------------------------------
    # INPUT
    # ---------------------------------------------------------

    office_file = None

    if hasattr(args, "extra") and args.extra:
        office_file = args.extra[0]

    if not office_file:

        print(f"\n{R}[!] {W}Missing Office document\n")
        return

    office_file = Path(office_file).expanduser().resolve()

    if not office_file.exists():

        print(
            f"\n{R}[!] {W}File not found: "
            f"{C}{office_file}{W}\n"
        )

        return

    wordlist = (
        getattr(args, "wordlist", None)
        or "/usr/share/wordlists/rockyou.txt"
    )

    wordlist = Path(wordlist).expanduser()

    # ---------------------------------------------------------
    # REFERENCE MODE
    # ---------------------------------------------------------

    if getattr(args, "ref", False):

        print(f"\n{B}┌── MODULE: OFFICE RECOVERY ──────────────────────────┐{W}")
        print(f"{B}└─────────────────────────────────────────────────────┘{W}")

        print(f"\n{B}[*]{W} EXTRACT HASH\n")

        print(
            f"{Y}office2john "
            f"{C}<FILE>{W}"
        )

        print(f"\n{B}[*]{W} CRACK HASH\n")

        print(
            f"{Y}john office.hash "
            f"--wordlist {C}<WORDLIST>{W}"
        )

        print(f"\n{B}[*]{W} SHOW RESULTS\n")

        print(
            f"{Y}john office.hash --show{W}\n"
        )

        return

    # ---------------------------------------------------------
    # ARTIFACTS
    # ---------------------------------------------------------

    artifact_dir = get_artifacts_dir(
        "office"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    hash_file = artifact_dir / "office.hash"
    cracked_file = artifact_dir / "cracked.txt"

    # ---------------------------------------------------------
    # HUD
    # ---------------------------------------------------------

    print(
        f"\n{B}┌── {BOLD}MODULE: OFFICE RECOVERY{W}{B} "
        f"{'─' * 29}┐{W}"
    )

    print(
        f"{B}│{W}  {B}FILE:{W} "
        f"{C}{office_file.name:<46}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}WORDLIST:{W} "
        f"{C}{wordlist.name:<42}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└{'─' * 56}┘{W}"
    )

    # ---------------------------------------------------------
    # EXTRACT HASH
    # ---------------------------------------------------------

    extract_cmd = [
        "office2john",
        str(office_file)
    ]

    print(
        f"\n{B}[*]{W} EXTRACTING OFFICE HASH\n"
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
            f"{R}[!] {W}Failed to extract Office hash\n"
        )

        return

    hash_file.write_text(
        result.stdout
    )

    print(
        f"{G}[+] {W}Hash saved: "
        f"{C}{hash_file}{W}"
    )

    # ---------------------------------------------------------
    # JOHN
    # ---------------------------------------------------------

    john_cmd = [
        "john",
        str(hash_file),
        f"--wordlist={wordlist}"
    ]

    print(
        f"\n{B}[*]{W} CRACKING DOCUMENT\n"
    )

    print(
        f"{Y}{' '.join(john_cmd)}{W}\n"
    )

    subprocess.run(john_cmd)

    # ---------------------------------------------------------
    # SHOW
    # ---------------------------------------------------------

    show_cmd = [
        "john",
        str(hash_file),
        "--show"
    ]

    print(
        f"{B}[*]{W} SHOWING RESULTS\n"
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
        l
        for l in result.stdout.splitlines()
        if l.strip()
    ]

    if not lines:

        print(
            f"{Y}[-] {W}No password recovered\n"
        )

        return

    cracked_file.write_text(
        "\n".join(lines)
    )

    print(
        f"\n{G}┌── RECOVERED PASSWORDS "
        f"{'─' * 39}┐{W}"
    )

    for line in lines:

        if ":" in line:

            parts = line.split(":")

            if len(parts) >= 2:

                password = parts[1]

                print(
                    f"{G}│{W} "
                    f"{B}PASSWORD:{W} "
                    f"{C}{password:<43}{W}"
                    f"{G}│{W}"
                )

    print(
        f"{G}└{'─' * 61}┘{W}"
    )

    print(
        f"\n{G}[+] {W}Results saved:"
    )

    print(
        f"  {B}├──{W} "
        f"{C}{hash_file}{W}"
    )

    print(
        f"  {B}└──{W} "
        f"{C}{cracked_file}{W}"
    )

    print()

    return [
        {
            "type": "credential",
            "data": {
                "source": str(office_file),
                "artifact": str(cracked_file)
            }
        }
    ]