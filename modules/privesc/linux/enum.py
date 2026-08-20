from pathlib import Path
import pyperclip

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markup import escape
from rich import box

from core.paths import get_tools_dir
from modules.upload.linux import stage_linux_files
from modules.download.linux import receive_file


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
    enum_script = get_tools_dir() / "linux_enum.sh"
    cred_script = get_tools_dir() / "linux_credscan.py"
    stage_linux_files([enum_script, cred_script])

    helper = """chmod +x linux_enum.sh && ./linux_enum.sh && python3 linux_credscan.py"""

    pyperclip.copy(helper)

    print()
    print(f"{Y}{helper}")
    print()
    print(f"{G}→ helper commands copied to clipboard{W}")

    #
    # Wait for enumeration
    #
    input(
        f"\n{Y}[*] Press ENTER after the enumeration has completed...{W}"
    )

    #
    # Download results
    #
    outfile = Path("linux_enum.txt")
    
    receive_file(
        outfile=outfile
    )

    #
    # Analyze
    #
    print()

    print(f"{G}[+] Enumeration received.{W}")
    analyze(outfile)
    
  

def analyze(outfile):
    
    from modules.privesc.linux.analyzers import suid
    from modules.privesc.linux.analyzers import sudo
    from modules.privesc.linux.analyzers import groups
    from modules.privesc.linux.analyzers import capabilities
    from modules.privesc.linux.analyzers import software
    from modules.privesc.linux.analyzers import cron
    from modules.privesc.linux.analyzers import containers
    from modules.privesc.linux.analyzers import nfs
    from modules.privesc.linux.analyzers import kernel
    from modules.privesc.linux.analyzers import shared_library
    from modules.privesc.linux.analyzers import writable_paths
    from modules.privesc.linux.analyzers import path
    from modules.privesc.linux.analyzers import processes
    from modules.privesc.linux.analyzers import users
    from modules.privesc.linux.analyzers import history
    from modules.privesc.linux.analyzers import network


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


    ENABLE_KERNEL_ANALYSIS = True
    if ENABLE_KERNEL_ANALYSIS and "KERNEL" in sections:
        if "KERNEL" in sections:

            report = kernel.analyze(
                sections["KERNEL"]
            )

            reports.append(report)

            findings.extend(
                report["findings"]
            )    


    ENABLE_USERS_ANALYSIS = True
    if ENABLE_USERS_ANALYSIS and "USERS" in sections:
        if "USERS" in sections:

            report = users.analyze(
                sections["USERS"]
            )

            reports.append(report)

            findings.extend(
                report["findings"]
            )                


    ENABLE_SUDO_ANALYSIS = True
    if ENABLE_SUDO_ANALYSIS and "SUDO" in sections:
        if "SUDO" in sections:

            report = sudo.analyze(
                sections["SUDO"]
            )

            reports.append(report)

            findings.extend(
                report["findings"]
            )

    ENABLE_SUID_ANALYSIS = True  
    if ENABLE_SUID_ANALYSIS and "SUID" in sections:
        if "SUID" in sections:

            report = suid.analyze(
                sections["SUID"]
            )

            reports.append(report)

            findings.extend(
                report["findings"]
            )


    ENABLE_GROUPS_ANALYSIS = True  
    if ENABLE_GROUPS_ANALYSIS and "GROUPS" in sections:
        if "GROUPS" in sections:
            report = groups.analyze(
                sections["GROUPS"]
            )
            reports.append(report)

            findings.extend(
                report["findings"]
            )


    ENABLE_PATH_ANALYSIS = True  
    if ENABLE_PATH_ANALYSIS and "PATH" in sections:
        if "PATH" in sections:
            report = path.analyze(
                sections["PATH"]
            )
            reports.append(report)

            findings.extend(
                report["findings"]
            )

    ENABLE_HISTORY_ANALYSIS = True  
    if ENABLE_HISTORY_ANALYSIS and "HISTORY" in sections:
        if "HISTORY" in sections:
            report = history.analyze(
                sections["HISTORY"]
            )
            reports.append(report)

            findings.extend(
                report["findings"]
            )

    ENABLE_NETWORK_ANALYSIS = True
    if ENABLE_NETWORK_ANALYSIS and "NETWORK" in sections:
        report = network.analyze(sections["NETWORK"])
        reports.append(report)
        findings.extend(report["findings"])
            
                
    
    ENABLE_CAPABILITIES_ANALYSIS = True  
    if ENABLE_CAPABILITIES_ANALYSIS and "CAPABILITIES" in sections:
        if "CAPABILITIES" in sections:
                report = capabilities.analyze(
                    sections["CAPABILITIES"]
                )
                reports.append(report)
        
                findings.extend(
                    report["findings"]
                )

    ENABLE_WRITABLE_PATHS_ANALYSIS = True  
    if ENABLE_WRITABLE_PATHS_ANALYSIS and "WRITABLE PATHS" in sections:
                        report = writable_paths.analyze(
                            sections["WRITABLE PATHS"]
                )
                        reports.append(report)
                
                        findings.extend(
                            report["findings"]
                )

    ENABLE_PROCESSES_ANALYSIS = True  
    if ENABLE_PROCESSES_ANALYSIS and "PROCESSES" in sections:
                            report = processes.analyze(
                                sections["PROCESSES"]
                    )
                            reports.append(report)
                    
                            findings.extend(
                                report["findings"]
                    )
                                    

    ENABLE_CRON_ANALYSIS = True  
    if ENABLE_CRON_ANALYSIS and "CRON" in sections:
                    report = cron.analyze(
                        sections["CRON"]
            )
                    reports.append(report)
            
                    findings.extend(
                        report["findings"]
            )   

    ENABLE_NFS_ANALYSIS = True  
    if ENABLE_NFS_ANALYSIS and "NFS" in sections:
                    report = nfs.analyze(
                        sections["NFS"]
            )
                    reports.append(report)
            
                    findings.extend(
                        report["findings"]
            )  
                    

                    
    
    ENABLE_SOFTWARE_ANALYSIS = True
    if ENABLE_SOFTWARE_ANALYSIS and "SOFTWARE" in sections:
        if "SOFTWARE" in sections:
                    report = software.analyze(
                        sections["SOFTWARE"]
                )
                    reports.append(report)
            
                    findings.extend(
                        report["findings"]
                )    


    ENABLE_CONTAINERS_ANALYSIS = True  
    if ENABLE_CONTAINERS_ANALYSIS and "CONTAINERS" in sections:
            if "CONTAINERS" in sections:
                        report = containers.analyze(
                            sections["CONTAINERS"]
                    )
                        reports.append(report)
                
                        findings.extend(
                            report["findings"]
                    )                 

    ENABLE_SHARED_LIBRARIES_ANALYSIS = True  
    if ENABLE_SHARED_LIBRARIES_ANALYSIS and "SHARED LIBRARIES" in sections:
            if "SHARED LIBRARIES" in sections:
                        report = shared_library.analyze(
                            sections["SHARED LIBRARIES"]
                    )
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
            Text("LINUX PRIVILEGE ESCALATION ANALYZER", justify="center", style="bold white"),
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
            elements.append(Text(report["report"]))

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
