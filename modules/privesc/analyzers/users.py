from collections import defaultdict
import re


def _get_command_output(section, command):
    pattern = rf">>> COMMAND: {re.escape(command)}\n\n(.*?)(?=\n>>> COMMAND:|\Z)"
    match = re.search(pattern, section, re.S)
    return match.group(1).strip() if match else ""


def analyze(section):

    passwd = _get_command_output(section, "cat /etc/passwd")
    groups = _get_command_output(section, "cat /etc/group")

    users = []
    group_map = defaultdict(list)

    #
    # Parse /etc/passwd
    #
    for line in passwd.splitlines():
        line = line.strip()
        if not line:
            continue

        parts = line.split(":")
        if len(parts) != 7:
            continue

        username, _, uid, _, _, home, shell = parts

        try:
            uid = int(uid)
        except ValueError:
            continue

        users.append({
            "name": username,
            "uid": uid,
            "home": home,
            "shell": shell,
        })

    #
    # Parse /etc/group
    #
    for line in groups.splitlines():
        line = line.strip()
        if not line:
            continue

        parts = line.split(":")
        if len(parts) != 4:
            continue

        group_name = parts[0]

        if not parts[3]:
            continue

        for member in parts[3].split(","):
            member = member.strip()
            if member:
                group_map[member].append(group_name)

    human_users = sorted(
        [u for u in users if u["uid"] >= 1000],
        key=lambda u: u["uid"],
    )

    interesting_accounts = [
        u for u in users
        if u["uid"] < 1000
        and u["shell"] not in (
            "/usr/sbin/nologin",
            "/bin/false",
            "/bin/sync",
        )
    ]

    report = []

    if human_users:
        report.append("Human Users")
        report.append("-" * 11)

        for user in human_users:
            member_of = ", ".join(sorted(group_map.get(user["name"], []))) or "-"

            report.append(
                f"{user['name']:<15}"
                f"{user['home']:<24}"
                f"{user['shell']:<18}"
                f"[{member_of}]"
            )

    if interesting_accounts:
        report.append("")
        report.append("Interesting Accounts")
        report.append("-" * 20)

        for user in interesting_accounts:
            report.append(
                f"{user['name']:<15}"
                f"{user['home']:<24}"
                f"{user['shell']}"
            )

    return {
        "module": "USERS",
        "summary": {
            "Total Users": len(users),
            "Human Users": len(human_users),
            "Service Accounts": len(users) - len(human_users),
        },
        "findings": [],
        "report": "\n".join(report),
    }