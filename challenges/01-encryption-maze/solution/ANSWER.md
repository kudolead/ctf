# Answer — Encryption Maze (7-stage)

Seven flags; the master flag is the canonical submission. Flags chain: each
stage's keyword unlocks the next keyed stage.

| Stage | Flag |
|-------|------|
| 1 | `flag{maze_1_trust_the_magic}` |
| 2 | `flag{maze_2_alphabet}` |
| 3 | `flag{maze_3_vigenere}` |
| 4 | `flag{maze_4_crib_and_brute}` |
| 5 | `flag{maze_5_inflate}` |
| 6 | `flag{maze_6_pixels}` |
| 7 (master) | `flag{maze_7_full_recipe_unl0ck3d}` |

## CyberChef recipe per stage

1. **From Base64** -> flag 1 + instructions + a Base85 blob.
2. **From Base85** (Alphabet: standard `!-u`) -> flag 2 + a Vigenere blob.
3. **Vigenere Decode**, Key `alphabet` (the keyword from flag 2) -> flag 3 + a
   Base64/XOR blob.
4. **From Base64**, then **XOR**, Key `vigenere`, key type **UTF8**.
   Key recovery: the block starts with the crib `flag{maze_4_`; XOR it against
   the first 12 bytes -> keystream `vigenerevige`, period 8 -> key `vigenere`
   (flag 3's keyword). The **XOR Brute Force** op demonstrates the single-byte
   case. -> flag 4 + a hex blob.
5. **From Hex** (bytes begin `1f 8b 08` = gzip) -> **Gunzip** -> flag 5 + a
   Base64 blob.
6. **From Base64** -> **Render Image**; flag 6 is drawn on the bitmap. The PNG
   ends at its `IEND` chunk; the bytes after it (skip `IEND` + the 4-byte CRC =
   8 bytes past the start of `IEND`) are the boss input -- carve them.
7. Boss (build this recipe top-to-bottom):
   - **Register**, Extractor `salt:(\w+)` -> captures `n3o` into `$R0`
   - **Subsection**, Section (regex) `payload:([0-9a-f|]+)` -> targets only the hex payload
   - **Fork**, Split delimiter `|`, Merge delimiter empty
   - **From Hex**
   - **XOR**, Key `pixels$R0`, key type **UTF8** (CyberChef substitutes `$R0` ->
     `n3o`, so the effective key is `pixelsn3o`)
   - **Merge** (closes the Fork)
   - **Merge** (closes the Subsection)
   The decoded payload contains the master flag `flag{maze_7_full_recipe_unl0ck3d}`.

## Notes

- **Key field types matter:** the XOR key fields in stages 4 and 7 must be set
  to **UTF8** (not Hex/Base64), or the key bytes are misread.
- Flags chain: stage 2's keyword (`alphabet`) is the stage-3 Vigenere key; stage
  3's keyword (`vigenere`) is the stage-4 XOR key; stage 6's keyword (`pixels`)
  plus the registered salt (`n3o`) is the boss key (`pixelsn3o`).
- The salt `n3o` is fixed in `build/build.py`; flags and keys are defined once
  there as the single source of truth.
- The reference solver verifies stages 1-5 and 7 programmatically; flag 6 is
  rendered in the PNG and confirmed by a valid image (not OCR'd).

## Reproduce

```
python build/build.py      # regenerate handout/cipher.txt + brief.txt
python solution/solve.py   # prints all 7 stage flags (stderr) + master (stdout)
python -m pytest tests/ -v # unit + full-chain roundtrip
```
