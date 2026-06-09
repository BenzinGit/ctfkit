from core.runner import (
    run_module_by_name
)


PROVIDES = []
REQUIRES = []


PHASES = [

    (
        "INTELLIGENCE",
        [

            "web.whois",
            "dns.records",
            "web.headers",
            "web.whatweb",
            "web.waf"

        ]
    ),

    (
        "DNS DISCOVERY",
        [

            "dns.axfr",
            "dns.brute"

        ]
    ),

    (
        "VHOST DISCOVERY",
        [

            "web.vhost"

        ]
    ),

    (
        "CONTENT DISCOVERY",
        [

            "web.fuzz"

        ]
    ),

    (
        "CRAWLING",
        [

            "web.spider"

        ]
    ),

    (
        "HISTORICAL DATA",
        [

            "web.wayback"

        ]
    ),

    (
        "DEEP ENUMERATION",
        [

            "web.nikto"

        ]
    )

]


def show_playbook():

    B = '\033[94m'
    C = '\033[96m'
    W = '\033[0m'

    print()

    print(
        f"{B}┌── WEB RECON PLAYBOOK "
        f"────────────────────────┐{W}"
    )

    print()

    for idx, (phase_name, modules) in enumerate(
        PHASES,
        start=1
    ):

        print(
            f"{C}PHASE {idx} - "
            f"{phase_name}{W}"
        )

        print(
            f"{'-' * 40}"
        )

        for module in modules:

            print(
                f"  {module}"
            )

        print()

    print(
        f"{B}└───────────────────────────────────────────────┘{W}"
    )

    print()


def run_phase(
    phase_index,
    phase_name,
    modules,
    data
):

    G = '\033[92m'
    B = '\033[94m'
    Y = '\033[93m'
    W = '\033[0m'
    R = '\033[91m'

    print()

    print(
        f"{B}[ PHASE "
        f"{phase_index}/{len(PHASES)} ] "
        f"{phase_name}{W}"
    )

    print()

    completed = []
    failed = []

    for idx, module in enumerate(
        modules,
        start=1
    ):

        print(
            f"{Y}[{idx}/{len(modules)}]{W} "
            f"{module}"
        )

        try:

            run_module_by_name(
                module,
                [],
                data
            )

            completed.append(
                module
            )

        except Exception as e:

            print(
                f"{R}[!]{W} "
                f"Failed: {module}"
            )

            print(
                f"    {e}"
            )

            failed.append(
                module
            )

    print()

    print(
        f"{G}[+]{W} "
        f"Completed: "
        f"{len(completed)}"
    )

    if failed:

        print(
            f"{R}[-]{W} "
            f"Failed: "
            f"{len(failed)}"
        )

    print()

    return completed, failed


def run_guided(data):

    G = '\033[92m'
    Y = '\033[93m'
    W = '\033[0m'

    completed = []
    failed = []

    for phase_index, (
        phase_name,
        modules
    ) in enumerate(
        PHASES,
        start=1
    ):

        print()

        print(
            f"{Y}Run Phase "
            f"{phase_index}: "
            f"{phase_name}"
            f"?{W}"
        )

        choice = input(
            "[Y/n]: "
        ).strip().lower()

        if choice == "n":

            continue

        c, f = run_phase(
            phase_index,
            phase_name,
            modules,
            data
        )

        completed.extend(c)
        failed.extend(f)

        print()

        print(
            f"{G}[+]{W} "
            f"Phase complete."
        )

        print(
            "Review findings before continuing."
        )

        print()

    return completed, failed


def run_single_phase(data):

    print()

    for idx, (
        phase_name,
        _
    ) in enumerate(
        PHASES,
        start=1
    ):

        print(
            f"{idx}) "
            f"{phase_name}"
        )

    print()

    choice = input(
        "Phase: "
    ).strip()

    try:

        idx = int(choice) - 1

    except ValueError:

        return [], []

    if idx < 0 or idx >= len(PHASES):

        return [], []

    phase_name, modules = (
        PHASES[idx]
    )

    return run_phase(
        idx + 1,
        phase_name,
        modules,
        data
    )


def run_auto(data):

    completed = []
    failed = []

    for phase_index, (
        phase_name,
        modules
    ) in enumerate(
        PHASES,
        start=1
    ):

        c, f = run_phase(
            phase_index,
            phase_name,
            modules,
            data
        )

        completed.extend(c)
        failed.extend(f)

    return completed, failed


def print_summary(
    completed,
    failed
):

    G = '\033[92m'
    R = '\033[91m'
    C = '\033[96m'
    W = '\033[0m'

    print()

    print(
        f"{C}WEB RECON COMPLETE{W}"
    )

    print()

    if completed:

        print(
            f"{G}Completed:{W}"
        )

        for module in completed:

            print(
                f"  ✓ {module}"
            )

        print()

    if failed:

        print(
            f"{R}Failed:{W}"
        )

        for module in failed:

            print(
                f"  ✗ {module}"
            )

        print()


def run(data, cred, args):

    show_playbook()

    print(
        "1) Guided"
    )

    print(
        "2) Run Single Phase"
    )

    print(
        "3) Auto"
    )

    print(
        "0) Exit"
    )

    print()

    choice = input(
        "Select: "
    ).strip()

    if choice == "0":

        return

    elif choice == "1":

        completed, failed = (
            run_guided(data)
        )

    elif choice == "2":

        completed, failed = (
            run_single_phase(data)
        )

    elif choice == "3":

        completed, failed = (
            run_auto(data)
        )

    else:

        return

    print_summary(
        completed,
        failed
    )
