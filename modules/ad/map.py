PROVIDES = []
REQUIRES = []


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

    #
    # NETWORK
    #

    network = ".".join(
        ip.split(".")[:3]
    ) + ".0/24"

    alive = (
        artifacts /
        "alive.txt"
    )

    smb = (
        artifacts /
        "smb.txt"
    )

    nmap = (
        artifacts /
        "nmap.txt"
    )

    print(
        f"\n{B}┌── AD MAP ───────────────────────────┐{W}"
    )

    print(
        f"  {B}[1]{W} Fast"
    )

    print(
        f"  {B}[2]{W} Fast + Nmap\n"
    )

    choice = input(
        f"{Y}Select> {W}"
    ).strip()

    #
    # PING SWEEP
    #

    print()

    print(
        f"{B}[*]{W} Discovering live hosts..."
    )

    cmd = [
        "fping",
        "-asg",
        network,
    ]

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    with open(
        alive,
        "w"
    ) as f:

        subprocess.run(
            cmd,
            stdout=f,
        )

    print(
        f"{G}[+] Live hosts:{W} {alive}"
    )

    #
    # SMB ENUM
    #

    print()

    print(
        f"{B}[*]{W} Enumerating SMB..."
    )

    cmd = [
        "nxc",
        "smb",
        str(alive),
        "--log",
        str(smb),
    ]

    if cred:

        cmd.extend([
            "-u",
            cred["user"],
            "-p",
            cred["secret"],
        ])

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    subprocess.run(
        cmd
    )

    print(
        f"{G}[+] SMB:{W} {smb}"
    )

    #
    # NMAP
    #

    if choice == "2":

        print()

        print(
            f"{B}[*]{W} Running Nmap..."
        )

        cmd = [
            "nmap",
            "-Pn",
            "-n",
            "-iL",
            str(alive),
            "-p",
            "53,80, 88,135,139,389,445,464,593,636,3268,3269,3389,5985,5986,8080,9389",
            "-oN",
            str(nmap),
        ]

        print(
            f"{Y}{' '.join(cmd)}{W}\n"
        )

        subprocess.run(
            cmd
        )

        print(
            f"{G}[+] Nmap:{W} {nmap}"
        )

    print()

    print(
        f"{G}[+] AD mapping complete.{W}"
    )

    print(
        f"  ├── {alive}"
    )

    print(
        f"  ├── {smb}"
    )

    if choice == "2":

        print(
            f"  └── {nmap}"
        )

    else:

        print(
            f"  └── (No Nmap)"
        )

    print()
