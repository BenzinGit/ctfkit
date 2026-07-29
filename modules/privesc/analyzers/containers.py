"""
CTFKit - Linux PrivEsc
Docker Container Analyzer
"""


# ==========================================
# PARSER
# ==========================================

def _parse(section):

    sockets = []

    for line in section.splitlines():

        line = line.strip()

        if not line:
            continue

        if line.startswith(">>>"):
            continue

        if "docker.sock" in line:
            sockets.append(line)

    return sockets


# ==========================================
# PUBLIC API
# ==========================================

def analyze(section):
    sockets = _parse(section)

    findings = []

    details = {
        "Sockets": sockets
    }
    for socket in sockets:
        socket_path = socket.split()[-1]

        findings.append({

            "priority": "HIGH",
            "module": "DOCKER",
            "title": socket_path,
            "reason": "Docker socket discovered",
            "recommendation": [
                "Check if the socket is writable.",
                f"Use: ctf privesc.linux.containers.dockersock {socket_path}"
            ]

        })

    return {

        "module": "DOCKER",

        "summary": {
            "Sockets": len(sockets)
        },

        "findings": findings,

        "details": details

    }
