# 01 — Encryption Maze

**Category:** Forensics / Encoding
**Difficulty:** Hard — unguided (ramps across 7 stages; ~3-4 hours for a junior)
**Flags:** seven chained stage flags — canonical/master in [`solution/ANSWER.md`](solution/ANSWER.md)

## Summary

An **unguided** 7-stage CyberChef maze. Participants receive a single blob
(`cipher.txt`). Each stage, when correctly processed, reveals only that stage's
flag and the next stage's ciphertext — **no instructions**. The player must
recognise every encoding and cipher on their own. Difficulty ramps so each stage
forces a *distinct* skill; the Magic op alone cannot finish it. (An earlier
revision narrated the next technique in-band; that guidance was removed to raise
the difficulty.)

## Curriculum

| # | CyberChef skill | Mechanic | Key source |
|---|---|---|---|
| 1 | Magic op, Base64, recipe view | From Base64 | — |
| 2 | Recognise an encoding by its alphabet (Magic under-ranks Base85) | From Base85 (`!-u`) | — |
| 3 | Classic ciphers | Vigenère Decode, key `alphabet` | keyword from flag 2 |
| 4 | XOR + multi-byte key recovery via crib | From Base64 → XOR key `vigenere` | keyword from flag 3 |
| 5 | Recognise magic bytes, decompress | From Hex → Gunzip (`1f 8b`) | — |
| 6 | Binary/file handling + file carving | From Base64 → Render Image; carve after `IEND` | — |
| 7 | Registers + Subsection + Fork | Register/Subsection/Fork/From Hex/XOR/Merge | keyword from flag 6 + register salt |

## Chaining modes

- **Keyed handoff** (stages 3, 4, 7): the key is the keyword from the previous
  stage's flag — you cannot skip a stage because its flag word is required next.
- **Positional handoff** (stages 2, 5, 6): no key; the previous block simply
  embeds the next ciphertext.

## Difficulty rationale

Magic peels the easy encodings (Base64/Hex) for free, so the friction sits where
Magic fails: recognising Base85 by alphabet, recovering the multi-byte XOR key
from the `flag{maze_4_` crib, spotting gzip magic bytes, carving data after a
PNG's `IEND`, and wiring CyberChef's register/subsection/fork flow-control for
the boss. Hands-on execution across seven escalating techniques targets ~3-4
hours for a junior.

## Artifacts (`build/build.py` → `handout/`)

- `cipher.txt` — the single starting blob.
- `brief.txt` — the up-front prompt ("Peel it back. … collect all seven.").

## Solution

See [`solution/ANSWER.md`](solution/ANSWER.md) for the per-stage CyberChef recipe
and all flags, and [`solution/solve.py`](solution/solve.py) for the programmatic
reference solver (prints all seven flags; doubles as the solvability check).

## Hints

This challenge is intentionally **unguided** — there is no player-facing hint
ladder. The complete per-stage CyberChef recipe lives only in
[`solution/ANSWER.md`](solution/ANSWER.md) as the author key.
