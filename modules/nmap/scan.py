def run(data, cred, args):
    import subprocess
    from pathlib import Path
    from core.paths import get_artifacts_dir

    # --- ANSI PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    ip = data.get("ip")
    name = data.get("name")

    if not ip:
        print(f"\n{R}[!] {W}{BOLD}SCAN ABORTED{W}")
        print(f"{R}  └── {W}Target IP is not set in the current profile.")
        return

    # ---------------- ARTIFACTS ----------------
    artifacts = get_artifacts_dir(name)
    scan_dir = artifacts / "scans"
    scan_dir.mkdir(parents=True, exist_ok=True)
    output_base = scan_dir / name

    # ---------------- MODE LOGIC ----------------
    mode = args.extra[0] if args.extra else "default"
    
    # Map modes to colors and commands for the UI
    mode_styles = {
        "fast": (Y, f"nmap -T4 -F -oA {output_base}_fast {ip}"),
        "full": (R, f"nmap -p- -T4 -v -oA {output_base}_full {ip}"),
        "default": (C, f"nmap -sC -sV -oA {output_base} {ip}")
    }

    mode_color, cmd = mode_styles.get(mode, mode_styles["default"])

    # ---------------- UI OUTPUT ----------------
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}PHASE: RECONNAISSANCE{W}")
    print(f"{B}  ├── {B}Target:{W}   {C}{ip}{W}")
    print(f"{B}  ├── {B}Mode:{W}     {mode_color}{mode.upper()}{W}")
    print(f"{B}  └── {B}Output:{W}   {scan_dir}/{BOLD}{name}_* {W}")
    
    print(f"\n{W}[*] Running:{Y} {cmd}\n{W}")

    # ---------------- EXECUTION ----------------
    try:
        subprocess.run(cmd, shell=True)
        print(f"\n{G}[+] {W}{BOLD}SCAN COMPLETE{W}")
        print(f"{G}  └── {W}Results saved to artifacts storage.")
    except KeyboardInterrupt:
        print(f"\n{R}[!] {W}Scan manually interrupted by operator.")