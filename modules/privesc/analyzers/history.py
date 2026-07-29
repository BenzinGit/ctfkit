import re


def _get_history_files(section):
    """
    Returns:
        [
            ("/home/user/.bash_history", "<contents>"),
            ...
        ]
    """
    pattern = r"^>>> FILE:\s*(.+?)\n(.*?)(?=^>>> FILE:|\Z)"
    return re.findall(pattern, section, re.MULTILINE | re.DOTALL)


def analyze(section):

    history_files = _get_history_files(section)

    findings = []

    seen = set()

    high_patterns = {
        "Credentials": [
            r"sshpass\b",
            r"password\s*=",
            r"passwd\s*=",
            r"token\s*=",
            r"apikey\s*=",
            r"secret\s*=",
            r"authorization:",
            r"bearer\s",
            r"-p\S+",              # mysql -pPassword
        ],
        "Flag access": [
            r"flag[\w.-]*",
        ],
    }

    medium_patterns = {
        "SSH command": [
            r"\bssh\b",
            r"\bscp\b",
            r"\bsftp\b",
            r"\bssh-keygen\b",
        ],
        "Database command": [
            r"\bmysql\b",
            r"\bpsql\b",
            r"\bmongo\b",
            r"\bredis-cli\b",
        ],
        "Private key reference": [
            r"id_rsa",
            r"id_ed25519",
            r"authorized_keys",
            r"\.pem\b",
            r"\.ppk\b",
        ],
        "Binary analysis": [
            r"\bstrings\b",
        ],
    }

    low_patterns = {
        "History cleanup": [
            r"history\s+-d",
            r"history\s+-c",
        ],
    }

    for filename, contents in history_files:

        for line in contents.splitlines():

            line = line.strip()

            if not line:
                continue

            lower = line.lower()

            #
            # HIGH
            #
            matched = False

            for reason, patterns in high_patterns.items():

                if any(re.search(p, lower) for p in patterns):

                    key = ("HIGH", line)

                    if key not in seen:

                        findings.append({
                            "priority": "HIGH",
                            "module": "history",
                            "title": line,
                            "reason": reason,
                            "recommendation": [
                                filename
                            ],
                        })

                        seen.add(key)

                    matched = True
                    break

            if matched:
                continue

            #
            # MEDIUM
            #
            for reason, patterns in medium_patterns.items():

                if any(re.search(p, lower) for p in patterns):

                    key = ("MEDIUM", line)

                    if key not in seen:

                        findings.append({
                            "priority": "MEDIUM",
                            "module": "history",
                            "title": line,
                            "reason": reason,
                            "recommendation": [
                                filename
                            ],
                        })

                        seen.add(key)

                    matched = True
                    break

            if matched:
                continue

            #
            # LOW
            #
            for reason, patterns in low_patterns.items():

                if any(re.search(p, lower) for p in patterns):

                    key = ("LOW", line)

                    if key not in seen:

                        findings.append({
                            "priority": "LOW",
                            "module": "history",
                            "title": line,
                            "reason": reason,
                            "recommendation": [
                                filename
                            ],
                        })

                        seen.add(key)

                    break

    return {
        "module": "HISTORY",
        "summary": {
            "History Files": len(history_files),
            "Findings": len(findings),
        },
        "findings": findings,
        "report": "\n".join(path for path, _ in history_files),
    }