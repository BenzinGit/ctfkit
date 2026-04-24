def run(data, cred, args):
    from pathlib import Path
    import subprocess

    name = args.extra[0] if args.extra else None

    if not name:
        print("[!] Usage: ctf bloodhound.stop <name>")
        return

    BASE = Path.home() / ".ctfkit" / "bloodhound"
    instance_dir = BASE / name
    compose_file = instance_dir / "docker-compose.yml"

    if not compose_file.exists():
        print(f"[!] Instance not found: {name}")
        return

    print(f"[*] Stopping BloodHound instance: {name}")

    subprocess.run([
        "docker", "compose",
        "-f", str(compose_file),
        "down"
    ])

    print("[+] Stopped")
