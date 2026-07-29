"""Static, evidence-based analysis of cron and systemd scheduled jobs.

The collector deliberately records filesystem metadata separately from job text.
That lets this module distinguish an actual writable execution path from a
generic writable file elsewhere on the host, which is the difference between a
useful lead and a false positive.
"""

from __future__ import annotations

import os
import re
import shlex
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Dict, Iterable, List, Optional, Set


CRON_SYSTEM_ENTRY = re.compile(
    r"^(?P<schedule>\S+\s+\S+\s+\S+\s+\S+\s+\S+)\s+(?P<user>\S+)\s+(?P<command>.+)$"
)
CRON_USER_ENTRY = re.compile(r"^(?P<schedule>\S+\s+\S+\s+\S+\s+\S+\s+\S+)\s+(?P<command>.+)$")
CRON_SPECIAL = re.compile(r"^(?P<schedule>@\w+)\s+(?:(?P<user>\S+)\s+)?(?P<command>.+)$")
PATH_ASSIGNMENT = re.compile(r"^\s*(?:export\s+)?PATH\s*=\s*([^\s#]+)")
ABSOLUTE_PATH = re.compile(r"(?<![\w$])(/[\w.@+,:=~%/\-]+)")
FILE_MARKER = re.compile(r"^>>> FILE: (.+)$")
META_LINE = re.compile(r"^(?P<mode>[dlcbps-][rwxstST-]{9})\|(?P<owner>[^|]+)\|(?P<group>[^|]+)\|(?P<path>/.*)$")

SHELL_WORDS = {"[", "[[", "cd", "do", "done", "elif", "else", "esac", "fi", "for", "function", "if", "in",
               "test", "then", "until", "while", "(" , ")"}
STANDARD_CRON_DIRS = {"/etc/cron.hourly", "/etc/cron.daily", "/etc/cron.weekly", "/etc/cron.monthly"}
SCHEDULED_SCRIPT_NAMES = ("backup", "archive", "rotate", "cleanup", "maintenance")


PLAYBOOKS = {
    "WORLD_WRITABLE": "ctf privesc.linux.cron.writable",
    "GROUP_WRITABLE": "ctf privesc.linux.cron.group",
    "PATH_HIJACK": "ctf privesc.linux.cron.path",
    "WILDCARD": "ctf privesc.linux.cron.wildcard",
    "SYSTEMD": "ctf privesc.linux.systemd.timer",
}

@dataclass
class Job:
    schedule: str
    user: str
    command: str
    source: str
    path: Optional[str] = None
    inherited_path: Optional[str] = None
    kind: str = "cron"


@dataclass
class Metadata:
    mode: str
    owner: str
    group: str
    path: str

    @property
    def world_writable(self) -> bool:
        return len(self.mode) >= 9 and self.mode[8] == "w"

    @property
    def group_writable(self) -> bool:
        return len(self.mode) >= 6 and self.mode[5] == "w"


def _split_commands(section: str) -> Dict[str, str]:
    """Return command output from the project's ``>>> COMMAND:`` transcript."""
    commands: Dict[str, List[str]] = {}
    current: Optional[str] = None
    for line in section.splitlines():
        if line.startswith(">>> COMMAND:"):
            current = line.split(">>> COMMAND:", 1)[1].strip()
            commands.setdefault(current, [])
        elif current is not None:
            commands[current].append(line)
    return {command: "\n".join(output) for command, output in commands.items()}


def _outputs_containing(commands: Dict[str, str], needle: str) -> Iterable[str]:
    for command, output in commands.items():
        if needle in command:
            yield output


def _strip_comment(line: str) -> str:
    # Cron has no reliable quote-aware comment grammar; preserving quoted '#'
    # avoids dropping shell arguments while still handling the usual case.
    quote = ""
    for index, char in enumerate(line):
        if char in "'\"" and (index == 0 or line[index - 1] != "\\"):
            quote = "" if quote == char else (char if not quote else quote)
        if char == "#" and not quote and (index == 0 or line[index - 1].isspace()):
            return line[:index]
    return line


def _file_blocks(text: str) -> Dict[str, str]:
    blocks: Dict[str, List[str]] = {}
    current: Optional[str] = None
    for line in text.splitlines():
        marker = FILE_MARKER.match(line)
        if marker:
            current = marker.group(1).strip()
            blocks.setdefault(current, [])
        elif current is not None:
            blocks[current].append(line)
    return {path: "\n".join(lines) for path, lines in blocks.items()}


def _parse_jobs(contents: str, source: str, default_user: str = "unknown") -> List[Job]:
    jobs: List[Job] = []
    path_value: Optional[str] = None
    system_format = source == "/etc/crontab" or source.startswith("/etc/cron.d/")
    for raw in contents.splitlines():
        line = _strip_comment(raw).strip()
        if not line:
            continue
        assignment = PATH_ASSIGNMENT.match(line)
        if assignment:
            path_value = assignment.group(1).strip("'\"")
            continue
        special = CRON_SPECIAL.match(line)
        match = special or (CRON_SYSTEM_ENTRY.match(line) if system_format else CRON_USER_ENTRY.match(line))
        if not match:
            continue
        groups = match.groupdict()
        jobs.append(Job(groups["schedule"], groups.get("user") or default_user,
                        groups["command"], source, inherited_path=path_value))
    return jobs


def _parse_systemd_jobs(contents: str, source: str) -> List[Job]:
    """Extract ExecStart directives from a collected service unit.

    Unit files can set ``User=``; absent that setting system services normally
    run as root, which is also systemd's default when ``User=`` is absent.
    """
    user = "root"
    jobs: List[Job] = []
    for line in contents.splitlines():
        if line.startswith("User="):
            user = line.split("=", 1)[1].strip() or "unknown"
        if line.startswith("ExecStart="):
            command = line.split("=", 1)[1].lstrip("-@:+!").strip()
            if command:
                jobs.append(Job("systemd timer", user, command, source, kind="systemd"))
    return jobs


def _metadata(outputs: Iterable[str]) -> Dict[str, Metadata]:
    result: Dict[str, Metadata] = {}
    for output in outputs:
        for line in output.splitlines():
            match = META_LINE.match(line.strip())
            if match:
                item = Metadata(**match.groupdict())
                result[item.path] = item
    return result


def _normalise(path: str) -> str:
    return os.path.normpath(path.rstrip(";,:"))


def _paths_in_command(command: str) -> Set[str]:
    return {_normalise(match.group(1)) for match in ABSOLUTE_PATH.finditer(command)}


def _first_executable(command: str) -> Optional[str]:
    try:
        tokens = shlex.split(command, comments=False)
    except ValueError:
        return None
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in {";", "&&", "||", "|"}:
            index += 1
            continue
        if "=" in token and not token.startswith("/") and token.split("=", 1)[0].replace("_", "").isalnum():
            index += 1
            continue
        return token
    return None


def _is_untrusted_path_dir(path_value: Optional[str], metadata: Dict[str, Metadata]) -> List[str]:
    if not path_value:
        return []
    # Metadata is intentionally sparse: the collector records all cron paths
    # but only writable paths elsewhere.  Missing metadata is therefore not
    # evidence of a writable directory.
    return [directory for directory in path_value.split(":")
            if directory in {".", ""} or (metadata.get(directory) and metadata[directory].world_writable)]


def _finding(priority, title, reason, evidence,
             recommendation=None,
             playbook=None):

    finding = {
        "priority": priority,
        "module": "CRON",
        "title": title,
        "reason": f"{reason} Evidence: {evidence}",
        "recommendation": []
    }

    if recommendation:
        finding["recommendation"].append(recommendation)

    if playbook:
        finding["recommendation"].append(f"Run: {playbook}")

    return finding


def _job_findings(job: Job, metadata: Dict[str, Metadata]) -> List[dict]:
    findings: List[dict] = []
    subject = f"{job.source}: {job.command}"
    paths = _paths_in_command(job.command)

    if job.path:
        paths.add(job.path)

    for path in sorted(paths):
        item = metadata.get(path)
        if not item:
            continue

        if item.world_writable:
            findings.append(_finding(
                "HIGH",
                subject,
                "Scheduled job references a world-writable path.",
                f"{path} is {item.mode} ({item.owner}:{item.group}).",
                playbook=f"{PLAYBOOKS['WORLD_WRITABLE']} {path}",
            ))

        elif item.group_writable and item.group not in {"root", "wheel"}:
            findings.append(_finding(
                "MEDIUM",
                subject,
                "Scheduled job references a group-writable path.",
                f"{path} is {item.mode} ({item.owner}:{item.group}).",
                playbook=PLAYBOOKS["GROUP_WRITABLE"]
            ))

        parent = str(PurePosixPath(path).parent)
        parent_meta = metadata.get(parent)

        if parent_meta and parent_meta.world_writable:
            findings.append(_finding(
                "HIGH",
                subject,
                "Scheduled job resolves a path from a world-writable directory.",
                f"Parent {parent} is {parent_meta.mode}.",
                playbook=PLAYBOOKS["WORLD_WRITABLE"]
            ))

    executable = _first_executable(job.command)

    if executable and "/" not in executable and executable not in SHELL_WORDS:
        risky_dirs = _is_untrusted_path_dir(job.inherited_path, metadata)

        if risky_dirs:
            findings.append(_finding(
                "HIGH",
                subject,
                "Bare executable may be resolved through an untrusted PATH directory.",
                f"Executable '{executable}', PATH={job.inherited_path}; risky entries: {', '.join(risky_dirs)}.",
                playbook=PLAYBOOKS["PATH_HIJACK"]
            ))

    if re.search(r"\b(?:tar|rsync|cp|find)\b[^\n]*(?:\s\*|\*/|--files-from)", job.command):
        findings.append(_finding(
            "MEDIUM",
            subject,
            "Scheduled command uses a wildcard-sensitive utility.",
            f"Command: {job.command}",
            playbook=PLAYBOOKS["WILDCARD"]
        ))

    return findings


def _expand_run_parts(jobs: Iterable[Job], metadata: Dict[str, Metadata]) -> List[Job]:
    """Model scripts invoked by run-parts as individual scheduled execution paths."""
    expanded: List[Job] = []
    for job in jobs:
        directories = [path for path in _paths_in_command(job.command) if path in STANDARD_CRON_DIRS]
        for directory in directories:
            prefix = directory.rstrip("/") + "/"
            for path, item in metadata.items():
                if path.startswith(prefix) and "/" not in path[len(prefix):] and item.mode.startswith("-"):
                    expanded.append(Job(job.schedule, job.user, path, f"{job.source} (run-parts)", path=path,
                                        inherited_path=job.inherited_path))
    return expanded


def _execution_paths(jobs: Iterable[Job]) -> Set[str]:
    paths: Set[str] = set()
    for job in jobs:
        paths.update(_paths_in_command(job.command))
        if job.path:
            paths.add(job.path)
    return paths


def _unlinked_script_candidates(metadata: Dict[str, Metadata], known_paths: Set[str]) -> List[dict]:
    """Surface common CTF leads when the responsible cron source is unreadable.

    A writable ``backup.sh`` does not prove scheduled execution. It does merit
    a clearly labelled lead when both its name and permissions resemble a
    scheduled administrative script; runtime observation supplies the proof.
    """
    findings: List[dict] = []
    for path, item in metadata.items():
        basename = PurePosixPath(path).name.lower()
        executable = item.mode.startswith("-") and "x" in item.mode[1:]
        scheduled_name = any(word in basename for word in SCHEDULED_SCRIPT_NAMES)
        if path in known_paths or not executable or not item.world_writable or not scheduled_name:
            continue
        parent = str(PurePosixPath(path).parent)
        parent_meta = metadata.get(parent)
        evidence = f"{path} is {item.mode} ({item.owner}:{item.group})"
        if parent_meta and parent_meta.world_writable:
            evidence += f"; parent {parent} is also {parent_meta.mode}"
        findings.append(_finding(
            "HIGH", path,
            "Potential scheduled administrative script is world writable, but no static cron or timer reference was collected.",
            evidence + ".",
            "Inspect the script and use pspy to confirm the executing UID and command line.",
            playbook=f"{PLAYBOOKS['WORLD_WRITABLE']} {path}"
        ))
    return findings


def analyze(section: str) -> dict:
    """Analyze a CRON transcript. Missing enhanced collector data degrades safely."""
    commands = _split_commands(section)
    blocks: Dict[str, str] = {}
    for output in commands.values():
        # The cron and systemd collector commands both use the same unambiguous
        # marker, so a future collector can add another source without parser
        # changes.
        blocks.update(_file_blocks(output))

    # Backwards-compatible parsing for the original collector.
    if not blocks:
        crontab = commands.get("cat /etc/crontab", "")
        if crontab:
            blocks["/etc/crontab"] = crontab
    jobs: List[Job] = []
    for source, content in blocks.items():
        if source.startswith("systemd:") and source.endswith(".service"):
            jobs.extend(_parse_systemd_jobs(content, source))
        elif source == "/etc/crontab" or source.startswith("/etc/cron.d/"):
            jobs.extend(_parse_jobs(content, source))
    for command, output in commands.items():
        if "crontab -l" not in command:
            continue
        if "no crontab for" not in output.lower():
            default_user = "root" if "sudo -n crontab -l" in command else "current-user"
            jobs.extend(_parse_jobs(output, f"{default_user} crontab", default_user=default_user))

    metadata = _metadata(_outputs_containing(commands, "CRON_PATH_METADATA"))
    metadata.update(_metadata(_outputs_containing(commands, "SYSTEMD_UNIT_METADATA")))
    if not metadata:  # old ``ls -l`` output cannot prove writable path reliably
        metadata = _metadata(_outputs_containing(commands, "find /etc/cron"))
    jobs.extend(_expand_run_parts(jobs, metadata))
    findings: List[dict] = []
    seen: Set[tuple] = set()
    for job in jobs:
        for finding in _job_findings(job, metadata):
            key = (finding["priority"], finding["title"], finding["reason"])
            if key not in seen:
                seen.add(key)
                findings.append(finding)

    candidates = _unlinked_script_candidates(metadata, _execution_paths(jobs))
    findings.extend(candidates)

    for path, item in metadata.items():
        if (path == "/etc/crontab" or path.startswith("/etc/cron.d/")) and item.world_writable:
            findings.append(_finding("HIGH", path, "Cron definition file is world writable.",
                                     f"{path} is {item.mode} ({item.owner}:{item.group}).",
                                     "Remove write access for untrusted users and review scheduled entries."))

    root_jobs = sum(job.user == "root" for job in jobs)
    return {"module": "CRON",
            "summary": {"Jobs": len(jobs), "Root jobs": root_jobs,
                        "Cron sources": len(blocks), "Observed paths": len(metadata),
                        "Actionable findings": len(findings),
                        "Unlinked candidates": len(candidates)},
            "findings": findings,
            "details": {"jobs": [job.__dict__ for job in jobs],
                        "metadata": {path: item.__dict__ for path, item in metadata.items()}}}
