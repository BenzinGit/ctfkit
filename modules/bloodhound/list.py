def run(data, creds, args):
    import subprocess
    from pathlib import Path

    # --- CORE PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    BASE = Path.home() / ".ctfkit" / "bloodhound"
    
    # Standardized Module Header (No Box for lists, use the Table Header)
    print(f"\n{B}┌── {BOLD}BLOODHOUND INSTANCES{W}{B} ─────────────────────────────────────────────┐{W}")
    print(f"{B}│{W} {BOLD}{'NAME':<20}{W} {B}│{W} {BOLD}{'STATUS':<10}{W}{B}│{W} {BOLD}{'PORT / URL':<32}{W} {B}│{W}")
    print(f"{B}├──────────────────────┼───────────┼──────────────────────────────────┤{W}")

    if not BASE.exists() or not any(BASE.iterdir()):
        print(f"{B}│{W} {DIM}{'No active instances found.':<68}{W} {B}│{W}")
    else:
        for item in sorted(BASE.iterdir()):
            if item.is_dir():
                name = item.name
                
                # Get Status
                status_proc = subprocess.run(
                    ["docker", "inspect", f"bh_{name}_app", "--format", "{{.State.Status}}"],
                    capture_output=True, text=True
                )
                raw_status = status_proc.stdout.strip().lower() if status_proc.returncode == 0 else "missing"
                
                # Tactical Status Coloring
                if raw_status == "running":
                    status = f"{G}RUNNING{W}"
                    status_padding = 11 # Adjusting for ANSI codes
                elif raw_status == "exited" or raw_status == "paused":
                    status = f"{Y}{raw_status.upper()}{W}"
                    status_padding = 11
                else:
                    status = f"{R}{raw_status.upper()}{W}"
                    status_padding = 11

                # Get Port Mapping
                port_proc = subprocess.run(
                    ["docker", "inspect", f"bh_{name}_app", "--format", 
                     '{{(index (index .NetworkSettings.Ports "8080/tcp") 0).HostPort}}'],
                    capture_output=True, text=True
                )
                port = port_proc.stdout.strip() if port_proc.returncode == 0 else "????"
                url = f"http://localhost:{port}" if port != "????" else "N/A"

                # Print formatted row (Manual padding for status to handle ANSI colors)
                name_str = f"{C}{name:<20}{W}"
                url_str = f"{W}{url:<32}{W}"
                
                # Note: We use 11 for status width, but since it has ANSI, we print it then pad manually
                print(f"{B}│{W} {name_str} {B}│{W} {status}{' ' * (11 - len(raw_status) - 2)} {B}│{W} {url_str} {B}│{W}")

    print(f"{B}└──────────────────────┴───────────┴──────────────────────────────────┘{W}")