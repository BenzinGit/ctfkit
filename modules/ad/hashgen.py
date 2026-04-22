import argparse
import hashlib

def run(data, cred, args):
    from core.target import target_add_cred

    # --- ANSI PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    extra = getattr(args, "extra", []) or []

    if len(extra) == 0:
        print(f"\n{R}[!] {W}{BOLD}HASHGEN FAILURE{W}")
        print(f"{R}  └── {W}Missing input. Provide: <password> or <user> <password>")
        return None

    # -------------------------
    # INPUT HANDLING
    # -------------------------
    if len(extra) == 1:
        if not cred:
            print(f"{R}[!] {W}No active credential to use as a fallback for the username.")
            return None
        user = cred.get("user")
        password = extra[0]
    else:
        user = extra[0]
        password = extra[1]

    if not user or not password:
        print(f"{R}[!] {W}Missing username or password string.")
        return None

    # -------------------------
    # GENERATE NTLM
    # -------------------------
    try:
        # NTLM is MD4(UTF-16-LE(password))
        ntlm_hash = hashlib.new(
            "md4",
            password.encode("utf-16le")
        ).hexdigest().upper() # Hashes look better in uppercase
    except Exception as e:
        print(f"{R}[!] {W}Generation error: {e}")
        return None

    # -------------------------
    # UI OUTPUT & STORAGE
    # -------------------------
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}PHASE: LOCAL HASH GENERATION{W}")
    print(f"{B}  ├── {B}Input:{W}    {Y}{'*' * len(password)}{W} (Plaintext)")


    # Store in the DB
    target_add_cred(
        argparse.Namespace(
            user=user,
            password=None, # We only want to store the hash for this entry
            hash=ntlm_hash,
            aes=None,
            ccache=None
        )
    )

    return [{
        "user": user,
        "type": "hash",
        "hash": ntlm_hash
    }]