from pathlib import Path
import pyperclip

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

priority_colors = {
    "HIGH": R,
    "MEDIUM": Y,
    "LOW": B,
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
    cred_script = get_tools_dir() / "credscan.py"
    stage_linux_files([enum_script, cred_script])

    helper = """chmod +x linux_enum.sh && ./linux_enum.sh && python3 credscan.py"""

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
    
    from modules.privesc.analyzers import suid
    from modules.privesc.analyzers import sudo
    from modules.privesc.analyzers import groups
    from modules.privesc.analyzers import capabilities
    from modules.privesc.analyzers import software
    from modules.privesc.analyzers import cron
    from modules.privesc.analyzers import containers
    from modules.privesc.analyzers import nfs
    from modules.privesc.analyzers import kernel
    from modules.privesc.analyzers import shared_library
    from modules.privesc.analyzers import writable_paths
    from modules.privesc.analyzers import path
    from modules.privesc.analyzers import processes
    from modules.privesc.analyzers import users
    from modules.privesc.analyzers import history
    from modules.privesc.analyzers import network


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
