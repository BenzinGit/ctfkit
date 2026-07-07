from pathlib import Path
import subprocess


RULES = {
    "best66": "/usr/share/hashcat/rules/best66.rule",
    "dive": "/usr/share/hashcat/rules/dive.rule",
    "oneruletorulethemall": "tools/rules/OneRuleToRuleThemAll.rule",
}


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
    # INPUT FILE
    # =========================================================

    infile = None

    if hasattr(args, "extra") and args.extra:
        infile = args.extra[0]

    if not infile:
        print(f"\n{R}[!] {W}{BOLD}MISSING WORDLIST{W}")
        print(f"{B}  └── Usage:{W} ctf wordlist.rules company.txt")
        return

    infile = Path(infile).expanduser().resolve()

    if not infile.exists():
        print(f"\n{R}[!] {W}{BOLD}FILE NOT FOUND{W}")
        print(f"{B}  └── {C}{infile}{W}")
        return

    # =========================================================
    # RULE
    # =========================================================

    rule_name = (
        getattr(args, "rule", None)
        or "best66"
    ).lower()

    if rule_name not in RULES:

        print(f"\n{R}[!] {W}{BOLD}UNKNOWN RULE{W}")
        print()

        for r in RULES:
            print(f"  {B}├──{W} {r}")

        print()
        return

    rule_file = Path(RULES[rule_name])

    if not rule_file.exists():

        print(f"\n{R}[!] {W}{BOLD}RULE FILE NOT FOUND{W}")
        print(f"{B}  └── {C}{rule_file}{W}")
        return

    # =========================================================
    # OUTPUT
    # =========================================================

    outfile = (
        infile.parent /
        f"{infile.stem}_{rule_name}.txt"
    )

    # =========================================================
    # REFERENCE MODE
    # =========================================================

    if getattr(args, "ref", False):

        print(
            f"\n{B}┌── {BOLD}MODULE: WORDLIST RULES{W}{B} "
            f"{'─' * 21}┐{W}"
        )

        print(
            f"{B}└──────────────────────────────────────────────────────┘{W}"
        )

        print(f"\n{B}[*]{W} Example Command\n")

        print(
            f"{Y}hashcat "
            f"{C}<wordlist>{Y} "
            f"-r {C}<rule>{Y} "
            f"--stdout > "
            f"{C}<output>{W}\n"
        )

        return

    # =========================================================
    # HUD
    # =========================================================

    print(
        f"\n{B}┌── {BOLD}MODULE: WORDLIST RULES{W}{B} "
        f"{'─' * 21}┐{W}"
    )

    print(
        f"{B}│{W}  {B}Input:{W} "
        f"{C}{infile.name:<43}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}Rule:{W}  "
        f"{C}{rule_name:<43}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}Output:{W}"
        f" {C}{outfile.name:<42}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└──────────────────────────────────────────────────────┘{W}"
    )

    # =========================================================
    # COMMAND
    # =========================================================

    cmd = [
        "hashcat",
        str(infile),
        "-r",
        str(rule_file),
        "--stdout"
    ]

    print(f"\n{B}[*]{W} Running\n")
    print(f"{Y}{' '.join(cmd)}{W}\n")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        print(f"{R}[!] {W}Generation failed\n")

        if result.stderr:
            print(result.stderr)

        return

    # =========================================================
    # SAVE
    # =========================================================

    words = []

    for line in result.stdout.splitlines():

        line = line.strip()

        if not line:
            continue

        words.append(line)

    words = sorted(set(words))

    outfile.write_text(
        "\n".join(words) + "\n"
    )

    # =========================================================
    # STATS
    # =========================================================

    print(
        f"{G}[+] {W}Generated "
        f"{C}{len(words):,}{W} candidates"
    )

    print(
        f"{G}[+] {W}Saved: "
        f"{C}{outfile}{W}\n"
    )

    return [
        {
            "type": "wordlist",
            "data": {
                "file": str(outfile),
                "count": len(words),
                "rule": rule_name
            }
        }
    ]
