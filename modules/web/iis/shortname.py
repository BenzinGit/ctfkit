def run(data, cred, args):
    import subprocess
    from core.target import get_current_url
    from core.paths import get_artifacts_dir, get_tools_dir

    # --- CORE PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    target = get_current_url(data)
    if not target:
        print(f"{R}[!] PHASE: ABORTED. Target URL missing.{W}")
        return data

    if not target.startswith("http"): target = f"http://{target}"

    # 1. PHASE HEADER & RECON
    print(f"\n{B}[*]{W} {BOLD}IIS TILDE ENUMERATION (8.3 SHORTNAMES){W}")
    print(f"{B}  ├── {B}Target:{W}   {C}{target}{W}")

    jar = get_tools_dir() / "iis" / "iis_shortname_scanner.jar"
    config = get_tools_dir() / "iis" / "config.xml"

    if not jar.exists() or not config.exists():
        print(f"{R}  └── [!] ERROR: Missing scanner tools (JAR or XML).{W}")
        return data

    # 2. COMMAND TRANSPARENCY
    cmd = ["java", "-jar", str(jar), "0", "5", target, str(config)]
    print(f"{B}  └── {B}Command:{W} {Y}{' '.join(cmd)}{W}")

    try:
        print(f"\n{B}[*]{W} Analyzing IIS response patterns...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout
    except Exception as e:
        print(f"{R}[!] Subprocess Failure: {e}{W}")
        return data

    # Save artifact
    artifact_dir = get_artifacts_dir("iis_shortname")
    outfile = artifact_dir / "scan.txt"
    outfile.write_text(output)

    # 3. PARSING LOGIC
    vulnerable = "Result: Vulnerable!" in output
    dirs = []
    files = []

    for line in output.splitlines():
        if line.strip().startswith("|_ ") and "~" in line:
            name = line.replace("|_ ", "").strip()
            if "." in name: files.append(name)
            else: dirs.append(name)

    # 4. THE LOOT BOX
    status_color = G if vulnerable else R
    status_text = "VULNERABLE" if vulnerable else "NOT VULNERABLE"

    print(f"\n{status_color}┌── IIS SCAN RESULTS ──────────────────────────────────────┐{W}")
    print(f"{status_color}│{W}  {BOLD}STATUS:{W}  {status_color}{status_text:<46}{W} {status_color}│{W}")
    
    if dirs or files:
        print(f"{status_color}├──────────────────────────────────────────────────────────┤{W}")
        if dirs:
            for d in dirs:
                print(f"{status_color}│{W}  {B}[DIR]{W}  {d:<48} {status_color}│{W}")
        if files:
            for f in files:
                print(f"{status_color}│{W}  {C}[FIL]{W}  {f:<48} {status_color}│{W}")
    
    print(f"{status_color}└──────────────────────────────────────────────────────────┘{W}")

    # 5. RECOMMENDATION (Yellow Alert)
    if vulnerable and files:
        print(f"\n{Y}[!] RECOMMENDATION: TARGETED BRUTE-FORCE{W}")

        prefixes = []

        for f in files:
            if "~" in f:
                prefix = f.split("~")[0].lower()
                prefixes.append(prefix)

        prefixes = list(set(prefixes))  # dedupe

        for p in prefixes:
            print(f"\n{B}  ├── Prefix:{W} {C}{p}{W}")

            print(f"{B}  │   {W}Generate wordlist:")
            print(f"{B}  │   {Y}egrep -r ^{p} /usr/share/wordlists/* | sed 's/^[^:]*://' > /tmp/{p}.txt{W}")

            print(f"{B}  │   {W}Gobuster:")
            print(f"{B}  │   {Y}gobuster dir -u {target} -w /tmp/{p}.txt -x asp,aspx,txt{W}")

        print("")