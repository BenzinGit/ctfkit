from pathlib import Path
import pyperclip

from core.paths import get_tools_dir
from modules.upload.windows import stage_windows_files
from modules.download.windows import receive_windows_file


G, C, B, Y, W, R = (
        '\033[92m',
        '\033[96m',
        '\033[94m',
        '\033[93m',
        '\033[0m',
        '\033[91m',
)

priority_colors = {
    "HIGH": R,
    "MEDIUM": Y,
    "LOW": B,
}

#
# Section name -> analyzer module
#
ANALYZERS = (
    "privileges",
)


def run(data, cred, args):

    #
    # Analyze existing output
    #
    if hasattr(args, "extra") and args.extra:

        output = Path(args.extra[0])

        if not output.is_file():
            print(f"{R}[-] File not found: {output}{W}")
            return

        analyze(output)

        return


    #
    # Upload enumerator
    #
    enum_script = get_tools_dir() / "windows_enum.ps1"
    stage_windows_files([enum_script])

    helper = r"powershell -ep bypass -File .\windows_enum.ps1"

    pyperclip.copy(helper)

    print()
    print(f"{Y}{helper}")
    print()
    print(f"{G}→ helper command copied to clipboard{W}")

    #
    # Wait for enumeration
    #
    input(
        f"\n{Y}[*] Press ENTER after the enumeration has completed...{W}"
    )

    #
    # Download results
    #
    outfile = Path("windows_enum.txt")

    receive_windows_file(
        outfile=outfile
    )

    #
    # Analyze
    #
    print()

    print(f"{G}[+] Enumeration received.{W}")
    analyze(outfile)


def analyze(outfile):

    import importlib

    modules = {
        name: importlib.import_module(f"modules.privesc.windows.analyzers.{name}")
        for name in ANALYZERS
    }

    #
    # Read enumeration
    #
    text = outfile.read_text(errors="ignore")

    #
    # Split enumeration into sections
    #
    sections = {}

    current = None

    for line in text.splitlines():

        if line.startswith("### BEGIN"):

            current = line.replace("### BEGIN", "").strip()

            sections[current] = []

            continue

        if line.startswith("### END"):

            current = None

            continue

        if current:

            sections[current].append(line)

    #
    # Convert lists into strings
    #
    for name in sections:

        sections[name] = "\n".join(sections[name])

    #
    # Results from every analyzer
    #
    reports = []

    findings = []

    for name, module in modules.items():

        section_name = module.SECTION

        if section_name not in sections:
            continue

        report = module.analyze(sections[section_name])

        reports.append(report)

        findings.extend(
            report["findings"]
        )

    #
    # Sort findings
    #
    priority = {

        "HIGH": 0,
        "MEDIUM": 1,
        "LOW": 2,

    }

    findings.sort(
        key=lambda x: priority[x["priority"]]
    )

    for level in ("HIGH", "MEDIUM", "LOW"):
        group = [x for x in findings if x["priority"] == level]

        if not group:
            continue

        color = priority_colors[level]

        print()
        print(color + "=" * 60)
        print(f" {level} PRIORITY")
        print("=" * 60 + W)

        for finding in group:

            print(
                f"  {C}[{finding['module']}]{Y} {finding['title']}{W}"
            )

            print(f"    └───┬ {W}{finding['reason']}{W}")
            for recommendation in finding["recommendation"]:
                print(f"        ├─ {recommendation}")
            print()

    #
    # Detailed reports
    #
    print()
    print(C + "=" * 60)
    print("MODULE REPORTS")
    print("=" * 60 + W)

    for report in reports:

        print()

        print(f"{C}{report['module']}{W}")
        print("-" * 40)

        for key, value in report["summary"].items():
            print(f"{C}{key:<18}{W}: {value}")

        if report.get("report"):
            print()
            print(report["report"])
