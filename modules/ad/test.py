def run(data, cred, args):
    print(f"[*] Dummy module loaded!")
    print(f"[*] My __name__ is: {__name__}")
    
    try:
        from module.parse_hash import parse_line
        print("[+] Success: I can see 'module.parse_hash'")
    except ImportError as e:
        print(f"[-] Failure: I cannot see 'module.parse_hash' -> {e}")

    return [{"user": "dummy", "type": "test", "secret": "success"}]