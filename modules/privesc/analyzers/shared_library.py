"""
CTFKit - Shared Libraries Analyzer
"""


def analyze(text):

    findings = []
    entries = []
    current = None

    #
    # Parse enumeration output
    #
    for line in text.splitlines():

        line = line.strip()

        if line.startswith("=================================================="):

            if current:
                entries.append(current)

            current = {}
            continue

        if current is None:
            continue

        if line.startswith("Binary :"):
            current["binary"] = line.split(":", 1)[1].strip()

        elif line.startswith("Path   :"):
            current["path"] = line.split(":", 1)[1].strip()

        elif line.startswith("Status :"):
            current["status"] = line.split(":", 1)[1].strip()

    if current:
        entries.append(current)

    #
    # Analyze
    #
    for entry in entries:

        if entry.get("status") != "WRITABLE":
            continue

        findings.append({

            "priority": "HIGH",

            "module": "shared_object",

            "title": entry["binary"],

            "reason": f"Writable RUNPATH: {entry['path']}",

            "recommendation": [
                f"Run: ctf privesc.linux.suid.shared_object {entry['binary']} {entry['path']}"
            ]
        })

    #
    # Report
    #
    return {

        "module": "Shared Libraries",

        "summary": {
            "Findings": len(findings),
            "Writable Paths": len(findings),
        },

        "findings": findings,
    }