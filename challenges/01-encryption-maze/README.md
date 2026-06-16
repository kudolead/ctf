# 01 — Encryption Maze

**Category:** Forensics / Encoding
**Difficulty:** Medium (ramps across 7 stages; ~3-4 hours for a junior)
**Flags:** seven chained stage flags — canonical/master in [`solution/ANSWER.md`](solution/ANSWER.md)

## Summary

A self-guiding, 7-stage CyberChef maze. Participants receive a single blob
(`cipher.txt`). Each stage, when correctly processed, reveals a block containing
(1) that stage's flag, (2) instructions teaching the next CyberChef technique,
and (3) the next stage's ciphertext. The maze narrates its own curriculum — the
player never needs to leave CyberChef. Difficulty ramps so each stage forces a
*distinct* skill; the Magic op alone cannot finish it.

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

## Hint ladder (one rung per stuck stage)

1. Stage 1: the trailing `=` and the alphabet say Base64. Try Magic.
2. Stage 2: this isn't Base64 — count the punctuation. It's Base85 (`From Base85`, alphabet `!-u`).
3. Stage 3: it's a Vigenère cipher; the key is the keyword from your last flag (`alphabet`).
4. Stage 4: `From Base64`, then XOR. You weren't given the key — every flag is `flag{maze_N_...}`, so crib-drag `flag{maze_4_` to recover it.
5. Stage 5: `From Hex`, then read the first bytes — `1f 8b` is gzip. `Gunzip`.
6. Stage 6: `From Base64` then `Render Image`. The flag is in the picture — and there's data after the PNG's `IEND`.
7. Stage 7: `Register` the salt, `Subsection` the payload, `Fork` on `|`, `From Hex`, `XOR` key `pixels$R0` (UTF8), `Merge`.
