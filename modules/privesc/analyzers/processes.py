import os
import re

MODULE = "PROCESSES"

SCRIPT_EXTENSIONS = (
    ".sh",
    ".py",
    ".pl",
    ".rb",
    ".php",
    ".lua",
    ".tcl",
)

INTERESTING_DIRS = (
    "/opt/",
    "/home/",
    "/srv/",
    "/tmp/",
    "/dev/shm/",
    "/var/tmp/",
)

IGNORE_EXECUTABLES = {
    "systemd",
    "systemd-journald",
    "systemd-logind",
    "systemd-resolved",
    "systemd-timesyncd",
    "dbus-daemon",
    "networkd-dispatcher",
    "dhclient",
    "cron",
    "atd",
    "sshd",
    "apache2",
    "mysqld",
    "snapd",
    "polkitd",
    "rsyslogd",
    "agetty",
    "vmtoolsd",
    "VGAuthService",
    "accounts-daemon",
    "irqbalance",
    "multipathd",
}

BACKUP_EXECUTABLES = {
    "tar",
    "rsync",
    "cpio",
    "zip",
    "unzip",
}

CREDENTIAL_PATTERNS = (
    r"--password(?:=|\s+\S+)",
    r"--passwd(?:=|\s+\S+)",
    r"password=",
    r"passwd=",
    r"token=",
    r"apikey=",
    r"api_key=",
    r"secret=",
    r"Authorization:\s*Bearer",
    r"sshpass\s+-p\s+\S+",
    r"\bmysql\b.*-p\S+",
)


def executable(command):
    first = command.split()[0]

    if first.startswith("["):
        return None

    return os.path.basename(first)


def analyze(section):

    findings = []
    seen = set()
    process_count = 0

    for line in section.splitlines():

        line = line.strip()

        if (
            not line
            or line.startswith("#")
            or line.startswith(">>>")
            or line.startswith("USER")
        ):
            continue

        parts = line.split(None, 10)

        if len(parts) < 11:
            continue

        process_count += 1

        user = parts[0]
        command = parts[10]

        exe = executable(command)

        #
        # Ignore kernel threads
        #
        if exe is None:
            continue

        #
        # Ignore common OS daemons
        #
        if exe in IGNORE_EXECUTABLES:
            continue

        #
        # Credentials
        #
        if any(re.search(p, command, re.IGNORECASE) for p in CREDENTIAL_PATTERNS):

            if command not in seen:
                seen.add(command)

                findings.append({
                    "priority": "HIGH",
                    "module": MODULE,
                    "title": command,
                    "reason": "Credentials appear to be exposed in the process arguments.",
                    "recommendation": [
                        "Review the process arguments for exposed credentials."
                    ]
                })

            continue

        #
        # Root executing scripts
        #
        if user == "root":

            if any(command.endswith(ext) or f"{ext} " in command for ext in SCRIPT_EXTENSIONS):

                if command not in seen:
                    seen.add(command)

                    findings.append({
                        "priority": "HIGH",
                        "module": MODULE,
                        "title": command,
                        "reason": "Root is executing a script.",
                        "recommendation": [
                            "Inspect the script.",
                            "Check permissions.",
                            "Review imported modules."
                        ]
                    })

                continue

        #
        # Root executing custom software
        #
        if user == "root":

            if any(d in command for d in INTERESTING_DIRS):

                if command not in seen:
                    seen.add(command)

                    findings.append({
                        "priority": "HIGH",
                        "module": MODULE,
                        "title": command,
                        "reason": "Root is executing software from a non-standard location.",
                        "recommendation": [
                            "Inspect the executable.",
                            "Check ownership and permissions.",
                            "Review related configuration files."
                        ]
                    })

                continue

        #
        # Backup utilities
        #
        if exe in BACKUP_EXECUTABLES:

            if command not in seen:
                seen.add(command)

                findings.append({
                    "priority": "MEDIUM",
                    "module": MODULE,
                    "title": command,
                    "reason": "Backup or archive utility detected.",
                    "recommendation": [
                        "Inspect for wildcard injection opportunities.",
                        "Review how the utility is executed."
                    ]
                })

    return {
        "module": MODULE,
        "summary": {
            "Processes": process_count,
            "Findings": len(findings),
        },
        "findings": findings,
    }