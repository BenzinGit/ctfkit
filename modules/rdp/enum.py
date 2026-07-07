import re
import subprocess

from core.paths import (
    get_artifacts_dir,
    get_tool_path
)


PROVIDES = []
REQUIRES = ["ip"]


def run(data, cred, args):

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    W = '\033[0m'
    R = '\033[91m'
    M = '\033[95m'


    windows = getattr(
        args,
        "windows",
        False
    )
    if windows:
        print(
            f"\n{B}┌── Windows "
            f"──────────────────────────────────────┐{W}"
        )
        print()
        print(f'{Y}Get-NetLocalGroupMember -ComputerName ACADEMY-EA-MS01 -GroupName "Remote Desktop Users"')
        

        print(
            f"\n{B}└──────────────────────────────────────────────┘{W}\n"
        )
        return

    reference = getattr(
        args,
        "reference",
        False
    )

    # -----------------------------
    # REFERENCE
    # -----------------------------

    if reference:

        print(
            f"\n{B}┌── REFERENCE "
            f"──────────────────────────────────────┐{W}"
        )

        print()

        print(
            f"{Y}nmap "
            f"-sV -sC "
            f"-p3389 "
            f"--script rdp* "
            f"{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}rdp-sec-check.pl "
            f"{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}xfreerdp "
            f"/u:{M}<USER>{W} "
            f"/p:{M}<PASS>{W} "
            f"/v:{M}<IP>{W}"
        )

        print(
            f"\n{B}└──────────────────────────────────────────────┘{W}\n"
        )
        print(
            f"\n{B}┌── Windows "
            f"──────────────────────────────────────┐{W}"
        )
        print()
        print(f'{Y}Get-NetLocalGroupMember -ComputerName ACADEMY-EA-MS01 -GroupName "Remote Desktop Users"')
        

        print(
            f"\n{B}└──────────────────────────────────────────────┘{W}\n"
        )

        return

    # -----------------------------
    # TARGET
    # -----------------------------

    ip = data.get(
        "ip"
    )

    if not ip:

        print(
            f"\n{R}[!]{W} "
            f"No target IP loaded."
        )

        return

    target_name = data.get(
        "name",
        "unknown"
    )

    # -----------------------------
    # TOOLS
    # -----------------------------

    rdp_sec_check = get_tool_path(
        "rdp-sec-check.pl"
    )

    # -----------------------------
    # ARTIFACTS
    # -----------------------------

    artifact_dir = (
        get_artifacts_dir(
            target_name
        )
        / "rdp"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: RDP ENUMERATION "
        f"────────────────────┐{W}"
    )

    print(
        f"{B}│{W} "
        f"TARGET: "
        f"{C}{ip:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└───────────────────────────────────────────────┘{W}"
    )

    # -----------------------------
    # NMAP
    # -----------------------------

    nmap_cmd = (
        f"nmap "
        f"-sV -sC "
        f"-p3389 "
        f"--script rdp* "
        f"{ip}"
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"SERVICE DETECTION\n"
    )

    print(
        f"{Y}{nmap_cmd}{W}\n"
    )

    result = subprocess.run(
        nmap_cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    nmap_output = (
        result.stdout
        + result.stderr
    )

    print(
        nmap_output
    )

    (
        artifact_dir
        / "service_detection.txt"
    ).write_text(
        nmap_output
    )

    # -----------------------------
    # RDP SECURITY CHECK
    # -----------------------------

    if rdp_sec_check.exists():

        sec_cmd = (
            f"perl "
            f"{rdp_sec_check} "
            f"{ip}"
        )

        print(
            f"\n{B}[{W}{G}*{W}{B}]{W} "
            f"SECURITY CHECK\n"
        )

        print(
            f"{Y}{sec_cmd}{W}\n"
        )

        result = subprocess.run(
            sec_cmd,
            shell=True,
            capture_output=True,
            text=True
        )

        sec_output = (
            result.stdout
            + result.stderr
        )

        print(
            sec_output
        )

        (
            artifact_dir
            / "security_check.txt"
        ).write_text(
            sec_output
        )

    else:

        sec_output = ""

        print(
            f"\n{Y}[!]{W} "
            f"rdp-sec-check.pl not found:"
        )

        print(
            f"{C}{rdp_sec_check}{W}"
        )

    # -----------------------------
    # SUMMARY
    # -----------------------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"SUMMARY\n"
    )

    hostname = re.search(
        r"DNS_Computer_Name:\s*(.+)",
        nmap_output
    )

    domain = re.search(
        r"DNS_Domain_Name:\s*(.+)",
        nmap_output
    )

    version = re.search(
        r"Product_Version:\s*(.+)",
        nmap_output
    )

    nla = (
        "CredSSP (NLA): SUCCESS"
        in nmap_output
    )

    if hostname:

        print(
            f"{G}[+]{W} "
            f"Hostname:"
        )

        print(
            f"    {C}{hostname.group(1).strip()}{W}"
        )

        print()

    if domain:

        value = (
            domain.group(1)
            .strip()
        )

        if value:

            print(
                f"{G}[+]{W} "
                f"Domain:"
            )

            print(
                f"    {C}{value}{W}"
            )

            print()

    if version:

        print(
            f"{G}[+]{W} "
            f"Product Version:"
        )

        print(
            f"    {C}{version.group(1).strip()}{W}"
        )

        print()

    print(
        f"{G}[+]{W} "
        f"NLA:"
    )

    print(
        f"    {C}{'Enabled' if nla else 'Unknown'}{W}"
    )

    print()

    # -----------------------------
    # RESULTS
    # -----------------------------

    print(
        f"{G}[+]{W} "
        f"Results saved:"
    )

    print(
        f"{C}{artifact_dir}{W}"
    )

    print()
