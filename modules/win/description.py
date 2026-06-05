def run(data, cred, args):
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    print(f"\n{B}┌── {BOLD}MODULE: DESCRIPTION ENUMERATION{W}{B} ─────────────────┐{W}")
    print(f"{B}└────────────────────────────────────────────────────┘{W}")

    print(f"\n{G}[+] Local User Descriptions{W}")
    print(r"""
Get-LocalUser | Select Name,Description
""")

    print(f"\n{G}[+] Computer Description{W}")
    print(r"""
Get-WmiObject -Class Win32_OperatingSystem | Select Description
""")

    print()
