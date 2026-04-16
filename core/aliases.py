ALIASES = {
    "target": {
        "aliases": ["target", "t", "aim"],
        "actions": {
            "create": ["create", "new", "add"],
            "list": ["list", "ls", "all"],
            "use": ["use", "set", "select"],
            "show": ["show", "info"],
            "creds": ["creds", "credentials", "c"],
            "set-cred": ["set-cred", "sc", "use-cred"],
            "add-cred": ["add-cred", "ac", "new-cred", "nc"],
            "add-domain": ["add-domain", "new-domain", "create-domain"]
        }
    },

    "smb": {
        "aliases": ["smb", "445"],
        "actions": {
            "list": ["list", "ls", "shares"],
            "connect": ["connect", "conn"]
        }
    },

    "util": {
        "aliases": ["util", "uma"],
        "actions": {
            "ping": ["ping", "pong"]
        }
    },

     "nmap": {
        "aliases": ["nmap"],
        "actions": {
            "scan": ["scan", "run"],
            "fast": ["fast", "quick"]

        }
    }
}
