import re
import socket
import subprocess

from core.paths import (
    get_artifacts_dir
)


PROVIDES = []
REQUIRES = ["ip"]


def run(data, cred, args):

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    W = '\033[0m'
    R = '\033[91m'
    M = '\033[95m'

    reference = getattr(
        args,
        "reference",
        False
    )

    # -----------------------------
    # REFERENCE
    # -----------------------------

    if reference:

        print(
            f"\n{B}┌── REFERENCE "
            f"──────────────────────────────────────┐{W}"
        )

        print()

        print(
            f"{Y}nmap -sV -p873 "
            f"{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}nc -nv "
            f"{M}<IP>{W} 873"
        )

        print()

        print(
            f"{Y}@RSYNCD: 31.0{W}"
        )

        print()

        print(
            f"{Y}#list{W}"
        )

        print()

        print(
            f"{Y}rsync -av --list-only "
            f"rsync://{M}<IP>{W}/{M}<SHARE>{W}"
        )

        print(
            f"\n{B}└──────────────────────────────────────────────┘{W}\n"
        )

        return

    # -----------------------------
    # TARGET
    # -----------------------------

    ip = data.get(
        "ip"
    )

    if not ip:

        print(
            f"\n{R}[!]{W} "
            f"No target IP loaded."
        )

        return

    target_name = data.get(
        "name",
        "unknown"
    )

    # -----------------------------
    # ARTIFACTS
    # -----------------------------

    artifact_dir = (
        get_artifacts_dir(
            target_name
        )
        / "rsync"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: RSYNC ENUMERATION "
        f"──────────────────┐{W}"
    )

    print(
        f"{B}│{W} "
        f"TARGET: "
        f"{C}{ip:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└───────────────────────────────────────────────┘{W}"
    )

    # -----------------------------
    # NMAP
    # -----------------------------

    cmd = (
        f"nmap "
        f"-sV "
        f"-p873 "
        f"{ip}"
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"SERVICE DETECTION\n"
    )

    print(
        f"{Y}{cmd}{W}\n"
    )

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    output = (
        result.stdout
        + result.stderr
    )

    print(
        output
    )

    (
        artifact_dir
        / "service_detection.txt"
    ).write_text(
        output
    )

    # -----------------------------
    # SHARE ENUM
    # -----------------------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"ENUMERATING SHARES\n"
    )

    shares_output = ""

    try:

        s = socket.socket()

        s.settimeout(
            5
        )

        s.connect(
            (
                ip,
                873
            )
        )

        banner = (
            s.recv(1024)
            .decode(
                errors="ignore"
            )
        )

        shares_output += banner

        s.sendall(
            b"@RSYNCD: 31.0\n"
        )

        shares_output += (
            s.recv(1024)
            .decode(
                errors="ignore"
            )
        )

        s.sendall(
            b"#list\n"
        )

        while True:

            chunk = s.recv(
                4096
            )

            if not chunk:

                break

            decoded = chunk.decode(
                errors="ignore"
            )

            shares_output += decoded

            if (
                "@RSYNCD: EXIT"
                in decoded
            ):
                break

        s.close()

    except Exception as e:

        shares_output = str(
            e
        )

    print(
        shares_output
    )

    (
        artifact_dir
        / "shares_raw.txt"
    ).write_text(
        shares_output
    )

    # -----------------------------
    # PARSE SHARES
    # -----------------------------

    shares = []

    for line in shares_output.splitlines():

        line = line.strip()

        if (
            not line
            or line.startswith("@")
        ):

            continue

        if " " in line:

            share = (
                line.split()[0]
            )

        else:

            share = line

        if re.match(
            r"^[A-Za-z0-9._-]+$",
            share
        ):

            shares.append(
                share
            )

    shares = list(
        dict.fromkeys(
            shares
        )
    )

    (
        artifact_dir
        / "shares.txt"
    ).write_text(
        "\n".join(
            shares
        )
    )

    # -----------------------------
    # DISPLAY
    # -----------------------------

    if shares:

        print(
            f"\n{B}[{W}{G}*{W}{B}]{W} "
            f"AVAILABLE SHARES\n"
        )

        for i, share in enumerate(
            shares,
            start=1
        ):

            print(
                f"{C}[{i}]{W} "
                f"{G}{share}{W}"
            )

        print()

        print(
            f"{Y}Download with:{W}"
        )

        print()

        print(
            f"{C}ctf rsync.download "
            f"<share>{W}"
        )

        print()

    else:

        print(
            f"\n{Y}[!]{W} "
            f"No shares discovered."
        )

    # -----------------------------
    # RESULTS
    # -----------------------------

    print(
        f"{G}[+]{W} "
        f"Results saved:"
    )

    print(
        f"{C}{artifact_dir}{W}"
    )

    print()
