from pathlib import Path


def run(data, cred, args):
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    image = getattr(args, "file", None)

    if not image:
        print(f"\n{R}[!] {W}{BOLD}MISSING IMAGE FILE{W}")
        print(f"{B}  └── Usage:{W} ctf mount.vhd <disk.vhdx>")
        return

    image = Path(image).expanduser().resolve()

    if not image.exists():
        print(f"\n{R}[!] {W}{BOLD}FILE NOT FOUND{W}")
        print(f"{B}  └── {image}")
        return

    mountpoint = "/mnt/vhdx"

    print(f"\n{B}┌── {BOLD}MODULE: VHD/VHDX MOUNTING{W}{B} ─────────────────────┐{W}")
    print(f"{B}│{W}  {B}Image:{W} {image.name:<39}{B}│{W}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{W}")

    print(f"\n{G}[+] Create Mountpoint{W}\n")

    print(f"sudo mkdir -p {mountpoint}")

    print(f"\n{G}[+] Mount Image{W}\n")

    print(
        f"sudo guestmount --add {image} "
        f"--ro {mountpoint} "
        f"-m /dev/sda1"
    )

    print(f"\n{G}[+] Browse Files{W}\n")

    print(f"ls {mountpoint}")
    print(f"cd {mountpoint}")

    print(f"\n{G}[+] Unmount{W}\n")

    print(f"sudo guestunmount {mountpoint}\n")
