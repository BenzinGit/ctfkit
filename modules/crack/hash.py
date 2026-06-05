from modules.crack.detect_hash import detect_mode
from modules.crack.detect_hash import detect_hashes


def run(data, cred, args):
    import subprocess
    import tempfile
    from pathlib import Path

    # --- CORE PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    # ---------------- HELPERS ----------------

    def resolve_hash_input():

        file = getattr(args, "file", None)

        # positional fallback
        if not file and hasattr(args, "extra") and args.extra:
            file = args.extra[0]

        if not file:
            print(f"\n{R}[!] {W}{BOLD}MISSING FILE{W}")
            print(f"{B}  └── {B}Option:{W} --file")
            return None

        candidate = Path(file).expanduser().resolve()

        # existing file
        if candidate.exists():
            return candidate

        # raw hash support
        tmp = Path(tempfile.gettempdir()) / "ctf_hash_input.txt"
        tmp.write_text(file + "\n")

        return tmp

    quiet = getattr(args, "quiet", False)

    hashfile = resolve_hash_input()

    if not hashfile:
        return

    # ---------------- WORDLIST ----------------

    wordlist_path = (
        getattr(args, "wordlist", None)
        or "/usr/share/wordlists/rockyou.txt"
    )

    wordlist = Path(wordlist_path).expanduser().resolve()

    if not wordlist.exists():
        print(f"\n{R}[!] {W}{BOLD}WORDLIST MISSING{W}")
        print(f"{B}  └── {W}{wordlist}")
        return

    # ---------------- DETECTION ----------------

    mode = getattr(args, "mode", None)

    auto_detected = False

    matches = []

    if not mode:

        matches = detect_hashes(hashfile)

        auto_detected = True

        if not matches:
            print(f"\n{R}[!] {W}{BOLD}DETECTION FAILED{W}")
            print(f"{B}  └── {W}Use --mode manually")
            return

    else:
        matches = [{
            "name": "Manual",
            "mode": str(mode),
            "confidence": 100
        }]

    output_path = getattr(args, "out", None) or "cracked.txt"
    output_file = Path(output_path).expanduser().resolve()

    # ---------------- HUD ----------------

    inner_w = 54

    print(f"\n{B}┌── {BOLD}MODULE: HASH RECOVERY{W}{B} {'─' * (inner_w - 23)}┐{W}")

    print(
        f"{B}│{W}  {B}Hashfile:{W} "
        f"{W}{hashfile.name:<{inner_w - 11}}{W} {B}│{W}"
    )

    if auto_detected:
        detected_str = matches[0]["name"]
        detected_mode = matches[0]["mode"]

        mode_str = (
            f"{detected_mode} "
            f"({detected_str} / Auto)"
        )
    else:
        mode_str = f"{mode} (Manual)"

    print(
        f"{B}│{W}  {B}Mode:{W}     "
        f"{Y}{mode_str:<{inner_w - 11}}{W} {B}│{W}"
    )

    print(
        f"{B}│{W}  {B}Wordlist:{W} "
        f"{W}{wordlist.name:<{inner_w - 11}}{W} {B}│{W}"
    )

    print(f"{B}└{'─' * (inner_w + 2)}┘{W}")

    # ---------------- CANDIDATES ----------------

    if auto_detected and len(matches) > 1:

        print(f"\n{B}[{W}{G}*{W}{B}]{W} {B}Candidate Modes:{W}")

        for h in matches:
            print(
                f"  {B}├──{W} "
                f"{Y}{h['mode']}{W} "
                f"({h['name']} / {h['confidence']}%)"
            )

    # ---------------- CRACK LOOP ----------------

    for h in matches:

        current_mode = h["mode"]
        current_name = h["name"]

        cmd = [
            "hashcat",
            "-m",
            str(current_mode),
            str(hashfile),
            str(wordlist),
            "--quiet"
        ]

        if quiet:
            cmd.append("--quiet")

        display_cmd = " ".join(cmd)

        print(
            f"\n{B}[{W}{G}*{W}{B}]{W} "
            f"{B}Trying:{W} "
            f"{Y}{current_name}{W} "
            f"({current_mode})"
        )

        print(
            f"{B}  └── {B}Command:{W} "
            f"{DIM}{display_cmd}{W}"
        )

        # ---------------- EXECUTION ----------------

        subprocess.run(cmd)

        # ---------------- SHOW ----------------

        show_cmd = [
            "hashcat",
            "-m",
            str(current_mode),
            str(hashfile),
            "--show"
        ]

        result = subprocess.run(
            show_cmd,
            capture_output=True,
            text=True
        )

        lines = [
            l for l in result.stdout.splitlines()
            if l.strip()
        ]

        # ---------------- SUCCESS ----------------

        if lines:

            output_file.write_text("\n".join(lines))

            print(f"\n{G}┌── CRACKED RESULTS ───────────────────────────────────────┐{W}")

            for line in lines:

                if ":" in line:
                    hsh, passwd = line.split(":", 1)

                    print(
                        f"{G}│{W}  "
                        f"{B}PASS:{W} "
                        f"{G}{BOLD}{passwd:<49}{W} "
                        f"{G}│{W}"
                    )

                else:
                    print(
                        f"{G}│{W}  "
                        f"{W}{line:<50}{W} "
                        f"{G}│{W}"
                    )

            print(f"{G}└──────────────────────────────────────────────────────────┘{W}")

            print(
                f"{B}  └── {B}Artifact:{W} "
                f"{Y}{output_file}{W}\n"
            )

            return

    # ---------------- FAILURE ----------------

    print(f"\n{Y}[!] {W}No hashes recovered during this session.\n")