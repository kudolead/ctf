# 03 — SIEM Password Hunt

**Category:** Blue team / Incident response
**Difficulty:** Medium
**Flag:** `flag{...}` inside a password-protected zip — flag + password in
[`solution/ANSWER.md`](solution/ANSWER.md)

## Summary

Participants receive a bundle of SIEM logs and a password-protected zip
(`evidence.zip`). By tracing the attacker's actions across the logs they recover
**three fragments** of the zip password, each dropped at a different
"checkpoint" of the intrusion. Concatenating the three fragments in the right
order yields the password; opening the zip reveals the flag.

This mirrors a real IR exercise: reconstruct the kill chain, and the artifacts
you collect along the way *are* the key.

## Learning objectives

- Pivot across heterogeneous log sources (auth, web, process, network) to build
  an attack timeline.
- Recognize stages of an intrusion: initial access → execution / persistence →
  exfiltration.
- Extract indicators (encoded strings, filenames, user-agents) that double as
  password fragments.
- Use the recovered password to open an AES-encrypted zip.

## Intended mechanics — three checkpoints

Design the logs so each stage yields exactly one fragment. Order matters; make
the intended order discoverable (e.g. by timestamp or an explicit `part1/2/3`
marker baked into the planted artifact).

| # | Stage | Log source | Planted fragment artifact |
|---|-------|-----------|---------------------------|
| 1 | Initial access | Web server / auth log | A suspicious request whose param or User-Agent carries `part1` (e.g. base64 in a query string). |
| 2 | Execution / persistence | Process-creation / EDR log | A decoded command line (e.g. PowerShell `-enc`) that contains `part2`. |
| 3 | Exfiltration | Proxy / firewall / DNS log | An upload or beacon whose path/host encodes `part3`. |

Password = `part1 + part2 + part3` (define the join rule in ANSWER.md — e.g.
direct concat, or a `-` separator).

### Realism / difficulty knobs

- Bury each fragment among plausible benign noise.
- Encode fragments (Base64, hex) so participants must decode, not just grep.
- Add false fragments at non-checkpoint events to punish pattern-matching.
- Vary log formats (JSON lines vs. syslog vs. CLF) to force real parsing.

## Artifacts to generate (`build/build.py` → `handout/`)

- `logs/` — the SIEM log files (auth.log, web access log, process events JSONL,
  proxy log). Synthetic, internally consistent timeline.
- `evidence.zip` — AES-encrypted (via `pyzipper`) containing `flag.txt`.
- `brief.txt` — scenario framing + the goal: "Reconstruct the attack. The
  password to the evidence archive was scattered across three stages."

## Solution outline

[`solution/solve.py`](solution/solve.py) parses the logs, recovers the three
fragments, builds the password, and opens the zip to print the flag.
[`solution/ANSWER.md`](solution/ANSWER.md) holds the password, the three
fragments, and the full timeline.

## Hint ladder

1. "Build a timeline. How did they get in, what did they run, what left?"
2. "Three stages, three fragments. Each stage drops exactly one."
3. "Fragments are encoded — decode the suspicious request, the command line,
   and the upload path."
4. "Join the three fragments in stage order to get the zip password."

## Dependencies

`pyzipper` (root `requirements.txt`) for the AES zip. `unzip`/`7z` or `pyzipper`
to open it.
