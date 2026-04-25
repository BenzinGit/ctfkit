def run(data, cred, args):
    import subprocess
    from pathlib import Path

    name = args.extra[0] if args.extra else None
    if not name:
        print("[!] Usage: ctf bloodhound.start <name>")
        return

    # Locate the compose file we generated earlier
    compose_file = Path.home() / ".ctfkit" / "bloodhound" / name / "docker-compose.yml"

    if not compose_file.exists():
        print(f"[!] No configuration found for instance: {name}")
        return

    print(f"[+] Waking up BloodHound instance: {name}...")
    
    # Run 'up -d' again. Docker is smart: if the containers exist, it just starts them.
    # If they don't exist, it recreates them using the existing volumes (data is safe).
    subprocess.run(["docker", "compose", "-f", str(compose_file), "up", "-d"])

    print(f"[+] Instance {name} is rising from the grave.")