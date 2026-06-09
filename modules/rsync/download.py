import os
import subprocess
from pathlib import Path

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
            f"{Y}rsync -av "
            f"rsync://{M}<IP>{W}/{M}<SHARE>{W}"
        )

        print()

        print(
            f"{Y}RSYNC_PASSWORD={M}<PASS>{W} "
            f"rsync -av "
            f"rsync://{M}<USER>{W}@{M}<IP>{W}/{M}<SHARE>{W}"
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
    # SHARE
    # -----------------------------

    share = None

    if getattr(
        args,
        "extra",
        None
    ):

        if args.extra:

            share = args.extra[0]

    if not share:

        print(
            f"\n{R}[!]{W} "
            f"Share required."
        )

        print()

        print(
            f"{Y}Run:{W}"
        )

        print()

        print(
            f"{C}ctf rsync.enum{W}"
        )

        print()

        print(
            f"{C}ctf rsync.download dev{W}"
        )

        print()

        return

    # -----------------------------
    # ARTIFACTS
    # -----------------------------

    loot_dir = (
        get_artifacts_dir(
            target_name
        )
        / "rsync"
        / share
    )

    loot_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------
    # AUTH
    # -----------------------------

    auth_label = (
        "anonymous"
    )

    cmd = None

    creds = data.get(
        "creds",
        []
    )

    current_index = data.get(
        "current_cred"
    )

    if (
        current_index is not None
        and current_index < len(creds)
    ):

        current = creds[
            current_index
        ]

        if (
            current.get(
                "type"
            )
            == "password"
        ):

            user = current.get(
                "user"
            )

            password = current.get(
                "secret"
            )

            auth_label = (
                f"{user} (password)"
            )

            cmd = (
                f"RSYNC_PASSWORD='{password}' "
                f"rsync -av "
                f"rsync://{user}@{ip}/{share} "
                f"'{loot_dir}'"
            )

    if not cmd:

        cmd = (
            f"rsync -av "
            f"rsync://{ip}/{share} "
            f"'{loot_dir}'"
        )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: RSYNC DOWNLOAD "
        f"────────────────────┐{W}"
    )

    print(
        f"{B}│{W} "
        f"TARGET: "
        f"{C}{ip:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W} "
        f"SHARE:  "
        f"{C}{share:<38}{W}"
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

    # -----------------------------
    # DESTINATION
    # -----------------------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"DESTINATION\n"
    )

    print(
        f"{C}{loot_dir}{W}"
    )

    # -----------------------------
    # COMMAND
    # -----------------------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"COMMAND\n"
    )

    print(
        f"{Y}{cmd}{W}\n"
    )

    # -----------------------------
    # EXECUTE
    # -----------------------------

    try:

        subprocess.run(
            cmd,
            shell=True
        )

        print()

        print(
            f"{G}[+]{W} "
            f"Download completed."
        )

        print(
            f"{G}[+]{W} "
            f"Saved to:"
        )

        print(
            f"{C}{loot_dir}{W}"
        )

    except KeyboardInterrupt:

        print(
            f"\n{R}[!]{W} "
            f"Download interrupted."
        )

    print()
