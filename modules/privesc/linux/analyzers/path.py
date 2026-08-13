"""
CTFKit - PATH Analyzer
"""

import os


STANDARD_PATHS = {
    "/bin",
    "/sbin",
    "/usr/bin",
    "/usr/sbin",
    "/usr/local/bin",
    "/usr/local/sbin",
    "/usr/games",
    "/usr/local/games",
    "/snap/bin",
}


def analyze(text):

    findings = []

    entries = []
    seen = set()

    #
    # Parse PATH
    #
    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if line.startswith(">>>"):
            continue

        if line.startswith("/"):
            entries = line.split(":")
            break

    duplicate_count = 0
    writable_count = 0
    nonstandard_count = 0

    #
    # Analyze entries
    #
    for entry in entries:

        #
        # Empty entry (::)
        #
        if entry == "":

            findings.append({

                "priority": "HIGH",

                "module": "path",

                "title": "Empty PATH entry",

                "reason": "An empty PATH entry resolves to the current working directory.",

                "recommendation": [
                    "Review for PATH hijacking opportunities."
                ]
            })

            continue

        #
        # Current directory
        #
        if entry == ".":

            findings.append({

                "priority": "HIGH",

                "module": "path",

                "title": ".",

                "reason": "Current working directory appears in PATH.",

                "recommendation": [
                    "Review for PATH hijacking opportunities."
                ]
            })

        #
        # Duplicate
        #
        if entry in seen:
            duplicate_count += 1
        else:
            seen.add(entry)

        #
        # Writable
        #
        if os.path.isdir(entry) and os.access(entry, os.W_OK):

            writable_count += 1

            findings.append({

                "priority": "HIGH",

                "module": "path",

                "title": entry,

                "reason": "Writable directory appears in PATH.",

                "recommendation": [
                    "Review for PATH hijacking opportunities."
                ]
            })

        #
        # Non-standard
        #
        if entry not in STANDARD_PATHS:

            nonstandard_count += 1

            findings.append({

                "priority": "MEDIUM",

                "module": "path",

                "title": entry,

                "reason": "Non-standard PATH entry detected.",

                "recommendation": [
                    "Verify whether privileged programs execute commands from this location."
                ]
            })

    return {

        "module": "PATH",

        "summary": {

            "Entries": len(entries),
            "Writable": writable_count,
            "Non-standard": nonstandard_count,
            "Duplicates": duplicate_count,

        },

        "findings": findings,

    }
