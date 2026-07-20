import os
import subprocess

from core.paths import (
    get_windows_tools_dir
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
            f"{Y}xfreerdp3 "
            f"/u:{M}<USER>{W} "
            f"/p:{M}<PASS>{W} "
            f"/v:{M}<IP>{W} "
            f"+clipboard "
            f"/dynamic-resolution "
            f"/cert:ignore "
            f"/drive:shared,{M}<DIR>{W}"
        )

        print()

        print(
            f"{Y}xfreerdp3 "
            f"/u:{M}<USER>{W} "
            f"/pth:{M}<NTLM>{W} "
            f"/v:{M}<IP>{W}"
        )

        print()

        print(
            f"{Y}\\\\tsclient\\shared{W}"
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

    # -----------------------------
    # WINDOWS SHARE
    # -----------------------------

    share_dir = (
        get_windows_tools_dir()
    )

    # -----------------------------
    # CREDS
    # -----------------------------

    creds = data.get(
        "creds",
        []
    )

    current_index = data.get(
        "current_cred"
    )

    if (
        current_index is None
        or current_index >= len(creds)
    ):

        print(
            f"\n{R}[!]{W} "
            f"No credential selected."
        )

        return

    current = creds[
        current_index
    ]

    user = current.get(
        "user"
    )

    cred_type = current.get(
        "type"
    )

    auth_label = (
        f"{user} ({cred_type})"
    )
    domain = data.get("domain")

    # -----------------------------
    # PASSWORD
    # -----------------------------
    
    if cred_type == "password":

        secret = current.get(
            "secret"
        )

        cmd = (
            f"xfreerdp3 "
            f"/v:{ip} "
            f"/u:'{user}' "
            f"/p:'{secret}' "

        )

        if domain:
            cmd += f"/d:'{domain}' "

        cmd += (
            f"+clipboard "
            f"/dynamic-resolution "
            f"/cert:ignore "
            f"/drive:shared,{share_dir}"
        )

    # -----------------------------
    # NTLM
    # -----------------------------

    elif cred_type == "ntlm":

        secret = current.get(
            "secret"
        )

        cmd = (
            f"xfreerdp3 "
            f"/v:{ip} "
            f"/u:'{user}' "
            f"/pth:{secret} "
            f"+clipboard "
            f"/dynamic-resolution "
            f"/cert:ignore "
            f"/drive:shared,{share_dir}"
        )

    # -----------------------------
    # KERBEROS
    # -----------------------------

    elif cred_type == "ticket":

        ccache = current.get(
            "ccache"
        )

        if not ccache:

            print(
                f"\n{R}[!]{W} "
                f"No ccache file."
            )

            return

        os.environ[
            "KRB5CCNAME"
        ] = ccache

        cmd = (
            f"xfreerdp3 "
            f"/v:{ip} "
            f"/u:'{user}' "
            f"+clipboard "
            f"/dynamic-resolution "
            f"/cert:ignore "
            f"/drive:shared,{share_dir}"
        )

    else:

        print(
            f"\n{R}[!]{W} "
            f"Unsupported credential type:"
            f" {cred_type}"
        )

        return

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: RDP CONNECT "
        f"────────────────────────┐{W}"
    )

    print(
        f"{B}│{W} "
        f"TARGET: "
        f"{C}{ip:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W} "
        f"AUTH:   "
        f"{C}{auth_label:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└───────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"SHARED DRIVE\n"
    )

    print(
        f"{C}{share_dir}{W}"
    )

    print()

    print(
        f"{C}\\\\tsclient\\shared{W}"
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"COMMAND\n"
    )

    print(
        f"{Y}{cmd}{W}\n"
    )

    try:

        subprocess.run(
            cmd,
            shell=True
        )

    except KeyboardInterrupt:

        print(
            f"\n{R}[!]{W} "
            f"Connection closed."
        )

    print()
