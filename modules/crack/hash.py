PROVIDES = []
REQUIRES = []
from modules.crack.detect_hash import detect_mode

def run(data, cred, args):
    import subprocess
    from pathlib import Path

    # ---------------- HELPERS ----------------
    def require_file(val, name):
        if not val:
            print(f"[!] Missing --{name}")
            return None

        path = Path(val).expanduser().resolve()

        if not path.exists():
            print(f"[!] File not found: {path}")
            return None

        return path

    quiet = getattr(args, "quiet", False)

    # ---------------- INPUT ----------------
    hashfile = require_file(getattr(args, "file", None), "file")
    if not hashfile:
        return

    # ---------------- WORDLIST ----------------
    wordlist = getattr(args, "wordlist", None) or "/usr/share/wordlists/rockyou.txt"
    wordlist = Path(wordlist).expanduser().resolve()

    if not wordlist.exists():
        print(f"[!] Wordlist not found: {wordlist}")
        return

    # ---------------- MODE ----------------
    mode = getattr(args, "mode", None)

    if not mode:
        mode = detect_mode(hashfile)

        if not mode:
            print("[!] Could not detect hash type")
            print("[*] Use --mode manually")
            return

        print(f"[*] Auto-detected mode: {mode}")

    # ---------------- OUTPUT ----------------
    output_path = getattr(args, "out", None) or "cracked.txt"
    output_file = Path(output_path).expanduser().resolve()

    # ---------------- RUN HASHCAT ----------------
    cmd = f"hashcat -m {mode} {hashfile} {wordlist}"

    run_result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    if not quiet and run_result.stdout:
        print(run_result.stdout)

    # ---------------- SHOW RESULTS ----------------
    show_cmd = f"hashcat -m {mode} {hashfile} --show"
    result = subprocess.run(show_cmd, shell=True, capture_output=True, text=True)

    lines = result.stdout.splitlines()

    if not lines:
        print("[!] No cracked hashes yet")
        return

    if not lines:
        print("[!] No cracked hashes yet")
        return

    if not quiet:
        print("\n[+] Cracked results:\n")
        for line in lines:
            print(f"[+] {line}")

    # ---------------- SAVE ----------------
    output_file.write_text("\n".join(lines))
    print(f"\n[+] Saved → {output_file}")