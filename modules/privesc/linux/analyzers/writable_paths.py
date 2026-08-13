"""
CTFKit - Writable Files & Directories Analyzer
"""


HIGH_FILES = {
    "/etc/passwd": (
        "HIGH",
        "Writable /etc/passwd",
        "Writable by the current user. User entries may be modified.",
    ),
    "/etc/shadow": (
        "HIGH",
        "Writable /etc/shadow",
        "Writable by the current user. Password hashes may be modified.",
    ),
    "/etc/sudoers": (
        "HIGH",
        "Writable /etc/sudoers",
        "Writable by the current user. Sudo policy may be modified.",
    ),
    "/etc/crontab": (
        "HIGH",
        "Writable /etc/crontab",
        "Writable by the current user. Scheduled root jobs may be modified.",
    ),
    "/etc/ld.so.preload": (
        "HIGH",
        "Writable /etc/ld.so.preload",
        "Writable by the current user. Shared libraries can be forced into privileged processes.",
    ),
    "/etc/profile": (
        "MEDIUM",
        "Writable /etc/profile",
        "Writable by the current user. Commands execute for future login shells.",
    ),
}


HIGH_PREFIXES = {
    "/etc/sudoers.d/": (
        "HIGH",
        "Writable sudoers.d file",
        "Writable sudo configuration detected.",
    ),
    "/etc/cron.": (
        "HIGH",
        "Writable cron file",
        "Writable cron configuration detected.",
    ),
    "/etc/profile.d/": (
        "MEDIUM",
        "Writable profile.d file",
        "Writable shell initialization script detected.",
    ),
}


INTERESTING_DIRS = {
    "/usr/local/bin": "Writable executable directory.",
    "/usr/local/sbin": "Writable executable directory.",
    "/opt": "Writable application directory.",
    "/etc/profile.d": "Writable shell initialization directory.",
}


def analyze(text):

    findings = []

    writable_dirs = []
    writable_files = []

    current = None

    #
    # Parse enumeration
    #
    for line in text.splitlines():

        line = line.strip()

        if line.startswith(">>> COMMAND:"):

            if "type d" in line:
                current = writable_dirs

            elif "type f" in line:
                current = writable_files

            else:
                current = None

            continue

        if not current:
            pass

        if current is None:
            continue

        if not line:
            continue

        if line.startswith(">>>"):
            continue

        current.append(line)

    #
    # Files
    #
    for path in writable_files:

        if path in HIGH_FILES:

            priority, title, reason = HIGH_FILES[path]

            findings.append({

                "priority": priority,

                "module": "writable",

                "title": path,

                "reason": reason,

                "recommendation": [
                    "Review the file for privilege escalation opportunities."
                ]
            })

            continue

        for prefix in HIGH_PREFIXES:

            if path.startswith(prefix):

                priority, title, reason = HIGH_PREFIXES[prefix]

                findings.append({

                    "priority": priority,

                    "module": "writable",

                    "title": path,

                    "reason": reason,

                    "recommendation": [
                        "Review the file for privilege escalation opportunities."
                    ]
                })

                break

    #
    # Directories
    #
    for path in writable_dirs:

        if path not in INTERESTING_DIRS:
            continue

        findings.append({

            "priority": "MEDIUM",

            "module": "writable",

            "title": path,

            "reason": INTERESTING_DIRS[path],

            "recommendation": [
                "Review whether executables or scripts can be placed here."
            ]
        })

    #
    # Report
    #
    return {

        "module": "Writable Files & Directories",

        "summary": {

            "Findings": len(findings),
            "Writable Files": len(writable_files),
            "Writable Directories": len(writable_dirs),

        },

        "findings": findings,

    }
