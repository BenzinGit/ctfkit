PROVIDES = ["domain"]
REQUIRES = []

def run(data, cred, args):
    import subprocess
    import json
    from pathlib import Path
    from core.target import load_current_profile, save_profile
    from core.paths import get_domains_dir

    # --- ANSI PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    quiet = getattr(args, "quiet", False)
    ip = data.get("ip")

    if not ip:
        print(f"\n{R}[!] {W}{BOLD}RECONNAISSANCE ABORTED{W}")
        print(f"{R}  └── {W}Target IP is not set in the current profile.")
        return

    output = getattr(args, "out", None) or "hosts.txt"
    output_file = Path(output).expanduser().resolve()

    # ---------------- RUN NXC ----------------
    cmd = f"nxc smb {ip} --generate-hosts-file {output_file}"
    
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}STEP 1: NETWORK ENUMERATION{W}")
    if not quiet:
        print(f"{B}  └── {W}Running: {Y}{cmd}{W}")

    subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.DEVNULL if quiet else None,
        stderr=subprocess.DEVNULL if quiet else None
    )

    if not output_file.exists():
        print(f"{R}  └── {W}Error: NetExec failed to generate host mapping.")
        return

    # ---------------- UPDATE /etc/hosts ----------------
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}STEP 2: SYSTEM RESOLUTION{W}")
    content = output_file.read_text().strip()
    if not content:
        print(f"{R}  └── {W}Error: Host mapping is empty.")
        return

    try:
        hosts_path = Path("/etc/hosts")
        existing = hosts_path.read_text()
        new_lines = [line for line in content.splitlines() if line not in existing]

        if new_lines:
            temp_file = Path("/tmp/ctf_hosts_append.txt")
            temp_file.write_text("\n".join(new_lines) + "\n")
            subprocess.run(f"sudo sh -c 'cat {temp_file} >> /etc/hosts'", shell=True)
            print(f"{G}  [+]{W} Injected {len(new_lines)} entries into {C}/etc/hosts{W}")
        else:
            print(f"{B}  [*]{W} DNS mapping already synchronized with system.")
    except Exception as e:
        print(f"{R}  [!] {W}Permission denied: Manual sync required.")
        print(f"      {Y}sudo sh -c 'cat {output_file} >> /etc/hosts'{W}")

    # ---------------- EXTRACTION ----------------
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}STEP 3: IDENTITY EXTRACTION{W}")
    domain, hostname = None, None
    for line in content.splitlines():
        parts = line.split()
        if len(parts) < 2: continue
        for name in parts[1:]:
            if "." in name: domain = name.lower()
            else: hostname = name.lower()
        if domain: break

    if not domain:
        print(f"{R}  └── {W}Error: Could not determine FQDN from network response.")
        return

    # ---------------- UPDATE PROFILE ----------------
    data, path = load_current_profile()
    data["domain"] = domain
    if hostname: data["hostname"] = hostname
    save_profile(data, path)

    # ---------------- REGISTER DOMAIN ----------------
    domains_dir = get_domains_dir()
    domains_dir.mkdir(parents=True, exist_ok=True)
    domain_file = domains_dir / f"{domain}.json"

    is_new = not domain_file.exists()
    if is_new:
        domain_data = {"name": domain, "dc": None, "creds": [], "notes": []}
        domain_file.write_text(json.dumps(domain_data, indent=2))

    # --- FINAL HUD ---
    print(f"\n{G}┌── DOMAIN DISCOVERY COMPLETE ─────────────────────────────┐{W}")
    print(f"{G}│{W}  {B}Domain:{W}   {C}{domain:<18}{W} {B}Identity:{W} {G}RESOLVED{W}    {G}│{W}")
    print(f"{G}│{W}  {B}Hostname:{W} {C}{hostname or 'N/A':<18}{W} {B}Database:{W} {G}UPDATED{W}     {G}│{W}")
    print(f"{G}└──────────────────────────────────────────────────────────┘{W}\n")