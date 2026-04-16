PROVIDES = ["creds"]
REQUIRES = []

def run(data, cred, args):
    import subprocess
    import argparse
    from pathlib import Path
    from core import target

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

    # ---------------- INPUT ----------------
    hashfile = require_file(args.file, "file")
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
        print("[!] Missing --mode")
        print("[*] Example: --mode 18200 (AS-REP), 13100 (Kerberoast), 0 (MD5)")
        return

    # ---------------- RUN HASHCAT ----------------
    cmd = f"hashcat -m {mode} {hashfile} {wordlist}"

    print(f"[*] Running: {cmd}\n")
    subprocess.run(cmd, shell=True)

    # ---------------- SHOW RESULTS ----------------
    show_cmd = f"hashcat -m {mode} {hashfile} --show"
    result = subprocess.run(show_cmd, shell=True, capture_output=True, text=True)

    lines = result.stdout.splitlines()

    if not lines:
        print("[!] No cracked hashes yet")
        return

    print("\n[+] Cracked credentials:\n")

    for line in lines:
        try:
            hash_part, password = line.rsplit(":", 1)

            user = extract_user(hash_part, mode)

            print(f"[+] {user}:{password}")

            # ---------------- OPTIONAL SAVE ----------------
            if getattr(args, "save", False):
                target.target_add_cred(
                    argparse.Namespace(
                        user=user,
                        password=password,
                        hash=None,
                        aes=None,
                        ccache=None
                    )
                )

        except Exception:
            print(f"[!] Failed to parse line: {line}")


def extract_user(hash_part, mode):
    try:
        if mode == "18200" and "$krb5asrep$" in hash_part:
            return hash_part.split("$")[3].split("@")[0]

        if mode == "13100" and "$krb5tgs$" in hash_part:
            return hash_part.split("$")[3].split("@")[0]

        if mode == "5600":
            return hash_part.split("::")[0]

        return "unknown"

    except Exception:
        return "unknown"