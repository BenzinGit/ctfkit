def run(data, cred, args):
    from pathlib import Path
    import subprocess
    import shutil

    name = args.extra[0] if args.extra else None

    if not name:
        print("[!] Usage: ctf bloodhound.rm <name>")
        return

    BASE = Path.home() / ".ctfkit" / "bloodhound"
    instance_dir = BASE / name
    compose_file = instance_dir / "docker-compose.yml"

    if not instance_dir.exists():
        print(f"[!] Instance not found: {name}")
        return

    print(f"[*] Removing BloodHound instance: {name}")

    # Stop + remove containers + volumes
    if compose_file.exists():
        subprocess.run([
            "docker", "compose",
            "-f", str(compose_file),
            "down",
            "--volumes",
            "--remove-orphans"
        ])

    # Force delete folder (even if owned by root)
    subprocess.run([
        "sudo", "rm", "-rf", str(instance_dir)
    ])




    print("[+] Removed completely")
