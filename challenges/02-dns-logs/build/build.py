#!/usr/bin/env python3
"""Build the DNS Logs handout (a pcap with DNS exfiltration).

STATUS: stub. Generate benign DNS traffic plus a sequence of exfil queries that
encode FLAG across subdomain labels, then write capture.pcap into ../handout/.

Contract (see /CONVENTIONS.md):
- FLAG is the single source of truth.
- Write only into the sibling handout/ directory.
- Seed any randomness so the pcap is reproducible.
"""
from __future__ import annotations

from pathlib import Path

FLAG = "flag{REPLACE_ME_dns_exfil}"
EXFIL_DOMAIN = "exfil.attacker-c2.net"
SEED = 1337

HANDOUT = Path(__file__).resolve().parent.parent / "handout"


def build_pcap() -> "list":
    """Return a list of scapy packets: benign traffic + interleaved exfil queries.

    TODO:
    - Base32-encode FLAG, strip padding, lowercase, chunk to ~30 chars.
    - Emit A queries of the form <seq>.<chunk>.EXFIL_DOMAIN.
    - Generate benign DNS queries to common domains as cover.
    - Interleave and (optionally) shuffle; seq preserves order.
    """
    raise NotImplementedError("Build the DNS exfil pcap for DNS Logs")


def main() -> None:
    HANDOUT.mkdir(exist_ok=True)
    # from scapy.all import wrpcap
    # packets = build_pcap()
    # wrpcap(str(HANDOUT / "capture.pcap"), packets)
    build_pcap()
    (HANDOUT / "brief.txt").write_text(
        "An analyst flagged unusual DNS traffic from one host. "
        "Find what left the network.\n",
        encoding="utf-8",
    )
    print(f"wrote capture.pcap and brief.txt to {HANDOUT}")


if __name__ == "__main__":
    main()
