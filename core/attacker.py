import subprocess
from core.target import get_current_proxy

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


def resolve_lhost(args=None, data=None):

    #
    # 0. Active proxy (highest priority)
    #

    if data:

        proxy = get_current_proxy(data)

        if proxy:
            return proxy

    #
    # 1. Explicit --lhost
    #

    if args and hasattr(args, "lhost") and args.lhost:
        return args.lhost

    #
    # 2. Interface supplied
    #

    if args and hasattr(args, "interface") and args.interface:

        ip = get_ip(args.interface)

        if ip:
            return ip

    #
    # 3. tun0
    #

    ip = get_ip("tun0")

    if ip:
        return ip

    return None


def get_current_interface():
    return "tun0"