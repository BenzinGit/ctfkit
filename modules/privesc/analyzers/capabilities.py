"""
CTFKit - Linux PrivEsc
Capabilities Analyzer
"""

from pathlib import Path
import re


# ==========================================
# KNOWLEDGE BASE
# ==========================================

CAPABILITIES = {

    "cap_setuid": {
        "priority": "HIGH",
        "reason": "Can change the effective user ID."
    },

    "cap_setgid": {
        "priority": "HIGH",
        "reason": "Can change the effective group ID."
    },

    "cap_dac_override": {
        "priority": "HIGH",
        "reason": "Can bypass filesystem permission checks."
    },

    "cap_sys_admin": {
        "priority": "HIGH",
        "reason": "Provides extensive administrative privileges."
    },

}


BINARIES = {

    "vim.basic": {
        "recommendation": [
            "Run: ctf privesc.linux.capabilities.vim"
        ]
    },

    "python3": {
        "recommendation": [
            "Run: ctf privesc.linux.capabilities.python"
        ]
    },

    "perl": {
        "recommendation": [
            "Run: ctf privesc.linux.capabilities.perl"
        ]
    },

}


# ==========================================
# PARSER
# ==========================================

LINE_RE = re.compile(
    r"^(?P<path>\S+)\s*=\s*(?P<cap>cap_[^+]+)\+(?P<flags>\w+)$"
)


def _parse(section):

    entries = []

    for line in section.splitlines():

        line = line.strip()

        if not line:
            continue

        #
        # Ignore find errors
        #
        if line.startswith("find:"):
            continue

        match = LINE_RE.match(line)

        if not match:
            continue

        path = match.group("path")

        entries.append({

            "path": path,
            "binary": Path(path).name,
            "capability": match.group("cap"),
            "flags": match.group("flags")

        })

    return entries


# ==========================================
# PUBLIC API
# ==========================================

def analyze(section):

    entries = _parse(section)

    findings = []

    gtfo = 0
    interesting = 0

    for entry in entries:

        capability = entry["capability"]
        binary = entry["binary"]

        #
        # Ignore harmless capabilities
        #
        if capability not in CAPABILITIES:
            continue

        interesting += 1

        info = CAPABILITIES[capability]

        recommendation = ["Review manually."]

        if binary in BINARIES:
            recommendation = BINARIES[binary]["recommendation"]
            gtfo += 1

        findings.append({

            "priority": info["priority"],
            "module": "CAPABILITIES",
            "title": entry["path"],
            "reason": info["reason"],
            "recommendation": recommendation

        })

    return {

        "module": "CAPABILITIES",

        "summary": {

            "GTFOBins": gtfo,
            "Interesting": interesting,
            "Total": len(entries)

        },

        "findings": findings,

        "details": {

            "entries": entries

        }

    }
