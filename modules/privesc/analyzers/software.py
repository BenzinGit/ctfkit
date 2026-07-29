"""
CTFKit - Linux PrivEsc
Software Analyzer
"""

import re


# ==========================================
# KNOWLEDGE BASE
# ==========================================

SOFTWARE = {

    "screen": {
        "pattern": r"Screen version ([0-9.]+)",

        "reason": "Historical Screen privilege escalation vulnerabilities.",
        "recommendation": [
            "Run: ctf privesc.linux.software.screen"
        ],

        "versions": {

            "4.05.00": {
                "priority": "HIGH",
                "reason": "Known Screen local privilege escalation.",
                "recommendation": [
                    "Run: ctf privesc.linux.software.screen"
                ]
            }

        }

    },

    "sudo": {
        "pattern": r"Sudo version ([0-9.p]+)",
        "reason": "Historical sudo privilege escalation vulnerabilities.",
        "recommendation": [
            "Run: ctf privesc.linux.software.sudo"
        ]
    },

    "pkexec": {
        "pattern": r"pkexec version ([0-9.]+)",
        "reason": "Historical pkexec privilege escalation vulnerabilities.",
        "recommendation": [
            "Run: ctf privesc.linux.software.pkexec"
        ]
    },

    "snap": {
        "pattern": r"snap\s+([0-9.+]+)",
        "reason": "Historical snapd privilege escalation vulnerabilities.",
        "recommendation": [
            "Run: ctf privesc.linux.software.snap"
        ]
    },

    "logrotate": {
        "pattern": r"logrotate ([0-9.]+)",

        "reason": "Historical logrotate privilege escalation vulnerabilities.",
        "recommendation": [
            "Run: ctf privesc.linux.software.logrotate"
        ],

        "versions": {

            "3.8.6": {
                "priority": "HIGH",
                "reason": "Known vulnerable logrotate version.",
                "recommendation": [
                    "Run: ctf privesc.linux.software.logrotate"
                ]
            },

            "3.11.0": {
                "priority": "HIGH",
                "reason": "Known vulnerable logrotate version.",
                "recommendation": [
                    "Run: ctf privesc.linux.software.logrotate"
                ]
            },

            "3.15.0": {
                "priority": "HIGH",
                "reason": "Known vulnerable logrotate version.",
                "recommendation": [
                    "Run: ctf privesc.linux.software.logrotate"
                ]
            },

            "3.18.0": {
                "priority": "HIGH",
                "reason": "Known vulnerable logrotate version.",
                "recommendation": [
                    "Run: ctf privesc.linux.software.logrotate"
                ]
            }

        }

    }

}


# ==========================================
# PUBLIC API
# ==========================================

def analyze(section):
    findings = []
    detected = []

    for name, info in SOFTWARE.items():

        match = re.search(info["pattern"], section, re.MULTILINE)

        if not match:
            continue

        version = match.group(1)

        detected.append(f"{name} ({version})")

        #
        # Exact version match
        #
        if "versions" in info and version in info["versions"]:

            vuln = info["versions"][version]

            findings.append({

                "priority": vuln["priority"],
                "module": "SOFTWARE",
                "title": f"{name} {version}",
                "reason": vuln["reason"],
                "recommendation": vuln["recommendation"]

            })

            continue

        #
        # Installed software worth checking
        #
        findings.append({

            "priority": "MEDIUM",
            "module": "SOFTWARE",
            "title": f"{name} {version}",
            "reason": info["reason"],
            "recommendation": info["recommendation"]

        })

    return {

        "module": "SOFTWARE",

        "summary": {

            "Detected": ", ".join(detected) if detected else "-",
            "Total": len(detected)

        },

        "findings": findings,

        "details": {

            "software": detected

        }

    }
