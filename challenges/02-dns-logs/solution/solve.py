#!/usr/bin/env python3
"""Reference solver for DNS Logs.

STATUS: stub. Parse capture.pcap, extract exfil queries to EXFIL_DOMAIN, order
by sequence, concatenate the chunks, Base32-decode, and print the flag.

Contract (see /CONVENTIONS.md):
- Read only from ../handout/.
- Print the recovered flag as the final stdout line.
- Exit non-zero if the flag cannot be recovered.
"""
from __future__ import annotations

import sys
from pathlib import Path

HANDOUT = Path(__file__).resolve().parent.parent / "handout"
EXFIL_DOMAIN = "exfil.attacker-c2.net"


def recover_flag(pcap_path: Path) -> str:
    """Extract and decode the exfiltrated flag from the capture.

    TODO: read pcap (scapy rdpcap or tshark), filter EXFIL_DOMAIN queries,
    sort by seq label, join chunks, Base32-decode.
    """
    raise NotImplementedError("Implement DNS exfil recovery for DNS Logs")


def main() -> int:
    flag = recover_flag(HANDOUT / "capture.pcap")
    if not flag.startswith("flag{"):
        print("failed to recover flag", file=sys.stderr)
        return 1
    print(flag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
