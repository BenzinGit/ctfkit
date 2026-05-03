import yaml
from pathlib import Path
import os
import re

from core.target import load_current_profile
from core.runner import run_module_by_name

# ---------------- UTILS ----------------
def clear_screen():
    os.system("clear")

def inject_vars(text, data):
    """Replaces {key} with values from the current profile (e.g., {target})."""
    if not text: return ""
    matches = re.findall(r'\{(.*?)\}', text)
    for m in matches:
        val = data.get(m, f"<{m}>")
        text = text.replace(f"{{{m}}}", str(val))
    return text

BASE_DIR = Path(__file__).resolve().parent.parent
PLAYBOOK_DIR = BASE_DIR / "playbooks"

# ---------------- COLORS ----------------
G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
BOLD, DIM = '\033[1m', '\033[2m'

# ---------------- LOAD & NORMALIZE ----------------
def load_playbook(name):
    path = PLAYBOOK_DIR / f"{name.replace('.', '/')}.yaml"
    if not path.exists():
        print(f"{R}[!] Playbook not found: {path}{W}")
        return None
    return yaml.safe_load(path.read_text())

def normalize_playbook(pb, fallback_name):
    if isinstance(pb, list): return {"name": fallback_name, "steps": pb}
    if isinstance(pb, dict):
        return {"name": pb.get("name", fallback_name), "steps": pb.get("steps", [])}
    raise Exception("Invalid playbook format")

# =========================================================
#  TACTICAL RENDERERS
# =========================================================

def render_enum_step(step, is_expanded, data):
    entries = step.get("entries", [])
        
    print(f"\n{DIM}Commands:{W}")
    for i, e in enumerate(entries):
        mode = step.get("mode", "enum")
        cmd = inject_vars(e.get("cmd", ""), data)
        if mode == "chain":
            print(f"\n{G}Step {i+1}:{W}")
        print(f"{BOLD}{cmd}{W}")

        if is_expanded:
            if e.get("info"): print(f" {B}├──{W} {C}INFO:{W} {e['info']}")
            
            # The "Look For" branch
            if e.get("look_for"):
                print(f" {B}├──{W} {G}LOOK FOR:{W}")
                for l in e["look_for"]: print(f" {B}│{W}   {B}•{W} {l}")
            
            # NEW: The Tactical Payload branch
            if e.get("payload"):
                print(f" {B}├──{W} {R}PAYLOAD:{W} {BOLD}{e['payload']}{W}")

            # The Example / Notes branch
            if e.get("notes"):
                print(f" {B}├──{W} {Y}NOTES:{W}")
                for n in e["notes"]: print(f" {B}│{W}   {B}•{W} {n}")

            if e.get("example_output"):
                print(f" {B}└──{W} {DIM}EXAMPLE:{W}")
                for line in e["example_output"].splitlines():
                    print(f"     {DIM}{line}{W}")

def render_standard_step(step, is_expanded, data):
    commands = step.get("commands", [])
    for cmd in commands:
        print(f"\n{B}{W}{Y}{inject_vars(cmd, data)}{W}")

    if is_expanded:
        if step.get("notes"):
            print(f" {B}├──{W} {C}NOTES:{W}")
            for n in step["notes"]: print(f" {B}│{W}   {B}•{W} {n}")
        if step.get("example_output"):
            print(f" {B}└──{W} {DIM}EXAMPLE:{W}")
            for line in step["example_output"].splitlines():
                print(f"     {DIM}{line}{W}")

# =========================================================
#  MAIN ENGINE
# =========================================================

def run_playbook(args):
    raw = load_playbook(args.name)
    if not raw: return

    pb = normalize_playbook(raw, args.name)
    data, _ = load_current_profile()
    steps = pb["steps"]
    idx, expanded = 0, set()

    while True:
        clear_screen()
        if not steps: return print(f"{R}[!] No steps found.{W}")

        step = steps[idx]
        mode = step.get("mode", "enum")
        is_expanded = idx in expanded

        # --- TACTICAL HEADER ---
        state = f"{G}EXPANDED{W}" if is_expanded else f"{C}MINIMAL{W}"
        print(f"{B}┌── PLAYBOOK: {BOLD}{pb['name'].upper()}{W} {B}{'─'*(40-len(pb['name']))}┐{W}")
        print(f"{B}│{W}  {C}STEP {idx+1}/{len(steps)}:{W} {BOLD}{step.get('title','').upper()}{W} ({state})")
        print(f"{B}└──────────────────────────────────────────────────────┘{W}")

        if step.get("info") and is_expanded:
            print(f"{DIM}{step['info']}{W}")

        # --- CONTENT ---
        if mode in ["enum", "chain"]:
            render_enum_step(step, is_expanded, data)
        else:
            render_standard_step(step, is_expanded, data)

        # --- TACTICAL FOOTER ---
        print(f"\n{DIM}{'─'*60}{W}")
        print(f"{BOLD}{B}[N]{W}ext  {BOLD}{B}[B]{W}ack  {BOLD}{B}[T]{W}oggle View  {BOLD}{B}[L]{W}ist  {BOLD}{R}[Q]{W}uit")
        
        choice = input(f"\n{B}Select: ").strip().lower()

        if choice == "t":
            expanded.remove(idx) if idx in expanded else expanded.add(idx)
        elif choice == "n":
            if idx < len(steps) - 1: idx += 1
            else: print(f"\n{G}[+] Mission Complete.{W}"); break
        elif choice == "b":
            if idx > 0: idx -= 1
        elif choice == "l":
            print(f"\n{B}[*] STEP LIST:{W}")
            for i, s in enumerate(steps):
                marker = f"{G}▶{W}" if i == idx else " "
                print(f" {marker} [{i+1}] {s.get('title')}")
            input(f"\n{DIM}Press Enter to return...{W}")
        elif choice == "q":
            break

    return data