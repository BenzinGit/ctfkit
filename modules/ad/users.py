from datetime import datetime
from pathlib import Path
import subprocess

import re
from core.paths import get_tools_dir


def kerbrute_enum(
    data,
    cred,
    args,
    artifact_dir
):

    from pathlib import Path
    from datetime import datetime
    import subprocess

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'

    target = data.get("ip")
    domain = data.get("domain")


    if not target or not domain:

        print(
            f"\n{R}[!] {W}Missing target/domain\n"
        )

        return set()


    #
    # DEFAULT WORDLIST
    #

    default_wordlist = Path(
        "/usr/share/seclists/Usernames/xato-net-10-million-usernames.txt"
    )

    if not default_wordlist.exists():

        default_wordlist = Path(
            "/usr/share/wordlists/seclists/Usernames/xato-net-10-million-usernames.txt"
        )

    print(
        f"\n{B}[?]{W} Username Wordlist"
    )

    user_input = input(
        f"{C}Path [{default_wordlist}] > {W}"
    ).strip()

    if user_input:

        userlist = Path(
            user_input
        ).expanduser().resolve()

    else:

        userlist = default_wordlist

    if not userlist.exists():

        print(
            f"\n{R}[!] {W}Wordlist not found\n"
        )

        print(
            f"{B}  └── {C}{userlist}{W}\n"
        )

        return set()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    users_file = (
        artifact_dir /
        "users.txt"
    )

    output_file = (
        artifact_dir /
        f"kerbrute_{timestamp}.txt"
    )

    cmd = [
        "kerbrute",
        "userenum",
        "-d",
        domain,
        "--dc",
        target,
        str(userlist),
        "-o",
        str(output_file)
    ]

    print(
        f"\n{B}[*]{W} Kerbrute User Enumeration\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    subprocess.run(
        cmd
    )
    users = set()

    for line in output_file.read_text(
        errors="ignore"
    ).splitlines():

        line = line.strip()

        if "VALID USERNAME:" not in line:
            continue

        try:

            username = (
                line.split(
                    "VALID USERNAME:",
                    1
                )[1]
                .strip()
                .split("@")[0]
            )

            if username:

                users.add(
                    username
                )

        except Exception:

            pass

    # <-- AFTER the loop is finished

    users = sorted(users)

    print(
        f"\n{G}[+] {W}"
        f"{len(users)} user(s) recovered\n"
    )

    for user in users[:20]:

        print(
            f"  {B}├──{W} "
            f"{C}{user}{W}"
        )


    return users

def windapsearch_enum(
    data,
    cred,
    args,
    artifact_dir
):


    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'

    target = data.get("ip")
    domain = data.get("domain")

    if not target or not domain:

        print(
            f"\n{R}[!] {W}Missing target/domain\n"
        )

        return set()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    logfile = (
        artifact_dir /
        f"windapsearch_{timestamp}.log"
    )

    service_file = (
        artifact_dir /
        "service_accounts.txt"
    )

    objects_file = (
        artifact_dir /
        "ldap_objects.txt"
    )

    windapsearch_file = (
        get_tools_dir()
        / "windapsearch.py"
    )

    cmd = [
        "python3",
        str(windapsearch_file),
        "-d",
        domain,
        "--dc-ip",
        target,
        "--custom",
        "objectClass=*"
    ]

    print(
        f"\n{B}[*]{W} Windapsearch LDAP Discovery\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    logfile.write_text(
        result.stdout +
        result.stderr
    )

    users = set()
    services = set()
    interesting = set()

    KEYWORDS = [
        "svc",
        "service",
        "admin",
        "priv",
        "backup",
        "sql",
        "exchange",
        "helpdesk"
    ]

    for line in result.stdout.splitlines():

        line = line.strip()

        if not line:
            continue

        #
        # Users
        #

        if line.startswith("CN="):

            try:

                cn = (
                    line.split(
                        "CN=",
                        1
                    )[1]
                    .split(
                        ",",
                        1
                    )[0]
                    .strip()
                )

            except Exception:

                continue

            if not cn:
                continue

            #
            # Service accounts
            #

            lower = cn.lower()

            if any(
                keyword in lower
                for keyword in KEYWORDS
            ):

                interesting.add(
                    cn
                )

                if (
                    lower.startswith("svc")
                    or "service" in lower
                ):

                    services.add(
                        cn
                    )

            #
            # Human-ish usernames
            #

            if (
                " " not in cn
                and not cn.endswith("$")
                and not cn.startswith("HealthMailbox")
                and not cn.startswith("SM_")
            ):

                users.add(
                    cn
                )

        #
        # OUs
        #

        if line.startswith("OU="):

            try:

                ou = (
                    line.split(
                        "OU=",
                        1
                    )[1]
                    .split(
                        ",",
                        1
                    )[0]
                    .strip()
                )

            except Exception:

                continue

            lower = ou.lower()

            if any(
                keyword in lower
                for keyword in KEYWORDS
            ):

                interesting.add(
                    ou
                )

    users = sorted(
        users
    )

    services = sorted(
        services
    )

    interesting = sorted(
        interesting
    )

    if services:

        service_file.write_text(
            "\n".join(
                services
            )
        )

    if interesting:

        objects_file.write_text(
            "\n".join(
                interesting
            )
        )

    print(
        f"{G}[+] {W}"
        f"{len(users)} user(s) recovered\n"
    )

    if services:

        print(
            f"{G}[+] {W}Service Accounts\n"
        )

        for svc in services:

            print(
                f"  {B}├──{W} "
                f"{C}{svc}{W}"
            )

        print()

    if interesting:

        print(
            f"{G}[+] {W}Interesting LDAP Objects\n"
        )

        for obj in interesting[:20]:

            print(
                f"  {B}├──{W} "
                f"{C}{obj}{W}"
            )

        if len(interesting) > 20:

            print(
                f"\n  {B}└──{W} "
                f"{C}+{len(interesting)-20}{W} more"
            )

        print()

    print(
        f"{G}[+] {W}Logs Saved"
    )

    print(
        f"{B}  ├── {C}{logfile}{W}"
    )

    if services:

        print(
            f"{B}  ├── {C}{service_file}{W}"
        )

    if interesting:

        print(
            f"{B}  └── {C}{objects_file}{W}"
        )

    print()

    return users

def anonymous_ldap_enum(
    data,
    cred,
    args,
    artifact_dir
):

    from datetime import datetime
    import subprocess

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'

    target = data.get("ip")

    if not target:

        print(
            f"\n{R}[!] {W}No target configured\n"
        )

        return set()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    naming_log = (
        artifact_dir /
        f"ldap_namingcontexts_{timestamp}.log"
    )

    users_log = (
        artifact_dir /
        f"ldap_users_{timestamp}.log"
    )

    full_log = (
        artifact_dir /
        f"ldap_full_{timestamp}.log"
    )

    interesting_file = (
        artifact_dir /
        "ldap_objects.txt"
    )

    #
    # DISCOVER BASE DN
    #

    cmd = [
        "ldapsearch",
        "-x",
        "-H",
        f"ldap://{target}",
        "-s",
        "base",
        "namingcontexts"
    ]

    print(
        f"\n{B}[*]{W} Anonymous LDAP Discovery\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    naming_log.write_text(
        result.stdout +
        result.stderr
    )

    base_dn = None

    for line in result.stdout.splitlines():

        if line.lower().startswith(
            "namingcontexts:"
        ):

            base_dn = (
                line.split(
                    ":",
                    1
                )[1]
                .strip()
            )

            break

    if not base_dn:

        domain = data.get(
            "domain"
        )

        if domain:

            base_dn = ",".join(
                f"dc={x}"
                for x in domain.split(".")
            )

    if not base_dn:

        print(
            f"{Y}[-]{W} Unable to determine Base DN\n"
        )

        return set()

    print(
        f"{G}[+] {W}Base DN: "
        f"{C}{base_dn}{W}\n"
    )

    #
    # USER ENUMERATION
    #

    cmd = [
        "ldapsearch",
        "-x",
        "-H",
        f"ldap://{target}",
        "-b",
        base_dn,
        "(&(objectCategory=person)(objectClass=user))",
        "sAMAccountName"
    ]

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    users_log.write_text(
        result.stdout +
        result.stderr
    )

    users = set()

    for line in result.stdout.splitlines():

        line = line.strip()

        if not line.startswith(
            "sAMAccountName:"
        ):
            continue

        username = (
            line.split(
                ":",
                1
            )[1]
            .strip()
        )

        if not username:
            continue

        if username.endswith("$"):
            continue

        users.add(
            username
        )

    #
    # FULL LDAP DUMP
    #

    full_cmd = [
        "ldapsearch",
        "-x",
        "-H",
        f"ldap://{target}",
        "-b",
        base_dn
    ]

    print(
        f"{B}[*]{W} Full LDAP Discovery\n"
    )

    print(
        f"{Y}{' '.join(full_cmd)}{W}\n"
    )

    full_result = subprocess.run(
        full_cmd,
        capture_output=True,
        text=True
    )

    full_log.write_text(
        full_result.stdout +
        full_result.stderr
    )

    interesting = set()

    KEYWORDS = [
        "service",
        "svc",
        "admin",
        "priv",
        "backup",
        "sql",
        "exchange",
        "helpdesk"
    ]

    for line in full_result.stdout.splitlines():

        line = line.strip()

        if not line.lower().startswith(
            "dn:"
        ):
            continue

        lower = line.lower()

        if not any(
            keyword in lower
            for keyword in KEYWORDS
        ):
            continue

        #
        # Extract CN=
        #

        if "CN=" in line:

            try:

                obj = (
                    line.split(
                        "CN=",
                        1
                    )[1]
                    .split(
                        ",",
                        1
                    )[0]
                    .strip()
                )

                if obj:

                    interesting.add(
                        obj
                    )

            except Exception:

                pass

        #
        # Extract OU=
        #

        elif "OU=" in line:

            try:

                obj = (
                    line.split(
                        "OU=",
                        1
                    )[1]
                    .split(
                        ",",
                        1
                    )[0]
                    .strip()
                )

                if obj:

                    interesting.add(
                        obj
                    )

            except Exception:

                pass

    interesting = sorted(
        interesting
    )

    if interesting:

        interesting_file.write_text(
            "\n".join(
                interesting
            )
        )

        print(
            f"{G}[+] {W}Interesting LDAP Objects\n"
        )

        for obj in interesting:

            print(
                f"  {B}├──{W} "
                f"{C}{obj}{W}"
            )

        print()

        print(
            f"{G}[+] {W}Objects Saved"
        )

        print(
            f"{B}  └── "
            f"{C}{interesting_file}{W}\n"
        )

    print(
        f"{G}[+] {W}"
        f"{len(users)} user(s) recovered\n"
    )

    print(
        f"{G}[+] {W}Logs Saved"
    )

    print(
        f"{B}  ├── {C}{naming_log}{W}"
    )

    print(
        f"{B}  ├── {C}{users_log}{W}"
    )

    print(
        f"{B}  └── {C}{full_log}{W}\n"
    )

    return users




def ldap_enum(
    data,
    cred,
    args,
    artifact_dir
):

    G = '\033[92m'
    B = '\033[94m'
    Y = '\033[93m'
    W = '\033[0m'

    if not cred:
        print(
            f"\n{Y}[-]{W} LDAP requires credentials\n"
        )
        return set()

    target = data.get("ip")
    domain = data.get("domain")

    current_user = cred["user"]
    current_secret = cred["secret"]
    cred_type = cred["type"]

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    logfile = (
        artifact_dir /
        f"ldap_users_{timestamp}.log"
    )

    cmd = [
        "netexec",
        "ldap",
        str(target)
    ]

    if domain:
        cmd.extend([
            "-d",
            domain
        ])

    if cred_type == "password":

        cmd.extend([
            "-u",
            current_user,
            "-p",
            current_secret
        ])

    elif cred_type == "ntlm":

        cmd.extend([
            "-u",
            current_user,
            "-H",
            current_secret
        ])

    elif cred_type == "ticket":

        cmd.extend([
            "--use-kcache"
        ])

    cmd.extend([
        "--users",
        "--log",
        str(logfile)
    ])

    print(
        f"\n{B}[*]{W} LDAP Enumeration\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    #
    # Keep NetExec output intact.
    #

    subprocess.run(cmd)

    if not logfile.exists():

        print(
            f"{Y}[-]{W} No logfile created\n"
        )

        return set()

    users = set()

    header_found = False
    lines = logfile.read_text( errors="ignore" ).splitlines()
    for line in lines:

        if "-Username-" in line:
            header_found = True
            continue

        if not header_found:
            continue

        if "LDAP" not in line:
            continue

        parts = line.split()

        try:

            ldap_idx = parts.index("LDAP")

            username = parts[ldap_idx + 4]

        except Exception:
            continue

        if username.startswith("-"):
            continue

        if username.startswith("["):
            continue

        users.add(username)

    print(
        f"{G}[+]{W} "
        f"{len(users)} user(s) recovered via LDAP\n"
    )

    return users



def windows(data, cred, args, artifact_dir):

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'

    BOLD = '\033[1m'
    from core.paths import get_tools_dir
    from modules.upload.windows import stage_windows_files
    


    print(
        f"{B}[?]{W} Transfer PowerView / SharpView?\n"
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

        PowerView = (
            windows_tools /
            "PowerView.ps1"
        )

        SharpView = (
            windows_tools /
            "SharpView.exe"
        )

        stage_windows_files([
            SharpView,
            PowerView
        ])

    print(
        f"\n{G}[+] {W}ActiveDirectory Module\n"
    )

    print(
        f"{Y}Import-Module ActiveDirectory{W}"
    )

    print()

    print(
        f"{Y}Get-ADUser -Filter *{W}"
    )

    print(
        f"{Y}Get-ADUser -Identity {C}<username>{W}"
    )

    print()

    print(
        f"{G}[+] {W}PowerView\n"
    )

    print(
        f"{Y}. .\\PowerView.ps1{W}"
    )

    print()

    print(
        f"{Y}Get-DomainUser{W}"
    )

    print(
        f"{Y}Get-DomainUser -Identity {C}<username>{W}"
    )

    print()

    print(
        f"{G}[+] {W}SharpView\n"
    )

    print(
        f"{Y}SharpView.exe Get-DomainUser{W}"
    )

    print(
        f"{Y}SharpView.exe Get-DomainUser -Identity {C}<username>{W}"
    )

    print()



def run(data, creds, args):

    from core.paths import get_chain_artifacts_dir

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'
    BOLD = '\033[1m'

    artifact_dir = get_chain_artifacts_dir(
        data["name"],
        "ad"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    users_file = (
        artifact_dir /
        "users.txt"
    )

    methods = {
        "1": {
            "name": "LDAP (NetExec)",
            "func": ldap_enum
        },
        "2": {
            "name": "LDAP (Windapsearch)",
            "func": windapsearch_enum
        },
        "3": {
            "name": "Anonymous LDAP",
            "func": anonymous_ldap_enum
        },
        "4": {
            "name": "Kerbrute",
            "func": kerbrute_enum
        },
        "5": {
            "name": "RID Cycling",
            "func": rid_enum
        },
         "6": {
            "name": "Windows Reference",
            "func": windows
        },
        "7": {
            "name": "All",
            "func": None
        }
    }

    print(
        f"\n{B}┌── {BOLD}MODULE: AD USER ENUMERATION{W}{B} ───────────────┐{W}"
    )

    print(
        f"{B}│{W}  {B}Domain:{W} "
        f"{C}{data.get('domain', 'UNKNOWN'):<36}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}Target:{W} "
        f"{C}{data.get('ip', 'UNKNOWN'):<36}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└──────────────────────────────────────────────┘{W}"
    )

    print()

    for key, item in methods.items():

        print(
            f"  {B}[{C}{key}{B}]{W} "
            f"{item['name']}"
        )

    choice = input(
        f"\n{B}Select>{W} "
    ).strip()

    if choice not in methods:

        print(
            f"\n{R}[!] {W}Invalid selection\n"
        )

        return
 
    selected = []

    if choice == "7":

        selected = [
            x["func"]
            for x in methods.values()
            if x["func"]
        ]

    else:

        selected = [
            methods[choice]["func"]
        ]

    users = set()

    for func in selected:

        try:

            result = func(
                data=data,
                cred=creds,
                args=args,
                artifact_dir=artifact_dir
            )

            if result:

                users.update(
                    result
                )

        except Exception as e:

            print(
                f"{Y}[-]{W} "
                f"{func.__name__}: "
                f"{e}"
            )

    users = sorted(
        set(users)
    )

    if not users:

        print(
            f"\n{Y}[-]{W} No users recovered\n"
        )

        return

    users_file.write_text(
        "\n".join(users)
    )

    print(
        f"\n{G}[+] {W}Recovered "
        f"{C}{len(users)}{W} user(s)\n"
    )

    for user in users[:20]:

        print(
            f"  {B}├──{W} "
            f"{C}{user}{W}"
        )

    if len(users) > 20:

        print(
            f"\n  {B}└──{W} "
            f"{C}+{len(users)-20}{W} more"
        )

    print()

    print(
        f"{G}[+] {W}Users Saved"
    )

    print(
        f"{B}  └── {C}{users_file}{W}\n"
    )

    return {
        "users": users
    }


def rid_enum(data, cred, args, artifact_dir):
    return {"NOT IMPLEMENTED"}