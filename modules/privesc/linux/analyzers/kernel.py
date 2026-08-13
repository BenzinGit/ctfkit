import re


KERNEL_EXPLOITS = [

    {
        "name": "Dirty COW",
        "cve": "CVE-2016-5195",
        "affected": [
            "2.6",
            "3.",
            "4.4"
        ],
        "reference": "https://dirtycow.ninja/"
    },

    {
        "name": "OverlayFS",
        "cve": "CVE-2015-1328",
        "affected": [
            "3.13",
            "3.16",
            "3.19"
        ],
        "reference": "https://www.exploit-db.com/exploits/37292"
    },

    {
        "name": "OverlayFS",
        "cve": "CVE-2021-3493",
        "affected": [
            "4.4",
            "4.15",
            "5.4",
            "5.8"
        ],
        "reference": "https://github.com/v4resk/red-book/blob/main/redteam/privilege-escalation/linux/kernel-exploits/overlayfs-exploits/cve-2021-3493.md"
    },

    {
        "name": "Dirty Pipe",
        "cve": "CVE-2022-0847",
        "affected": [
            "5.8",
            "5.9",
            "5.10",
            "5.11",
            "5.12",
            "5.13",
            "5.14",
            "5.15"
        ],
        "reference": "https://github.com/Arinerron/CVE-2022-0847-DirtyPipe-Exploit"
    },

]

import re


def analyze(text):

    findings = []

    #
    # Kernel
    #

    kernel = "Unknown"

    m = re.search(r"Linux\s+\S+\s+([^\s]+)", text)
    if m:
        kernel = m.group(1)

    #
    # OS
    #

    distro = "Unknown"

    m = re.search(r'DISTRIB_DESCRIPTION="([^"]+)"', text)
    if m:
        distro = m.group(1)

    #
    # Architecture
    #

    architecture = "Unknown"

    m = re.search(
        r"\b(x86_64|amd64|i[3-6]86|aarch64|arm64|armv\d+l?)\b",
        text
    )

    if m:
        architecture = m.group(1)

    #
    # Knowledge base
    #

    matches = 0

    for exploit in KERNEL_EXPLOITS:

        vulnerable = False

        for version in exploit["affected"]:

            if kernel.startswith(version):

                vulnerable = True
                break

        if not vulnerable:
            continue

        matches += 1

        recommendation = []

        if exploit.get("module"):
            recommendation.append(
                f"Run: {exploit['module']}"
            )

        if exploit.get("reference"):
            recommendation.append(
                f"Reference: {exploit['reference']}"
            )

        findings.append({

            "priority": "HIGH",
            "module": "KERNEL",
            "title": f"{exploit['name']} ({exploit['cve']})",
            "reason": f"Kernel {kernel} matches the affected versions for this privilege escalation vulnerability.",
            "recommendation": recommendation

        })

    #
    # Unknown kernel
    #

    if matches == 0 and kernel != "Unknown":

        findings.append({

            "priority": "MEDIUM",
            "module": "KERNEL",
            "title": kernel,
            "reason": "Kernel version identified. Investigate whether public privilege escalation exploits exist.",
            "recommendation": [
                "Search: searchsploit linux kernel",
                "Search Exploit-DB",
                "Search GitHub for PoCs"
            ]

        })

    return {

        "module": "KERNEL",

        "summary": {

            "Kernel": kernel,
            "OS": distro,
            "Architecture": architecture,
            "Matches": matches

        },

        "findings": findings,

        "details": {

            "Kernel": kernel,
            "OS": distro,
            "Architecture": architecture

        }

    }