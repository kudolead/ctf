# Design — Encryption Maze (multi-stage CyberChef curriculum)

**Date:** 2026-06-16
**Challenge:** `challenges/01-encryption-maze`
**Status:** approved design, pending implementation plan

## 1. Goal

Rebuild stage 01 from a single 6-layer blob into a **self-guiding, 7-stage
CyberChef curriculum** modelled on the reference `debugging_maze.py`: each stage
teaches the next technique in-band, drops its own flag, and unlocks the next
stage. Target completion time: **3–4 hours for a junior**. Every stage forces a
*distinct* CyberChef capability so the player cannot coast on the Magic op.

## 2. Core mechanic — the self-guiding chain

There is one starting artifact, `handout/cipher.txt`. When the player applies
the correct operation for a stage, the output is a **revealed block**: a UTF-8
text region containing exactly three parts:

1. **`flag{...}`** — that stage's flag.
2. **Flavor / instruction text** — teaches the next CyberChef technique (the
   in-band equivalent of `debugging_maze`'s printed messages). Keeps the player
   inside CyberChef; no external README needed to progress.
3. **The next stage's ciphertext** — a blob the player feeds into the next
   operation.

The player advances by extending one CyberChef recipe (or pasting each new blob
back into the Input pane). Stage 7's revealed block is the **master flag** and
the maze's "you escaped" message.

### Two chaining modes

Not every technique consumes a key, so chaining works two ways. Each stage's
instruction text states which applies:

- **Keyed handoff** (stages 3, 4, 7): the decryption key is the **descriptor
  word from the previous stage's flag**. This is the "flag = next key" force —
  you cannot skip a stage, because its flag word is mechanically required next.
- **Positional handoff** (stages 2, 5, 6): no key; the previous revealed block
  simply embeds the next ciphertext.

## 3. The seven stages

| # | CyberChef skill | Operation(s) to apply | Key source | Stage flag |
|---|---|---|---|---|
| 1 | Magic op, Base64, recipe view | `From Base64` | — | `flag{maze_1_trust_the_magic}` |
| 2 | Recognize encoding by **alphabet** (Magic under-ranks Base85) | `From Base85` (alphabet `!-u`, standard ASCII85) | — | `flag{maze_2_alphabet}` |
| 3 | Classic ciphers | `Vigenère Decode`, key = `alphabet` | word from flag 2 | `flag{maze_3_vigenere}` |
| 4 | XOR + **multi-byte key recovery via crib** | `From Base64` → `XOR` key `vigenere` (UTF-8) | word from flag 3, crib-recovered | `flag{maze_4_crib_and_brute}` |
| 5 | Spot **magic bytes**, decompress | `From Hex` → `Gunzip` (recognize `1f 8b`) | — | `flag{maze_5_inflate}` |
| 6 | Binary / file handling, file carving | `From Base64` → `Render Image` (flag in pixels); carve bytes after PNG `IEND` for stage 7 | — | `flag{maze_6_pixels}` |
| 7 | **BOSS: Registers + Subsection + Fork** | `Register` `salt:(\w+)` → `Subsection` `payload:(.*)` → `Fork` on `\|` → `From Hex` → `XOR` key `pixels$R0` → `Merge` | word from flag 6 (`pixels`) + register `$R0` | `flag{maze_7_full_recipe_unl0ck3d}` (master) |

### Per-stage detail

- **Stage 1 — Magic/Base64.** `cipher.txt` is Base64 (trailing `=` is the tell).
  Magic peels it instantly. Teaches the recipe pane and that Magic exists.
- **Stage 2 — alphabet recognition.** Revealed-1 embeds an ASCII85 blob. Magic
  ranks Base85 low and the punctuation-heavy alphabet (`!"#$%...`) is the
  giveaway. Player applies `From Base85` (standard `!-u`).
- **Stage 3 — Vigenère.** Revealed-2 embeds a Vigenère-enciphered block.
  Instruction: "the keyword from your last flag opens this." Key = `alphabet`
  (the descriptor word of flag 2). CyberChef `Vigenère Decode`.
- **Stage 4 — XOR + crib.** Revealed-3 embeds `From Base64`-then-XOR ciphertext.
  The key is *not* handed over directly: the instruction teaches the
  `XOR Brute Force` op for the single-byte idea, then explains multi-byte
  recovery — "you know every flag starts with `flag{`; XOR that crib against the
  bytes to recover the key, and the result will look familiar." The recovered
  key is `vigenere` (flag 3's word), reinforcing the chain.
- **Stage 5 — compression.** Revealed-4 embeds a hex string whose bytes start
  `1f 8b` (gzip magic). `From Hex` → `Gunzip` (or `Raw Inflate`). Teaches magic
  bytes + decompression.
- **Stage 6 — image + carving.** Revealed-5 embeds a Base64 string that decodes
  to a PNG. `From Base64` → `Render Image` shows `flag{maze_6_pixels}` drawn in
  the bitmap. The instruction notes "a PNG ends at `IEND`; anything after is
  yours" — the **stage-7 boss blob is appended after the PNG `IEND` chunk**, so
  the player carves the trailing bytes (file-carving skill).
- **Stage 7 — boss.** The carved blob is text:
  `salt:<token>\npayload:<hex>|<hex>|<hex>`. Recipe: `Register` captures the
  salt into `$R0`; `Subsection` isolates the payload after `payload:`; `Fork`
  splits on `|`; `From Hex`; `XOR` with key `pixels$R0` (literal `pixels`
  concatenated with the register — CyberChef substitutes `$R0` inside argument
  fields); `Merge`. Output is the master-flag block. Exercises registers,
  subsections, and fork/merge together.

## 4. Build architecture (`build/build.py`)

The flag list, key words, and per-stage instruction text are the single source
of truth, defined once at the top. The build composes the chain **inner → outer**
(stage 7 first, stage 1 last), so each `encode` is the exact inverse of the
player's `decode`:

```
master_block            = STAGES[7].revealed_text          # contains flag 7
boss_blob               = encode_boss(master_block, salt, key="pixels"+salt)
ct6 = b64(render_png("flag{maze_6_pixels}", hint) + boss_blob.encode())
revealed_5 = flag5 + instr5 + ct6
ct5 = gzip(revealed_5).hex()
revealed_4 = flag4 + instr4 + ct5
ct4 = b64(xor(revealed_4, key="vigenere"))
revealed_3 = flag3 + instr3 + ct4
ct3 = vigenere_encode(revealed_3, key="alphabet")
revealed_2 = flag2 + instr2 + ct3
ct2 = base85_encode(revealed_2)
revealed_1 = flag1 + instr1 + ct2
cipher.txt = b64(revealed_1)
```

Constraints (per `/CONVENTIONS.md`): writes only into sibling `handout/`,
resolves paths relative to the script file, deterministic (no RNG; the salt is a
fixed literal), prints a summary. `brief.txt` is also written: the only up-front
hint — "Something is hidden in here. Peel it back. Each layer teaches you the
next; collect all seven flags."

### Encoding helpers and why each is safe at scale

- `Base85` (stdlib `base64.a85encode`, no `<~ ~>` framing) — **linear**; used for
  the large outer wrap. (Base58 was rejected here: its big-integer encode is
  O(n²) and would make both the build and CyberChef's *From Base58* hang on the
  tens-of-KB outer payload.)
- `Vigenère`, `XOR`, `gzip`, `hex`, `Base64` — all linear.
- `render_png` uses **Pillow** (new dependency) to draw the stage-6 flag text on
  a small bitmap. Deterministic output (fixed font/size/canvas).

## 5. Solver architecture (`solution/solve.py`)

Reads only `handout/cipher.txt`. Walks the 7 stages forward, applying the inverse
of each build step, and prints all seven flags (final stdout line = the master
flag) so it doubles as the solvability check. The XOR stage includes a real
`recover_key()` that derives the key from the `flag{` crib and reduces it to its
minimal period, mirroring the intended manual path. Exits non-zero if the master
flag is not recovered.

## 6. Answer + author docs

- `solution/ANSWER.md` — all seven flags, and the exact CyberChef recipe for
  each stage including op arguments (alphabets, keys, regexes, register refs),
  plus the carving note for stage 6 and the register/subsection/fork wiring for
  stage 7.
- `README.md` — updated author spec: the 7-stage curriculum table, the two
  chaining modes, difficulty rationale, and a hint ladder with one rung per
  stage (so a stuck player can be nudged on a single stage without spoilers).

## 7. Conventions reconciliation

`/CONVENTIONS.md` currently says "exactly one flag per challenge." This challenge
introduces a documented exception. Update the flag-format section with a
**Multi-stage challenges** note: a chained challenge may define multiple stage
flags; they are listed in `solution/ANSWER.md`, the build defines them once as
the single source of truth, and the final/master flag is the canonical
submission. No change to other challenges.

## 8. Dependencies

Add to root `requirements.txt`:

```
Pillow>=10.0    # 01-encryption-maze: render the stage-6 flag into a PNG
```

All other operations use the Python standard library (`base64`, `zlib`/`gzip`,
`codecs`).

## 9. Testing / acceptance

- `python challenges/01-encryption-maze/build/build.py` writes `cipher.txt` +
  `brief.txt` deterministically (byte-identical across runs).
- `python challenges/01-encryption-maze/solution/solve.py` recovers and prints
  all seven flags, master flag last, exit 0.
- Manual spot-check: each stage is solvable in CyberChef with only the
  operations named in `ANSWER.md` (especially the stage-7 register/subsection/
  fork recipe and the stage-6 `Render Image` + IEND carve).
- `python build_all.py` runs stage 01 without error (stages 02/03 remain
  unimplemented stubs and are out of scope here).

## 10. Out of scope

- No automated CyberChef recipe execution/verification (manual spot-check only).
- No changes to challenges 02 or 03.
- No scoring/grader integration beyond listing flags in `ANSWER.md`.
