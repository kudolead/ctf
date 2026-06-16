# 02 — DNS Logs

**Category:** Blue team
**Difficulty:** Easy → Medium
**Flag:** `flag{...}` — canonical value in [`solution/ANSWER.md`](solution/ANSWER.md)

## Summary

Participants get a packet capture (`capture.pcap`) of otherwise-normal network
traffic with one host quietly exfiltrating data over DNS. The flag is encoded
across the subdomain labels of queries to an attacker-controlled domain. They
must filter DNS traffic, isolate the exfil queries, concatenate the encoded
labels in order, and decode them to recover the flag.

## Learning objectives

- Filter and read DNS traffic in Wireshark / `tshark`.
- Recognize DNS tunneling / exfiltration patterns (high query volume to one
  domain, long random-looking labels, `TXT`/`A`/`NULL` abuse).
- Reassemble data split across many queries and decode it (hex or Base32 —
  Base32 is realistic because DNS labels are case-insensitive and limited to
  `a-z0-9-`).

## Intended mechanics

1. Generate a background of benign DNS/HTTP traffic so the channel isn't obvious.
2. Pick an exfil domain, e.g. `exfil.attacker-c2.net`.
3. Encode the flag (Base32, lowercased, `=` padding stripped), split into chunks
   that fit a DNS label (≤63 chars; use ~30 for realism).
4. Emit sequential `A` queries: `<seq>.<chunk>.exfil.attacker-c2.net` so order is
   recoverable even if packets are reordered. (`seq` = zero-padded index.)
5. Interleave the exfil queries among benign queries.

To **solve**: `tshark -r capture.pcap -Y 'dns.qry.name contains "attacker-c2"' -T fields -e dns.qry.name`,
sort by `seq`, strip the domain suffix, concatenate chunks, Base32-decode.

### Difficulty knobs

- Easy: contiguous queries, obvious domain, hex encoding.
- Medium: shuffled order (rely on `seq`), Base32, buried in heavy benign traffic.
- Hard: encode in `TXT` record answers instead of query names, or add a second
  decoy exfil domain that decodes to a troll string.

## Artifacts to generate (`build/build.py` → `handout/`)

- `capture.pcap` — the packet capture (built with scapy; see deps).
- `brief.txt` — "An analyst flagged unusual DNS traffic from one host. Find what
  left the network."

## Solution outline

See [`solution/solve.py`](solution/solve.py) (parses the pcap with scapy/tshark
and decodes) and [`solution/ANSWER.md`](solution/ANSWER.md).

## Hint ladder

1. "Focus on DNS. Is one domain queried far more than the rest?"
2. "Look at the subdomain labels — they aren't random."
3. "Each query carries a sequence number and a chunk. Put them in order."
4. "The chunks are Base32. Concatenate and decode."

## Dependencies

`scapy` (root `requirements.txt`). `tshark` available on the participant box.
