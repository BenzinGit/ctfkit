"""
CTFKit - Linux PrivEsc
Privileged Groups Analyzer
"""

import re


# ==========================================
# KNOWLEDGE BASE
# ==========================================

GROUPS = {

    "docker": {
        "priority": "HIGH",
        "reason": "Docker group membership allows privileged containers.",
        "recommendation": [
            "Run: ctf privesc.linux.groups.docker"
        ]
    },

    "lxd": {
        "priority": "HIGH",
        "reason": "LXD group membership may allow host filesystem access.",
        "recommendation": [
            "Run: ctf privesc.linux.groups.lxd"
        ]
    },

    "disk": {
        "priority": "HIGH",
        "reason": "Disk group grants raw access to block devices.",
        "recommendation": [
            "Run: ctf privesc.linux.groups.disk"
        ]
    },

    "adm": {
        "priority": "HIGH",
        "reason": "Can read system log files.",
        "recommendation": [
            "Run: ctf privesc.linux.groups.adm"
        ]
    },

}


# ==========================================
# PARSER
# ==========================================

def _parse(section):

    groups = []

    for line in section.splitlines():

        if "groups=" not in line:
            continue

        #
        # groups=1000(user),27(sudo),110(lxd)
        #
        value = line.split("groups=", 1)[1]

        for match in re.findall(r"\(([^)]+)\)", value):
            groups.append(match)

    return groups


# ==========================================
# PUBLIC API
# ==========================================

def analyze(section):

    groups = _parse(section)

    findings = []

    detected = []

    for group in groups:

        if group not in GROUPS:
            continue

        info = GROUPS[group]

        detected.append(group)

        findings.append({

            "priority": info["priority"],
            "module": "GROUPS",
            "title": group,
            "reason": info["reason"],
            "recommendation": info["recommendation"]

        })

    return {

        "module": "GROUPS",

        "summary": {

            "Detected": ", ".join(detected) if detected else "-",
            "Total": len(groups)

        },

        "findings": findings,

        "details": {

            "groups": groups,
            "interesting": detected

        }

    }
