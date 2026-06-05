import subprocess
from pathlib import Path


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
            f"{Y}showmount -e {M}<IP>{W}"
        )

        print()

        print(
            f"{Y}sudo mount -t nfs "
            f"{M}<IP>{W}:{M}<EXPORT>{W} "
            f"{M}<LOCAL_DIR>{W} "
            f"-o nolock"
        )

        print()

        print(
            f"{Y}sudo umount {M}<LOCAL_DIR>{W}"
        )

        print(
            f"\n{B}└──────────────────────────────────────────────┘{W}\n"
        )

        return

    # -----------------------------
    # TARGET
    # -----------------------------

    ip = data.get("ip")

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
    # EXPORT
    # -----------------------------

    export = None

    if getattr(
        args,
        "extra",
        None
    ):

        if args.extra:

            export = args.extra[0]

    # -----------------------------
    # ENUM
    # -----------------------------

    if not export:

        print(
            f"\n{B}[{W}{G}*{W}{B}]{W} "
            f"Enumerating exports...\n"
        )
        print(f"{Y}showmount -e {ip}")
        result = subprocess.run(
            f"showmount -e {ip}",
            shell=True,
            capture_output=True,
            text=True
        )

        exports = []

        for line in result.stdout.splitlines():

            line = line.strip()

            if not line:
                continue

            if line.startswith(
                "Export list"
            ):
                continue

            export_path = (
                line.split()[0]
            )

            exports.append(
                export_path
            )

        if not exports:

            print(
                f"{R}[!]{W} "
                f"No exports found."
            )

            return

        print(
            f"{B}[{W}{G}*{W}{B}]{W} "
            f"AVAILABLE EXPORTS\n"
        )

        for i, entry in enumerate(
            exports,
            start=1
        ):

            print(
                f"{B}[{W}{Y}{i}{W}{B}]{W} "
                f"{C}{entry}{W}"
            )

        print()

        print(
            f"{B}[{W}{R}0{W}{B}]{W} Exit"
        )

        choice = input(
            "\n> "
        ).strip()

        if choice == "0":

            return

        if (
            not choice.isdigit()
            or int(choice) < 1
            or int(choice) > len(exports)
        ):

            print(
                f"\n{R}[!]{W} "
                f"Invalid selection."
            )

            return

        export = exports[
            int(choice) - 1
        ]

    # -----------------------------
    # MOUNT DIR
    # -----------------------------

    mount_name = (
        export
        .strip("/")
        .replace("/", "_")
    )

    if not mount_name:

        mount_name = "root"

    mount_dir = (
        Path("artifacts")
        / target_name
        / "nfs"
        / mount_name
    )

    mount_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------
    # COMMAND
    # -----------------------------

    cmd = (
        f"sudo mount -t nfs "
        f"{ip}:{export} "
        f"{mount_dir} "
        f"-o nolock"
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: NFS MOUNT "
        f"──────────────────────────┐{W}"
    )

    print(
        f"{B}│{W} "
        f"TARGET: "
        f"{C}{ip:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W} "
        f"EXPORT: "
        f"{C}{export:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└───────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"MOUNT POINT\n"
    )

    print(
        f"{C}{mount_dir}{W}"
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"COMMAND\n"
    )

    print(
        f"{Y}{cmd}{W}\n"
    )

    result = subprocess.run(
        cmd,
        shell=True
    )

    if result.returncode != 0:

        print(
            f"\n{R}[!]{W} "
            f"Mount failed."
        )

        return

    print(
        f"\n{G}[+]{W} "
        f"Mounted successfully."
    )

    print(
        f"{G}[+]{W} "
        f"Browse:"
    )

    print(
        f"{C}{mount_dir}{W}"
    )

    print()
    print(
        f"\n{Y}[!]{W} "
        f"Close the mounted terminal when finished."
    )
    subprocess.run(
        [
            "x-terminal-emulator",
            "-e",
            f"bash -c 'cd {mount_dir}; exec bash'"
        ]
    )

    result = subprocess.run(
        f"sudo umount {mount_dir}",
        shell=True
    )

    if result.returncode == 0:

        print(
            f"\n{G}[+]{W} "
            f"Unmounted."
        )

    else:

        print(
            f"\n{Y}[!]{W} "
            f"Could not unmount automatically."
        )

        print(
            f"{Y}sudo umount {mount_dir}{W}"
        )