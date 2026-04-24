import yaml
from pathlib import Path

from core.target import load_current_profile, get_current_url
from core.runner import run_module_by_name
import os
import time
def clear_screen():
    os.system("clear")


# ---------------- PATH ----------------
BASE_DIR = Path(__file__).resolve().parent.parent
PLAYBOOK_DIR = BASE_DIR / "playbooks"


def show_step_list(steps, current_idx, completed):
    B, C, G, Y, W = '\033[94m', '\033[96m', '\033[92m', '\033[93m', '\033[0m'
    BOLD, DIM = '\033[1m', '\033[2m'

    print(f"\n{B}┌── {BOLD}PLAYBOOK STEPS{W}{B} ───────────────────────────────┐{W}")

    for i, step in enumerate(steps):
        is_active = (i == current_idx)
        is_done = (i in completed)

        marker = f"{G}▶{W}" if is_active else " "
        done = f"{G}✔{W}" if is_done else " "

        print(f"{B}│{W}  {marker}{done} [{i+1}] {C}{step['title']}{W}")

    print(f"{B}└──────────────────────────────────────────────────────┘{W}")


# ---------------- LOAD ----------------
def load_playbook(name):
    path = PLAYBOOK_DIR / f"{name.replace('.', '/')}.yaml"

    if not path.exists():
        print(f"[!] Playbook not found: {name}")
        return None

    return yaml.safe_load(path.read_text())


# ---------------- RENDER ----------------
def render_text(text, data):
    from core.target import get_current_url, get_active_cred

    
    url = get_current_url(data)

    cred = get_active_cred(data) or {}
    user = cred.get("user", "user")
    password = cred.get("secret", "password")

    return text.format(
        url=url or "http://target",
        ip=data.get("ip", ""),
        domain=data.get("domain", ""),
        user=user,
        password=password
    )


# ---------------- RUN ----------------
def run_playbook(args):
    pb = load_playbook(args.name)
    if not pb: return
    completed = set()
    steps = pb.get("steps", [])
    idx = 0

    # --- CORE PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    data, _ = load_current_profile()
    steps = pb.get("steps", [])
    idx = 0

    # 1. MISSION BRIEF HEADER
    inner_w = 54
    print(f"\n{B}┌── {BOLD}MISSION BRIEF: {pb.get('name', args.name).upper()}{W}{B} {'─' * (inner_w - 18)}┐{W}")
    print(f"{B}│{W}  {B}Target:{W}   {C}{data.get('name', 'unknown'):<38}{W} {B}│{W}")
    print(f"{B}│{W}  {B}Steps:{W}    {W}{len(steps):<38}{W} {B}│{W}")
    print(f"{B}└{'─' * (inner_w + 2)}┘{W}")

    while True:
        clear_screen()
        step = steps[idx]
        has_run = "run" in step
        
        # 2. STEP HEADER (The Tree Style)
        status = f"{G}✔{W} " if idx in completed else ""
        print(f"\n{B}[{idx+1}/{len(steps)}]{W} {status}{BOLD}{step['title'].upper()}{W}")

        if step.get("info"):
            print(f"{DIM}{step['info'].strip()}{W}")

        # 3. CONTENT SECTIONS
        if step.get("checklist"):
            print(f"\n{C}── CHECKLIST ──────────────────────────────────────────{W}")
            for c in step["checklist"]:
                print(f"  {B}□{W} {c}")

        if step.get("commands"):
            print(f"\n{Y}── COMMANDS ───────────────────────────────────────────{W}")
            for cmd in step["commands"]:
                print(f"  {Y}#{W} {render_text(cmd, data)}")

        if step.get("payloads"):
            print(f"\n{R}── PAYLOADS ───────────────────────────────────────────{W}")
            for p in step["payloads"]:
                print(f"  {R}→{W} {BOLD}{p}{W}")


        if step.get("success"):
            print(f"\n{G}── SUCCESS ───────────────────────────────────────────{W}")
            for p in step["success"]:
                print(f"  {G}→{W} {BOLD}{p}{W}")        

        # 4. ACTION HUD (The footer)
        print(f"\n{B}───────────────────────────────────────────────────────{W}")
        nav_hints = f"{B}[n]{W}ext  {B}[b]{W}ack  {B}[c]{W}omplete  {B}[l]{W}ist  {B}[q]{W}uit"
        action_hint = f"  {G}[1]{W} {BOLD}EXECUTE MODULE{W}" if has_run else ""
        
        choice = input(f"{nav_hints}{action_hint}\n{BOLD}Command{W} > ").strip().lower()

        # -------- LOGIC --------
        if choice == "1" and has_run:
            run_cfg = step["run"]
            name = run_cfg.get("name")
            raw_args = run_cfg.get("args", [])
            parsed_args = [render_text(a, data) for a in raw_args]
            
            print(f"\n{G}[*]{W} {BOLD}INVOKING MODULE:{W} {C}{name}{W}")
            run_module_by_name(name, parsed_args, data=data)
            input(f"\n{DIM}Press Enter to return to Briefing...{W}")

        # ... (previous code remains the same until the CHOICE LOGIC)

        elif choice == "n":
            if idx < len(steps) - 1: 
                idx += 1
                # VISUAL SEPARATOR FOR STEP TRANSITION
                print(f"\n{B}{'━' * 60}{W}")
                print(f"{G}▷▷▷{W} {BOLD}TRANSITIONING TO STEP {idx+1}{W} {G}▷▷▷{W}")
                print(f"{B}{'━' * 60}{W}")
            else: 
                print(f"\n{G}[√]{W} {BOLD}Playbook Complete.{W}")
                break

        elif choice == "b":
            if idx > 0: 
                idx -= 1
                # VISUAL SEPARATOR FOR STEP TRANSITION
                print(f"\n{Y}{'━' * 60}{W}")
                print(f"{Y}◁◁◁{W} {BOLD}RETURNING TO STEP {idx+1}{W} {Y}◁◁◁{W}")
                print(f"{Y}{'━' * 60}{W}")
            else:
                print(f"{Y}[!] Already at first step.{W}")


        elif choice == "q":
            print(f"{Y}[!] Aborting Mission.{W}")
            break

        elif choice == "l":
            show_step_list(steps, idx, completed)
            jump = input(f"{BOLD}Jump to step (enter index or press Enter): {W}").strip()

            if jump.isdigit():
                j = int(jump)

                # user inputs 1-based → convert to index
                j_idx = j - 1

                if 0 <= j_idx < len(steps):
                    idx = j_idx
                    print(f"\n{G}[*]{W} Jumping to step {j}")
                else:
                    print(f"{Y}[!] Invalid step number{W}")


        elif choice == "c":
            if idx in completed:
                completed.remove(idx)
                print(f"{Y}[-]{W} Marked as incomplete")
            else:
                completed.add(idx)
                print(f"{G}[+]{W} Marked as complete")
