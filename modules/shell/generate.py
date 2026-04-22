def run(data, cred, args):
    from pathlib import Path
    import subprocess
    from core.shell_templates import SHELLS
    from core.paths import get_artifacts_dir
    from core.attacker import resolve_lhost

    # --- CORE PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    # ---------------- SETTINGS ----------------
    target = data.get("name", "unknown")
    stype = args.extra[0] if (hasattr(args, "extra") and args.extra) else "bash"
    
    if stype not in SHELLS:
        print(f"\n{R}[!] {W}{BOLD}UNKNOWN SHELL TYPE: {stype}{W}")
        return

    shell_info = SHELLS[stype]
    lhost = resolve_lhost(args)
    
    if not lhost:
        print(f"\n{R}[!] {W}{BOLD}LHOST RESOLUTION FAILED{W}\n{B}  └── {W}Check tun0 or use --lhost")
        return

    # --- THE FIX ---
    # args.lport might exist as None, so we check the value specifically
    lport_raw = getattr(args, "lport", None)
    lport = int(lport_raw) if lport_raw is not None else 4444

    # ---------------- GENERATION ----------------
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    SHELL_DIR = BASE_DIR / "shells"
    shell_path = SHELL_DIR / shell_info["file"]

    if not shell_path.exists():
        print(f"\n{R}[!] {W}{BOLD}FILE NOT FOUND{W}\n{B}  └── {W}{shell_path}")
        return

    payload = shell_path.read_text().replace("{lhost}", lhost).replace("{lport}", str(lport))

    # Save logic
    base = get_artifacts_dir(target)
    shell_dir = base / "shells"
    shell_dir.mkdir(parents=True, exist_ok=True)
    ext = shell_path.suffix if shell_path.suffix else ".txt"
    outfile = shell_dir / f"{stype}_{lport}{ext}"
    outfile.write_text(payload)

    # ---------------- MODULE HUD (THE BOX) ----------------
    inner_w = 54
    print(f"\n{B}┌── {BOLD}MODULE: SHELL GENERATOR{W}{B} {'─' * (inner_w - 22)}┐{W}")
    print(f"{B}│{W}  {B}Type:{W}      {C}{stype:<38}{W} {B}│{W}")
    print(f"{B}│{W}  {B}Listener:{W}  {G}{lhost}{W} {B}:{W} {Y}{lport:<28}{W} {B}│{W}")
    print(f"{B}│{W}  {B}Mode:{W}      {W}{shell_info['mode'].upper():<38}{W} {B}│{W}")
    print(f"└{'─' * (inner_w + 2)}┘{W}")

    # ---------------- THE PAYLOAD BOX ----------------
    raw = getattr(args, "format", None) == "raw"
    
    if not raw:
        print(f"\n{G}┌── GENERATED PAYLOAD ──────────────────────────────────────{W}")
        display_lines = payload.splitlines()
        for line in display_lines[:5]:
            # Ensure line doesn't break the box width
            clean_line = line.replace('\t', '    ')
            print(f"{G}│{W}  {Y}{clean_line[:80]:<80}{W} {G}│{W}")
        if len(display_lines) > 5:
            print(f"{G}│{W}  {DIM}... (truncated, see artifact or clipboard){W}{' ':<12} {G}│{W}")
        print(f"{G}└─────────────────────────────────────────────────────────{W}")

    # ---------------- FINAL ACTIONS ----------------
    copied = False
    if shell_info["mode"] == "inline" and not raw:
        copied = copy_to_clipboard(payload)
    print(f"{B}  └── {B}Artifact:{W} {Y}{outfile}{W}")
    if copied:
        print(f"{B}  └── {G}Payload copied to clipboard{W}")

    if raw:
        print(payload)
    return [{"type": "shell", "data": {"payload": payload, "file": str(outfile)}}]
    

def copy_to_clipboard(text):
    import subprocess
    try:
        subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True)
        return True
    except:
        return False