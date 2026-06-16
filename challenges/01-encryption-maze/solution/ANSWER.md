# Answer — Encryption Maze

**Flag:** `flag{p33l_th3_3ncrypt10n_m4z3}`

## CyberChef recipe (outer → inner)

Drop `cipher.txt` into the input and stack these operations top-to-bottom:

1. **From Base64**
2. **From Hex**
3. **Reverse** — *Reverse by: Character* (this is the red-herring layer; it is
   not a "decode," just an order flip)
4. **ROT13** — leave *Rotate lower/upper case* on, *Rotate numbers* **off**
5. **From Base58** — alphabet `123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz` (Bitcoin, the default)
6. **XOR** — Key: `maze` (UTF-8)

Output: `flag{p33l_th3_3ncrypt10n_m4z3}`

## What the participant sees at each peel

| Step | Output |
|------|--------|
| input (`cipher.txt`) | `MzM0NjZm…UTM=` (Base64; `=` padding is the tell) |
| From Base64 | `33466f4c6d737538…5151513` (hex — only `0-9a-f`) |
| From Hex | `3FoLmsu8xgP2Ug2rFTjpTTumia1YUK8KRHPvD7FQ3` (looks like a token) |
| Reverse | `3QF7DvPHRK8KUY1aimuTTpjTFr2gU2Pgx8usmLoF3` |
| ROT13 | `3DS7QiCUEX8XHL1nvzhGGcwGSe2tH2Ctk8hfzYbS3` (valid Base58) |
| From Base58 | 28 non-printable bytes — the XOR ciphertext |
| XOR `maze` | `flag{p33l_th3_3ncrypt10n_m4z3}` |

## Walkthrough notes

- **Base64 → Hex → looks-like-a-token.** Magic peels Base64 and Hex for free.
  After Hex you get a 41-char alphanumeric string. Magic will *not* reliably
  call the next move, because it is a **reverse**, not a codec — the discipline
  test. A junior who keeps spamming Magic stalls here; the move is to notice
  nothing decodes and try a transpose/reverse.
- **Reverse → ROT13.** After reversing, the string is still alphanumeric.
  ROT13 turns it into a valid Base58 string (Magic may now suggest ROT13).
- **Base58, not Base64.** The alphabet has no `0`, `O`, `I`, or `l` and no `+`/`/`
  — that is the giveaway it is Base58. Magic ranks Base58 below Base64, so the
  participant should recognize it by alphabet rather than trusting Magic's top
  pick.
- **XOR key recovery (the main time sink).** From Base58 yields raw bytes that
  decode to nothing. Because the plaintext starts with the known crib `flag{`,
  XOR the first 5 cipher bytes against `flag{` to recover the keystream
  `m a z e m`. The repeat (`m` at positions 0 and 4) reveals the period is 4, so
  the key is `maze`. `solution/solve.py:recover_key` performs exactly this and
  reduces the keystream to its minimal period.

## Reproduce programmatically

```
python build/build.py      # regenerates handout/cipher.txt + brief.txt
python solution/solve.py   # prints the recovered key (stderr) and flag (stdout)
```

The flag and XOR key are defined once at the top of `build/build.py`
(`FLAG`, `XOR_KEY`) and are the single source of truth.
