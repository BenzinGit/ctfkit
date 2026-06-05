ALIASES = {
    "target": {
        "aliases": ["target", "t", "host", "hosts", "targets"],
        "actions": {
            "create": ["create", "create-target", "new", "new-target", "add", "add-target"],
            "list": ["list", "ls", "all"],
            "use": ["use", "set", "select", "switch"],
            "show": ["show", "info", "target-info", "host-info"],
            "creds": ["creds","credentials", "c", "users", "accounts", "list-creds", "list-users", "ls-creds", "ls-users"],
            "set-cred": ["set-cred", "set-user", "use-cred", "use.user", "select-cred", "select-user", "switch-cred", "switch-user", "su"],
            "add-cred": ["add-cred", "add-user","new-cred","new-user","create-cred","create-user","useradd"],
            "add-domain": ["add-domain", "ad", "new-domain", "create-domain"],
            "delete": ["delete", "remove"],
            "set-url": ["set-url", "switch-url", "use-url", "seturl", "switchurl", "newurl" "surl"],
            "add-url":["add-url", "new-url", "addurl", "aurl"]


        }
    },

    "smb": {
        "aliases": ["smb", "445"],
        "actions": {
            "list": ["list", "ls"],
            "connect": ["connect", "conn"]
        }
    },

    "util": {
        "aliases": ["util", "utility"],
        "actions": {
            "ping": ["ping"]
        }
    },

     "nmap": {
        "aliases": ["nmap"],
        "actions": {
            "scan": ["scan", "run"],
            "fast": ["fast", "quick"]

        }
    },
     "win": {
        "aliases": ["win", "windows"],
        "actions": {
            "upload": ["upload", "drop"],
            "clipboard": ["clipboard", "clip"]

        }
     
    },
     "ad": {
        "aliases": ["ad", "active-directory"],
        "actions": {
            "collect": ["collect", "bloodhound", "bh"]
        }
     
    },

    "privesc": {
        "aliases": ["privesc", "pe"],
        "actions": {
            "sudo": ["sudo"]
        }
     
    },
     
    "upload": {
        "aliases": ["upload", "drop"],
        "actions": {
            "windows": ["windows", "win", "w"],
            "linux": ["linux", "lin", "l"]

        }

    },

    "download": {
        "aliases": ["download", "grab"],
        "actions": {
            "windows": ["windows", "win", "w"],
            "linux": ["linux", "lin", "l"]

        }

    }
    

        
}