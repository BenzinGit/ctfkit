from modules.crack.detect_hash import detect_mode

def run(data, cred, args):
    import subprocess
    from pathlib import Path

    # --- CORE PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    # ---------------- HELPERS ----------------
    def require_file(val, name):
        if not val:
            print(f"\n{R}[!] {W}{BOLD}MISSING FILE{W}\n{B}  └── {B}Option:{W} --{name}")
            return None
        path = Path(val).expanduser().resolve()
        if not path.exists():
            print(f"\n{R}[!] {W}{BOLD}NOT FOUND{W}\n{B}  └── {B}Path:{W} {path}")
            return None
        return path

    quiet = getattr(args, "quiet", False)
    hashfile = require_file(getattr(args, "file", None), "file")
    if not hashfile: return

    # Wordlist Logic
    wordlist_path = getattr(args, "wordlist", None) or "/usr/share/wordlists/rockyou.txt"
    wordlist = Path(wordlist_path).expanduser().resolve()
    if not wordlist.exists():
        print(f"\n{R}[!] {W}{BOLD}WORDLIST MISSING{W}\n{B}  └── {W}{wordlist}")
        return

    # Mode Detection
    mode = getattr(args, "mode", None)
    auto_detected = False
    if not mode:
        mode = detect_mode(hashfile)
        auto_detected = True
        if not mode:
            print(f"\n{R}[!] {W}{BOLD}DETECTION FAILED{W}\n{B}  └── {W}Use --mode manually")
            return

    output_path = getattr(args, "out", None) or "cracked.txt"
    output_file = Path(output_path).expanduser().resolve()

    # ---------------- MODULE HUD (THE BOX) ----------------
    inner_w = 54
    print(f"\n{B}┌── {BOLD}MODULE: HASH RECOVERY{W}{B} {'─' * (inner_w - 20)}┐{W}")
    
    # Row 1: Target File
    print(f"{B}│{W}  {B}Hashfile:{W} {W}{hashfile.name:<{inner_w - 11}}{W} {B}│{W}")
    
    # Row 2: Mode Info
    mode_str = f"{mode} (Auto-Detected)" if auto_detected else f"{mode} (Manual)"
    print(f"{B}│{W}  {B}Mode:{W}     {Y}{mode_str:<{inner_w - 11}}{W} {B}│{W}")
    
    # Row 3: Wordlist
    print(f"{B}│{W}  {B}Wordlist:{W} {W}{wordlist.name:<{inner_w - 11}}{W} {B}│{W}")
    
    print(f"{B}└{'─' * (inner_w + 2)}┘{W}")

    # ---------------- EXECUTION ----------------
    cmd = f"hashcat -m {mode} {hashfile} {wordlist} --quiet"
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {B}Executing:{W} {Y}{cmd}{W}\n")

    # Run Hashcat
    subprocess.run(cmd, shell=True)

    # Show Results
    show_cmd = f"hashcat -m {mode} {hashfile} --show"
    result = subprocess.run(show_cmd, shell=True, capture_output=True, text=True)
    lines = [l for l in result.stdout.splitlines() if l.strip()]

    # ---------------- THE LOOT BOX ----------------
    if lines:
        output_file.write_text("\n".join(lines))
        
        print(f"{G}┌── CRACKED RESULTS ───────────────────────────────────────┐{W}")
        for line in lines:
            # Format: hash:password -> password is the highlight
            if ":" in line:
                h, p = line.split(":", 1)
                print(f"{G}│{W}  {B}PASS:{W} {G}{BOLD}{p:<44}{W} {G}│{W}")
            else:
                print(f"{G}│{W}  {W}{line:<50}{W} {G}│{W}")
        print(f"{G}└──────────────────────────────────────────────────────────┘{W}")
        print(f"{B}  └── {B}Artifact:{W} {Y}{output_file}{W}\n")
    else:
        print(f"{Y}[!] {W}No hashes recovered during this session.\n")