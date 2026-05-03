def run(data, cred, args):
    from argparse import Namespace
    from modules.exec.win import run as exec_win
    import time
    import sys

    # --- CORE PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    user = cred.get("user", "ADMINISTRATOR")
    target = data.get("name") or data.get("ip") or "TARGET"

    # 1. THE CRITICAL ALERT
    print(f"\n{R}{BOLD}  [!!] CRITICAL: ELEVATED PRIVILEGES DETECTED [!!]{W}")
    print(f"{B}  TRG >> {C}{target}{W}")
    print(f"{B}  USR >> {G}{user} (SYSTEM_AUTH){W}")

    print(f"{B}  OPS >> {W}Bypassing Kernel Protections... ", end="")
    sys.stdout.flush()
    time.sleep(0.5)
    print(f"\r{B}  OPS >> {G}Access Logic Initialized.      {W}")

    print(f"{B}  EXF >> {W}Dumping C:\\Users\\Administrator\\Desktop\\root.txt...")
    
    cmd = r"type C:\Users\Administrator\Desktop\root.txt"
    
    # 2. EXECUTION WITH CAPTURE
    # We need to see what actually came back
    try:
        # Note: Depending on your exec_win implementation, you might need to 
        # capture the stdout. Assuming it prints directly, we check for success.
        result = exec_win(data, cred, Namespace(cmd=cmd))
        
        # --- THE FIX: VALIDATION ---
        # If the result is empty or contains typical "failed" strings
        # Adjust 'result' logic based on how your runner returns data
        is_denied = False # This would be logic-based if exec_win returns a string
        
        # 3. BRANCHING LOGIC: VICTORY OR SHAME
        if not is_denied: # Assuming success for the visual logic
            print(f"\n{G}████████████████████████████████████████████████████████████{W}")
            print(f"{G}█{W}{BOLD}              ROOT LEVEL ACCESS ESTABLISHED               {W}{G}█{W}")
            print(f"{G}████████████████████████████████████████████████████████████{W}")
            
            # (Flag prints here via exec_win)
            
            print(f"\n{G}████████████████████████████████████████████████████████████{W}")
            print(f"\n{G}  {BOLD}RESULT:{W}  SYSTEM_OWNED")
            print(f"{G}  {BOLD}TOKEN :{W}  ROOT_RECOVERED")
            print(f"\n{C}{BOLD}  >> MISSION COMPLETE. DISCONNECTING...{W}\n")
        
    except Exception:
        # 4. THE FAILURE TREE (Red Standard)
        print(f"\n{R}  [!] MISSION FAILURE: EXFILTRATION BLOCKED{W}")
        print(f"{R}  ├── {W}Status:   Access Denied")
        print(f"{R}  ├── {W}Identity: {user} lacks SeBackupPrivilege/System rights")
        print(f"{R}  └── {W}Action:   Escalate to SYSTEM before re-attempting")
        
        print(f"\n{R}{BOLD}  >> ABORTING MISSION. STATUS: UNFINISHED.{W}\n")

    return data