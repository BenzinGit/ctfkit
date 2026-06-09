# modules/crack/hashdb.py

import re

HASH_TYPES = [

    # =====================================================
    # ACTIVE DIRECTORY
    # =====================================================

    {
        "name": "ASREP",
        "mode": "18200",
        "category": "AD",
        "aliases": [
            "ASREP",
            "ASREPROAST",
        ],
        "confidence": 100,
        "match": lambda s: "$krb5asrep$" in s,
    },

    {
        "name": "Kerberoast",
        "mode": "13100",
        "category": "AD",
        "aliases": [
            "KERBEROAST",
            "KERBEROS",
            "TGS",
        ],
        "confidence": 100,
        "match": lambda s: "$krb5tgs$" in s,
    },

    {
        "name": "NetNTLMv2",
        "mode": "5600",
        "category": "AD",
        "aliases": [
            "NETNTLMV2",
        ],
        "confidence": 100,
        "match": lambda s: "::" in s and "$" not in s,
    },

    {
        "name": "NetNTLMv1",
        "mode": "5500",
        "category": "AD",
        "aliases": [
            "NETNTLMV1",
        ],
        "confidence": 90,
        "match": lambda s: "::" in s and len(s.split(":")) >= 5,
    },

    {
        "name": "DCC2",
        "mode": "2100",
        "category": "AD",
        "aliases": [
            "DCC2",
            "MSCACHE2",
            "MSCASH2",
        ],
        "confidence": 90,
        "match": lambda s: "$DCC2$" in s.upper(),
    },

    # =====================================================
    # WINDOWS
    # =====================================================

    {
        "name": "NTLM",
        "mode": "1000",
        "category": "Windows",
        "aliases": [
            "NTLM",
            "NTHASH",
        ],
        "confidence": 60,
        "match": lambda s: re.fullmatch(
            r"[a-fA-F0-9]{32}",
            s
        ),
    },

    {
        "name": "LM",
        "mode": "3000",
        "category": "Windows",
        "aliases": [
            "LM",
        ],
        "confidence": 50,
        "match": lambda s: re.fullmatch(
            r"[a-fA-F0-9]{32}",
            s
        ),
    },

    # =====================================================
    # NETWORK
    # =====================================================

    {
        "name": "IPMI",
        "mode": "7300",
        "category": "Network",
        "aliases": [
            "IPMI",
        ],
        "confidence": 100,
        "match": lambda s: (
            ":" in s
            and len(s.split(":")) == 3
        ),
    },

    # =====================================================
    # GENERIC
    # =====================================================

    {
        "name": "MD5",
        "mode": "0",
        "category": "Generic",
        "aliases": [
            "MD5",
        ],
        "confidence": 40,
        "match": lambda s: re.fullmatch(
            r"[a-fA-F0-9]{32}",
            s
        ),
    },

    {
        "name": "SHA1",
        "mode": "100",
        "category": "Generic",
        "aliases": [
            "SHA1",
        ],
        "confidence": 90,
        "match": lambda s: re.fullmatch(
            r"[a-fA-F0-9]{40}",
            s
        ),
    },

    {
        "name": "SHA256",
        "mode": "1400",
        "category": "Generic",
        "aliases": [
            "SHA256",
        ],
        "confidence": 90,
        "match": lambda s: re.fullmatch(
            r"[a-fA-F0-9]{64}",
            s
        ),
    },

    {
        "name": "bcrypt",
        "mode": "3200",
        "category": "Generic",
        "aliases": [
            "BCRYPT",
        ],
        "confidence": 100,
        "match": lambda s: (
            s.startswith("$2a$")
            or s.startswith("$2b$")
            or s.startswith("$2y$")
        ),
    },

]