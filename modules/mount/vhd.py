from pathlib import Path
import subprocess
import os
import re


def run(data, cred, args):

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    W = '\033[0m'
    R = '\033[91m'
    BOLD = '\033[1m'

    # =========================================================
    # HELPERS
    # =========================================================

    def run_cmd(cmd):

        print(f"\n{B}[*]{W} Running\n")
        print(f"{Y}{' '.join(cmd)}{W}\n")

        return subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

    def get_image():

        image = getattr(args, "file", None)

        if not image and hasattr(args, "extra") and args.extra:
            image = args.extra[0]

        return image

    def get_largest_partition(loopdev):

        result = subprocess.run(
            ["lsblk", "-b", "-o", "NAME,SIZE", "-nr", loopdev],
            capture_output=True,
            text=True
        )

        largest = None
        largest_size = 0

        for line in result.stdout.splitlines():

            parts = line.split()

            if len(parts) != 2:
                continue

            name, size = parts

            if name == Path(loopdev).name:
                continue

            try:
                size = int(size)

                if size > largest_size:
                    largest_size = size
                    largest = f"/dev/{name}"

            except:
                pass

        return largest

    # =========================================================
    # REFERENCE MODE
    # =========================================================

    if getattr(args, "ref", False):

        print(f"\n{B}┌── {BOLD}MODULE: VHD MOUNTING{W}{B} ───────────────────────────┐{W}")
        print(f"{B}└────────────────────────────────────────────────────────────┘{W}")

        print(f"\n{B}[*]{W} Standard VHD/VHDX\n")

        print(f"{Y}sudo guestmount --add <IMAGE> --inspector --ro /mnt/vhd{W}")

        print(f"\n{B}[*]{W} BitLocker\n")

        print(f"{Y}sudo losetup -f -P <IMAGE>{W}")
        print(f"{Y}sudo dislocker /dev/loopXpY -u<PASSWORD> -- /mnt/bitlocker{W}")
        print(f"{Y}sudo mount -o loop /mnt/bitlocker/dislocker-file /mnt/bitlocker_mount{W}")

        print()
        return

    # =========================================================
    # UNMOUNT
    # =========================================================

    if getattr(args, "unmount", False):

        print(f"\n{B}┌── {BOLD}MODULE: VHD UNMOUNT{W}{B} ────────────────────────────┐{W}")
        print(f"{B}└────────────────────────────────────────────────────────────┘{W}")

        cmds = [

            ["sudo", "guestunmount", "/mnt/vhd"],

            ["sudo", "umount", "/mnt/bitlocker_mount"],

            ["sudo", "umount", "/mnt/bitlocker"],

            ["sudo", "losetup", "-D"]

        ]

        for cmd in cmds:

            try:
                run_cmd(cmd)
            except:
                pass

        print(f"\n{G}[+] {W}Unmount complete\n")
        return

    # =========================================================
    # TARGET FILE
    # =========================================================

    image = get_image()

    if not image:

        print(f"\n{R}[!] {W}{BOLD}MISSING IMAGE FILE{W}")
        print(f"{B}  └── Usage:{W} ctf mount.vhd backup.vhd")
        return

    image = Path(image).expanduser().resolve()

    if not image.exists():

        print(f"\n{R}[!] {W}{BOLD}FILE NOT FOUND{W}")
        print(f"{B}  └── {image}")
        return

    password = getattr(args, "password", None)

    # =========================================================
    # HUD
    # =========================================================

    print(f"\n{B}┌── {BOLD}MODULE: VHD MOUNTING{W}{B} ───────────────────────────┐{W}")

    print(
        f"{B}│{W}  {B}Image:{W} "
        f"{C}{image.name:<45}{W}"
        f"{B}│{W}"
    )

    if password:

        print(
            f"{B}│{W}  {B}Type:{W}  "
            f"{C}BitLocker{W}"
            f"{' ' * 42}{B}│{W}"
        )

    else:

        print(
            f"{B}│{W}  {B}Type:{W}  "
            f"{C}Standard VHD{W}"
            f"{' ' * 39}{B}│{W}"
        )

    print(f"{B}└────────────────────────────────────────────────────────────┘{W}")

    # =========================================================
    # STANDARD VHD
    # =========================================================

    if not password:

        os.makedirs("/mnt/vhd", exist_ok=True)

        cmd = [
            "sudo",
            "guestmount",
            "--add",
            str(image),
            "--inspector",
            "--ro",
            "/mnt/vhd"
        ]

        result = run_cmd(cmd)

        if result.returncode != 0:

            print(f"{R}[!] {W}Mount failed\n")
            print(result.stderr)

            return

        print(f"\n{G}[+] {W}Mounted successfully")
        print(f"{B}  └── {C}/mnt/vhd{W}\n")

        return [
            {
                "type": "mount",
                "data": {
                    "path": "/mnt/vhd",
                    "image": str(image)
                }
            }
        ]

    # =========================================================
    # BITLOCKER
    # =========================================================

    run_cmd([
        "sudo",
        "mkdir",
        "-p",
        "/mnt/bitlocker"
    ])

    run_cmd([
        "sudo",
        "mkdir",
        "-p",
        "/mnt/bitlocker_mount"
    ])

    losetup_cmd = [
        "sudo",
        "losetup",
        "-f",
        "-P",
        str(image)
    ]

    result = run_cmd(losetup_cmd)

    if result.returncode != 0:

        print(f"{R}[!] {W}Failed creating loop device")
        return

    loop_result = subprocess.run(
        ["losetup", "-j", str(image)],
        capture_output=True,
        text=True
    )

    match = re.search(r"(/dev/loop\d+)", loop_result.stdout)

    if not match:

        print(f"{R}[!] {W}Could not locate loop device")
        return

    loopdev = match.group(1)

    partition = get_largest_partition(loopdev)

    if not partition:

        print(f"{R}[!] {W}Could not locate partition")
        return

    print(f"{G}[+] {W}Partition selected: {C}{partition}{W}")

    dislocker_cmd = [
        "sudo",
        "dislocker",
        partition,
        f"-u{password}",
        "--",
        "/mnt/bitlocker"
    ]

    result = run_cmd(dislocker_cmd)

    if result.returncode != 0:

        print(f"{R}[!] {W}Dislocker failed")
        print(result.stderr)

        return

    mount_cmd = [
        "sudo",
        "mount",
        "-o",
        "loop",
        "/mnt/bitlocker/dislocker-file",
        "/mnt/bitlocker_mount"
    ]

    result = run_cmd(mount_cmd)

    if result.returncode != 0:

        print(f"{R}[!] {W}Final mount failed")
        print(result.stderr)

        return

    print(f"\n{G}[+] {W}Mounted successfully")
    print(f"{B}  └── {C}/mnt/bitlocker_mount{W}\n")

    subprocess.Popen(
        [
            "xdg-open",
            "/mnt/bitlocker_mount"
        ]
    )
    return [
        {
            "type": "mount",
            "data": {
                "path": "/mnt/bitlocker_mount",
                "image": str(image)
            }
        }
    ]