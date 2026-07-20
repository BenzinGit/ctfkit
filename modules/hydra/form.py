
"""
Skeleton hydra.form module for CTFKit.

This is a starting point intended to be customized to your framework.
"""

import json
import re
import subprocess
from datetime import datetime

from core.paths import get_artifacts_dir
from core.target import get_current_url
import shlex

PROVIDES = []
REQUIRES = []

G = '\033[92m'
C = '\033[96m'
B = '\033[94m'
Y = '\033[93m'
R = '\033[91m'
W = '\033[0m'
BOLD = '\033[1m'

USERLISTS = {
    "1": ("Top Usernames",
          "/usr/share/seclists/Usernames/top-usernames-shortlist.txt"),
    "2": ("Custom", None),
}

PASSLISTS = {
    "1": ("2023 Top 200",
          "/usr/share/seclists/Passwords/Common-Credentials/2023-200_most_used_passwords.txt"),
    "2": ("rockyou",
          "/usr/share/wordlists/rockyou.txt"),
    "3": ("Custom", None),
}

def choose(table, prompt):
    print()
    for k,v in table.items():
        print(f"  [{k}] {v[0]}")
    c=input(f"{Y}{prompt}> {W}").strip()
    if c not in table:
        return None
    if table[c][1]:
        return table[c][1]
    return input("Path> ").strip()

def parse_hydra(text):
    m=re.search(r"login:\s*(\S+)\s+password:\s*(.+)",text)
    if not m:
        return None
    return m.group(1),m.group(2).strip()

def run(data,cred,args):
    base=get_current_url(data)
    if not base:
        print(f"{R}[!] No target selected.{W}")
        return

    base=input(f"{Y}Base URL [{base}]> {W}").strip() or base    

    path = input(
        f"{Y}Path [/]> {W}"
    ).strip()

    #
    # Default = root
    #

    if not path:

        path = "/"

    #
    # Ensure leading slash
    #

    elif not path.startswith("/"):

        path = "/" + path

    method=input(f"{Y}Method [POST]> {W}").strip().upper() or "POST"

    user_field=input(f"{Y}Username Field [username]> {W}").strip() or "username"
    pass_field=input(f"{Y}Password Field [password]> {W}").strip() or "password"

    fail=input(f"{Y}Failure String [Invalid credentials]> {W}").strip() or "Invalid credentials"

    users=choose(USERLISTS,"Username Wordlist")
    pwds=choose(PASSLISTS,"Password Wordlist")

    threads=input(f"{Y}Threads [16]> {W}").strip() or "16"

    art=get_artifacts_dir(data["name"])/"hydra"
    art.mkdir(parents=True,exist_ok=True)
    outfile=art/f"hydra_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    if "://" in base:
        target = base.split("://", 1)[1].split("/", 1)[0]
    else:
        target = base.split("/", 1)[0]
    service=f"http-{'post' if method=='POST' else 'get'}-form"

    form=f"{path}:{user_field}=^USER^&{pass_field}=^PASS^:F={fail}"

    cmd=[
        "hydra",
        "-L",users,
        "-P",pwds,
        "-f",
        "-t",threads,
        target,
        service,
        form,
    ]

    print("\nRunning:\n")
    print(shlex.join(cmd))
    print()

    r=subprocess.run(cmd,capture_output=True,text=True)
    outfile.write_text(r.stdout+r.stderr)

    found=parse_hydra(r.stdout+r.stderr)

    if found:
        user,password=found
        print(f"{G}[+] Credentials found{W}")
        print(f"User: {user}")
        print(f"Pass: {password}")
        return [{
            "type":"credential",
            "data":{
                "username":user,
                "password":password,
                "type":"password",
            }
        }]

    print(f"{R}[!] No credentials found.{W}")
    print(outfile)

