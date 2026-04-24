def run(data, cred, args):
    from pathlib import Path
    import subprocess
    import socket
    import time

    name = args.extra[0] if args.extra else None
    if not name:
        print("[!] Usage: ctf bloodhound.new <name>")
        return

    BASE = Path.home() / ".ctfkit" / "bloodhound"
    instance_dir = BASE / name
    if instance_dir.exists():
        print(f"[!] Instance already exists: {name}")
        return
    instance_dir.mkdir(parents=True)

    def get_free_port():
        s = socket.socket()
        s.bind(("", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    web_port = get_free_port()

    # Using the exact variables from your working cat output
    compose_content = f"""
services:
  app-db:
    image: docker.io/library/postgres:16
    container_name: bh_{name}_postgres
    environment:
      - POSTGRES_USER=bloodhound
      - POSTGRES_PASSWORD=bloodhoundcommunityedition
      - POSTGRES_DB=bloodhound
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U bloodhound -d bloodhound -h 127.0.0.1 -p 5432"]
      interval: 5s
      timeout: 5s
      retries: 5

  graph-db:
    image: docker.io/library/neo4j:4.4
    container_name: bh_{name}_neo4j
    environment:
      - NEO4J_AUTH=neo4j/bloodhoundcommunityedition
      - NEO4J_dbms_allow__upgrade=true
    healthcheck:
      test: ["CMD-SHELL", "wget -O /dev/null -q http://localhost:7474 || exit 1"]
      interval: 5s
      timeout: 5s
      retries: 10

  bloodhound:
    image: docker.io/specterops/bloodhound:latest
    container_name: bh_{name}_app
    ports:
      - "{web_port}:8080"
    environment:
      - bhe_database_connection=user=bloodhound password=bloodhoundcommunityedition dbname=bloodhound host=app-db
      - bhe_neo4j_connection=neo4j://neo4j:bloodhoundcommunityedition@graph-db:7687/
      - bhe_enable_text_logger=true
    depends_on:
      app-db:
        condition: service_healthy
      graph-db:
        condition: service_healthy
    restart: unless-stopped
"""

    compose_file = instance_dir / "docker-compose.yml"
    compose_file.write_text(compose_content.strip())

    print(f"[+] Launching BloodHound instance: {name}")
    
    # We use -v to ensure no old auth data exists
    subprocess.run(["docker", "compose", "-f", str(compose_file), "down", "-v"], capture_output=True)
    
    # Start everything - the 'depends_on' with 'service_healthy' handles the timing now
    subprocess.run(["docker", "compose", "-f", str(compose_file), "up", "-d"])

    print(f"[*] Services started. It may take 30-60s for the admin password to appear in logs.")
    print(f"[+] Web UI: http://localhost:{web_port}")