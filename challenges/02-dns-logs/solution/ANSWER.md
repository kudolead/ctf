# Answer — DNS Logs

**Flag:** `flag{REPLACE_ME_dns_exfil}`
**Exfil domain:** `exfil.attacker-c2.net`
**Encoding:** Base32 (lowercased, padding stripped), chunked across labels.

## Quick solve (tshark)

```bash
tshark -r capture.pcap -Y 'dns.qry.name contains "attacker-c2"' \
       -T fields -e dns.qry.name \
  | sort -t. -k1 -n \
  | sed -E 's/\.exfil\.attacker-c2\.net$//; s/^[0-9]+\.//' \
  | tr -d '\n' \
  | python3 -c 'import sys,base64; s=sys.stdin.read().upper(); s+="="*(-len(s)%8); print(base64.b32decode(s).decode())'
```

> Replace the flag once `build/build.py` is implemented.

## Walkthrough notes

- The tell is query volume + long non-dictionary labels to a single domain.
- The `seq` label makes reassembly robust to packet reordering.
