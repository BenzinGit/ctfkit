import subprocess
from pathlib import Path


DEFAULT_WORDLIST = "/usr/share/wordlists/rockyou.txt"
HASHCAT_MODE = "5200"


def run(data, cred, args):
    """
    Crack Password Safe (.psafe3)

    Usage:
        ctf crack.psafe3 file.psafe3
        ctf crack.psafe3 file.psafe3 wordlist.txt
    """

    # -------------------------
    # Parse arguments
    # -------------------------
    extra = getattr(args, "extra", []) or []

    if len(extra) < 1:
        print("[-] Missing file")
        return data

    file = Path(extra[0]).expanduser()

    wordlist = DEFAULT_WORDLIST
    if len(extra) >= 2:
        wordlist = extra[1]

    # -------------------------
    # Validate inputs
    # -------------------------
    if not file.exists():
        print(f"[-] File not found: {file}")
        return data

    wordlist_path = Path(wordlist).expanduser()
    if not wordlist_path.exists():
        print(f"[-] Wordlist not found: {wordlist_path}")
        return data

    # -------------------------
    # Build command
    # -------------------------
    crack_cmd = [
        "hashcat",
        "-a", "0",
        "-m", HASHCAT_MODE,
        str(file),
        str(wordlist_path)
    ]

    print(f"[*] Running: {' '.join(crack_cmd)}")

    # -------------------------
    # Execute and capture output
    # -------------------------
    try:
        result = subprocess.run(
            crack_cmd,
            capture_output=True,
            text=True
        )
    except Exception as e:
        print(f"[-] Hashcat failed: {e}")
        return data

    output = result.stdout + result.stderr

    # -------------------------
    # Extract password from output
    # -------------------------
    password = None

    for line in output.splitlines():
        if ":" in line and file.name in line:
            try:
                password = line.split(":", 1)[1].strip()
                break
            except:
                continue

    if not password:
        print("[-] No password recovered")
        return data

    print(f"[+] Password: {password}")

    # -------------------------
    # Optional save
    # -------------------------
    out_file = getattr(args, "out", None)

    if out_file:
        out_path = Path(out_file).expanduser()
        out_path.write_text(password + "\n")
        print(f"[+] Saved to: {out_path}")


    # -------------------------
    # Optional: open file
    # -------------------------

    print(f"[*] Opening: pwsafe {file}")

    try:
        subprocess.run(["pwsafe", str(file)])
    except Exception as e:
        print(f"[-] Failed to open pwsafe: {e}")


    return data