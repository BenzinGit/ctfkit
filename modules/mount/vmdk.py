from pathlib import Path


def run(data, cred, args):
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    image = getattr(args, "file", None)

    if not image:
        print(f"\n{R}[!] {W}{BOLD}MISSING IMAGE FILE{W}")
        print(f"{B}  └── Usage:{W} ctf mount.vmdk <disk.vmdk>")
        return

    image = Path(image).expanduser().resolve()

    if not image.exists():
        print(f"\n{R}[!] {W}{BOLD}FILE NOT FOUND{W}")
        print(f"{B}  └── {image}")
        return

    mountpoint = "/mnt/vmdk"

    print(f"\n{B}┌── {BOLD}MODULE: VMDK MOUNTING{W}{B} ─────────────────────────┐{W}")
    print(f"{B}│{W}  {B}Image:{W} {image.name:<39}{B}│{W}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{W}")

    print(f"\n{G}[+] Create Mountpoint{W}\n")

    print(f"sudo mkdir -p {mountpoint}")

    print(f"\n{G}[+] Mount Image{W}\n")

    print(
        f"sudo guestmount -a {image} "
        f"-i --ro {mountpoint}"
    )

    print(f"\n{G}[+] Browse Files{W}\n")

    print(f"ls {mountpoint}")
    print(f"cd {mountpoint}")

    print(f"\n{G}[+] Extract Registry Hives{W}\n")

    print(f"cp {mountpoint}/Windows/System32/config/SAM .")
    print(f"cp {mountpoint}/Windows/System32/config/SYSTEM .")
    print(f"cp {mountpoint}/Windows/System32/config/SECURITY .")

    print(f"\n{G}[+] Dump Hashes{W}\n")

    print("ctf dump.hives")

    print(f"\n{G}[+] Unmount{W}\n")

    print(f"sudo guestunmount {mountpoint}\n")
