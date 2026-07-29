"""
CTFKit - Linux PrivEsc
NFS Analyzer
"""

import re


# ==========================================
# KNOWLEDGE BASE
# ==========================================

NFS = {

    "no_root_squash": {

        "priority": "HIGH",

        "reason": (
            "NFS export allows remote root users to create root-owned "
            "SUID files."
        )

    },

    "root_squash": {

        "priority": "INFO",

        "reason": (
            "NFS export uses 'root_squash'. The standard NFS SUID "
            "upload attack is not possible."
        )

    }

}


# ==========================================
# PARSER
# ==========================================

def _parse(section):

    exports = []

    for line in section.splitlines():

        line = line.strip()

        if (
            not line or
            line.startswith("#") or
            line.startswith(">>>")
        ):
            continue

        #
        # /tmp *(rw,no_root_squash)
        #
        match = re.match(r"^(\S+)\s+.*\(([^)]*)\)", line)

        if not match:
            continue

        path = match.group(1)

        options = [
            option.strip()
            for option in match.group(2).split(",")
        ]

        exports.append({

            "path": path,
            "options": options

        })

    return exports


# ==========================================
# PUBLIC API
# ==========================================

def analyze(section):

    exports = _parse(section)

    findings = []

    vulnerable = []

    for export in exports:

        path = export["path"]
        options = export["options"]

        #
        # Vulnerable
        #
        if "no_root_squash" in options:

            vulnerable.append(path)

            findings.append({

                "priority": "HIGH",

                "module": "NFS",

                "title": f"no_root_squash ({path})",

                "reason": NFS["no_root_squash"]["reason"],

                "recommendation": [

                    f"Export: {path}",
                    f"Run: ctf privesc.linux.nfs.shell {path}"

                ]

            })

        #
        # Safe
        #
        elif "root_squash" in options:

            findings.append({

                "priority": "INFO",

                "module": "NFS",

                "title": f"root_squash ({path})",

                "reason": NFS["root_squash"]["reason"],

                "recommendation": [

                    f"Export: {path}"

                ]

            })

    return {

        "module": "NFS",

        "summary": {

            "Vulnerable": len(vulnerable),
            "Exports": ", ".join(
                export["path"] for export in exports
            ) if exports else "-"

        },

        "findings": findings,

        "details": {

            "exports": exports,
            "vulnerable": vulnerable

        }

    }