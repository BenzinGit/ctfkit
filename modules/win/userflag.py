def run(data, cred, args):
    from argparse import Namespace
    from modules.exec.win import run as exec_win
    import time
    import sys

    # --- CORE PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    user = cred.get("user", "UNKNOWN")
    target = data.get("name", "TARGET")
    
    # 1. THE INTRUSION HEADER
    print(f"\n{G}  SCN >> {W}{BOLD}OBJECTIVE_LOCATE: {user}\\Desktop\\user.txt{W}")
    print(f"{G}  TRG >> {C}{target}{W}")
    
    # Simple, fast loading bar for effect
    print(f"{B}  EXE >> {W}", end="")
    for _ in range(15):
        sys.stdout.write(f"{G}█{W}")
        sys.stdout.flush()
        time.sleep(0.10)
    print(f" {G}100%{W}")

    # 2. THE DATA STREAM
    print(f"\n{DIM}[!] INTERCEPTING DATA STREAM...{W}")
    
    cmd = fr"type C:\Users\{user}\Desktop\user.txt"
    
    # Execute and isolate the payload
    print(f"{BOLD}{G}------------------------------------------------------------{W}")
    
    try:
        # Calling the execution engine
        exec_win(data, cred, Namespace(cmd=cmd))
    except Exception:
        print(f"{R}ERR >> STREAM BROKEN{W}")

    print(f"{BOLD}{G}------------------------------------------------------------{W}")

    # 3. THE ANALYST FOOTER
    print(f"\n{G}  ID  :: {W}{user}")
    print(f"{G}  TS  :: {W}{time.strftime('%H:%M:%S')} (UTC)")
    print(f"{G}  STA :: {W}{BOLD}PIVOT READY / ESCALATION RECOMMENDED{W}\n")

    return data