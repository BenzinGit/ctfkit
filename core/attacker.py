import subprocess

def get_ip(interface="tun0"):
    try:
        result = subprocess.check_output(
            ["ip", "addr", "show", interface],
            text=True
        )
        for line in result.splitlines():
            line = line.strip()
            if line.startswith("inet "):
                return line.split()[1].split("/")[0]
    except Exception:
        return None


def resolve_lhost(args):
    # 1. Explicit argument wins
    if hasattr(args, "lhost") and args.lhost:
        return args.lhost

    # 2. Try interface from args
    if hasattr(args, "interface") and args.interface:
        ip = get_ip(args.interface)
        if ip:
            return ip

    # 3. Default to tun0
    return get_ip("tun0")