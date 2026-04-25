def run(data, cred, args):
    import subprocess
    import re
    from pathlib import Path

    # --- CORE PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    BASE = Path.home() / ".ctfkit" / "bloodhound"
    
    # Total inner width: 104
    print(f"\n{B}┌── {BOLD}BLOODHOUND INSTANCES{W}{B} ───────────────────────────────────────────────────────────────────────────────────┐{W}")
    print(f"{B}│{W} {BOLD}{'NAME':<20}{W} {B}│{W} {BOLD}{'STATUS':<11}{W} {B}│{W} {BOLD}{'PORT':<7}{W} {B}│{W} {BOLD}{'INITIAL PASSWORD':<58}{W} {B}│{W}")
    print(f"{B}├──────────────────────┼─────────────┼─────────┼────────────────────────────────────────────────────────────┤{W}")

    if not BASE.exists() or not any(BASE.iterdir()):
        print(f"{B}│{W} {DIM}{'No active instances found.':<102}{W} {B}│{W}")
    else:
        for item in sorted(BASE.iterdir()):
            if item.is_dir():
                name = item.name
                container_name = f"bh_{name}_app"
                
                # 1. Get Status
                status_proc = subprocess.run(
                    ["docker", "inspect", container_name, "--format", "{{.State.Status}}"],
                    capture_output=True, text=True
                )
                raw_status = status_proc.stdout.strip().lower() if status_proc.returncode == 0 else "missing"
                
                # Status Icons
                if raw_status == "running":
                    status_text = f"{G}● RUNNING{W}"
                    stat_len = 9 
                elif raw_status in ["exited", "paused", "created"]:
                    status_text = f"{Y}○ {raw_status.upper()}{W}"
                    stat_len = len(raw_status) + 2
                else:
                    status_text = f"{R}✖ MISSING{W}"
                    stat_len = 9

                # 2. Get Port
                port_proc = subprocess.run(
                    ["docker", "inspect", container_name, "--format", 
                     '{{range $p, $conf := .NetworkSettings.Ports}}{{(index $conf 0).HostPort}}{{end}}'],
                    capture_output=True, text=True
                )
                port = port_proc.stdout.strip() or "????"

                # 3. Extract Password (The Fix: Remove tail)
                password_plain = "PENDING/CHANGED"
                password_display = f"{DIM}PENDING/CHANGED{W}"
                
                if raw_status != "missing":
                    # We search the whole log because the password is only at the top
                    log_proc = subprocess.run(
                        f"docker logs {container_name} 2>&1", 
                        shell=True, capture_output=True, text=True
                    )
                    match = re.search(r"Initial Password Set To:\s+([a-zA-Z0-9_!@#$%^&*]+)", log_proc.stdout)
                    if match:
                        password_plain = match.group(1)
                        password_display = f"{Y}{BOLD}{password_plain}{W}"

                # Formatting Rows
                name_col = f"{C}{name:<20}{W}"
                status_col = f"{status_text}{' ' * (11 - stat_len)}"
                port_col = f"{Y}{port:<7}{W}"
                pass_col = f"{password_display}{' ' * (58 - len(password_plain))}"

                print(f"{B}│{W} {name_col} {B}│{W} {status_col} {B}│{W} {port_col} {B}│{W} {pass_col} {B}│{W}")

    print(f"{B}└──────────────────────┴─────────────┴─────────┴────────────────────────────────────────────────────────────┘{W}")