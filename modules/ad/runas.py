def run(
    data,
    cred,
    args,
):

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    W = '\033[0m'

    domain = data.get(
        "domain",
        "DOMAIN"
    )
    target_user = input(
        f"{Y}Username> {W}"
    ).strip()
    print(
        f"\n{G}[+] {W}RunAs\n"
    )

    print(
        f"{Y}runas /user:{C}{domain}\\{target_user}{Y} cmd.exe{W}"
    )

    print()

    print(
        f"{Y}runas /user:{C}{domain}\\{target_user}{Y} powershell.exe{W}"
    )

    print()

    print(
        f"{G}[+] {W}NetOnly\n"
    )

    print(
        f"{Y}runas /netonly /user:{C}{domain}\\{target_user}{Y} cmd.exe{W}"
    )

    print()

    print(
        f"{Y}runas /netonly /user:{C}{domain}\\{target_user}{Y} powershell.exe{W}"
    )

    print()
