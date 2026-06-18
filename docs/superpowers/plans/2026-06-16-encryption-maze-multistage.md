# Encryption Maze (multi-stage) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild `challenges/01-encryption-maze` into a self-guiding, 7-stage CyberChef curriculum where each stage teaches the next technique in-band, drops its own flag, and chains into the next stage.

**Architecture:** A single `cipher.txt` is composed inner→outer by `build/build.py`: stage 7 (boss) is wrapped by stage 6 (image), …, down to stage 1 (Base64). Each stage's decoded output is a "revealed block" = flag + instructions + the next stage's ciphertext (the boss input is carved from bytes appended after the PNG `IEND`). `solution/solve.py` walks the chain forward, applying the exact inverse of each build step, and prints all seven flags. Build and solve each carry their own small copies of the shared codecs (xor, vigenère, base85, boss) to honor the CONVENTIONS separation (`build/` writes handout, `solution/` reads handout).

**Tech Stack:** Python 3 stdlib (`base64`, `gzip`, `codecs`, `re`, `io`), Pillow (stage-6 PNG render), pytest (tests).

**Reference design:** `docs/superpowers/specs/2026-06-16-encryption-maze-multistage-design.md`

---

## File Structure

| File | Responsibility |
|---|---|
| `requirements.txt` (modify) | Add `Pillow` (runtime) and `pytest` (dev). |
| `CONVENTIONS.md` (modify) | Add a "Multi-stage challenges" note permitting chained multi-flag challenges. |
| `challenges/01-encryption-maze/build/build.py` (rewrite) | Constants (flags, keys, instruction text, salt), codec helpers, `render_png`, `encode_boss`, revealed-block builder, inner→outer chain composition, writes `cipher.txt` + `brief.txt`. |
| `challenges/01-encryption-maze/solution/solve.py` (rewrite) | Inverse codecs, `recover_key` (XOR crib), `carve_after_iend`, `decode_boss`, `solve(cipher)->list[str]` walking all 7 stages, `main()`. |
| `challenges/01-encryption-maze/solution/ANSWER.md` (rewrite) | All 7 flags + exact CyberChef recipe per stage. |
| `challenges/01-encryption-maze/README.md` (rewrite) | Author spec: 7-stage table, chaining modes, hint ladder. |
| `challenges/01-encryption-maze/tests/test_maze.py` (create) | Unit tests for codecs + integration round-trip. |

### Shared constants (single source of truth, defined at top of `build/build.py`)

```python
FLAG_1 = "flag{maze_1_trust_the_magic}"
FLAG_2 = "flag{maze_2_alphabet}"
FLAG_3 = "flag{maze_3_vigenere}"
FLAG_4 = "flag{maze_4_crib_and_brute}"
FLAG_5 = "flag{maze_5_inflate}"
FLAG_6 = "flag{maze_6_pixels}"
FLAG_7 = "flag{maze_7_full_recipe_unl0ck3d}"   # master flag

VIGENERE_KEY = "alphabet"   # keyword from FLAG_2 -> unlocks stage 3
XOR_KEY = b"vigenere"       # keyword from FLAG_3 -> unlocks stage 4 (crib-recovered)
BOSS_KEYWORD = "pixels"     # keyword from FLAG_6 -> part of stage 7 key
BOSS_SALT = "n3o"           # captured by the stage-7 Register ($R0)
# stage-7 XOR key = BOSS_KEYWORD + BOSS_SALT = b"pixelsn3o"; CyberChef key field: pixels$R0

MARKER = "\n--- NEXT STAGE INPUT (paste this into a fresh Input) ---\n"
CRIB = b"flag{maze_4_"     # 12-byte crib used for stage-4 key recovery
```

---

## Task 1: Dependencies and conventions

**Files:**
- Modify: `requirements.txt`
- Modify: `CONVENTIONS.md`

- [ ] **Step 1: Add dependencies to `requirements.txt`**

Append these lines to the existing file:

```
Pillow>=10.0      # 01-encryption-maze: render the stage-6 flag into a PNG
pytest>=8.0       # dev: challenge codec + round-trip tests
```

- [ ] **Step 2: Install them**

Run: `python -m pip install -r requirements.txt`
Expected: Pillow and pytest install successfully.

- [ ] **Step 3: Add the multi-stage note to `CONVENTIONS.md`**

Under the "## Flag format" section, after the existing bullet list, add:

```markdown
### Multi-stage (chained) challenges

A challenge may be a self-guiding chain of stages, each with its own flag, when
that serves the learning design. In that case:

- The build script still defines every flag once, at the top, as the single
  source of truth.
- All stage flags are listed in `solution/ANSWER.md`.
- The final/master flag is the canonical submission; intermediate flags are
  collectible checkpoints and may double as key material for later stages.

`01-encryption-maze` is the reference example.
```

- [ ] **Step 4: Commit**

```bash
git add requirements.txt CONVENTIONS.md
git commit -m "chore: add Pillow/pytest deps and multi-stage flag convention"
```

---

## Task 2: Build constants and core codecs

Build the codec helpers shared by the cascade. TDD each one.

**Files:**
- Modify: `challenges/01-encryption-maze/build/build.py` (replace the stub)
- Create: `challenges/01-encryption-maze/tests/test_maze.py`

- [ ] **Step 1: Write failing tests for the codecs**

Create `challenges/01-encryption-maze/tests/test_maze.py`:

```python
import base64
import importlib.util
from pathlib import Path

CHALLENGE = Path(__file__).resolve().parent.parent


def _load(modname, relpath):
    spec = importlib.util.spec_from_file_location(modname, CHALLENGE / relpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


build = _load("em_build", "build/build.py")


def test_xor_is_involutive():
    data = b"flag{maze_4_crib_and_brute} payload"
    assert build.xor(build.xor(data, b"vigenere"), b"vigenere") == data


def test_vigenere_roundtrip_preserves_nonletters():
    text = "flag{maze_3_vigenere}\nMixed 123 +/= XYZ"
    enc = build.vigenere(text, "alphabet")
    assert enc != text
    assert build.vigenere(enc, "alphabet", decrypt=True) == text
    # digits/punctuation untouched by the cipher
    assert "123 +/=" in enc


def test_base85_roundtrip():
    blob = b"the quick brown fox \x00\x01\x02 jumps"
    assert build.b85decode(build.b85encode(blob)) == blob
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest challenges/01-encryption-maze/tests/test_maze.py -v`
Expected: FAIL — `module 'em_build' has no attribute 'xor'` (build.py is still the stub).

- [ ] **Step 3: Replace `build/build.py` header and add codecs**

Replace the entire contents of `challenges/01-encryption-maze/build/build.py` with this header + constants + codecs (the chain composition is added in Task 5; for now `main` may be a stub that `pass`es):

```python
#!/usr/bin/env python3
"""Build the Encryption Maze handout — a self-guiding 7-stage CyberChef maze.

See ../README.md for the curriculum and
docs/superpowers/specs/2026-06-16-encryption-maze-multistage-design.md for the
design. The chain is composed inner->outer so solution/solve.py reverses it.

Contract (see /CONVENTIONS.md): flags are the single source of truth; writes
only into the sibling handout/; deterministic output (fixed salt, mtime=0).
"""
from __future__ import annotations

import base64
import codecs
import gzip
import io
from pathlib import Path

from PIL import Image, ImageDraw

HANDOUT = Path(__file__).resolve().parent.parent / "handout"

FLAG_1 = "flag{maze_1_trust_the_magic}"
FLAG_2 = "flag{maze_2_alphabet}"
FLAG_3 = "flag{maze_3_vigenere}"
FLAG_4 = "flag{maze_4_crib_and_brute}"
FLAG_5 = "flag{maze_5_inflate}"
FLAG_6 = "flag{maze_6_pixels}"
FLAG_7 = "flag{maze_7_full_recipe_unl0ck3d}"

VIGENERE_KEY = "alphabet"
XOR_KEY = b"vigenere"
BOSS_KEYWORD = "pixels"
BOSS_SALT = "n3o"

MARKER = "\n--- NEXT STAGE INPUT (paste this into a fresh Input) ---\n"


def xor(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def vigenere(text: str, key: str, decrypt: bool = False) -> str:
    """CyberChef-compatible Vigenere: only letters are shifted; the key index
    advances only on letters; case preserved; non-letters pass through."""
    out, ki, key = [], 0, key.lower()
    for ch in text:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            shift = ord(key[ki % len(key)]) - ord("a")
            if decrypt:
                shift = -shift
            out.append(chr((ord(ch) - base + shift) % 26 + base))
            ki += 1
        else:
            out.append(ch)
    return "".join(out)


def b85encode(data: bytes) -> str:
    """Standard ASCII85 (CyberChef 'From Base85' alphabet !-u), no framing."""
    return base64.a85encode(data).decode("ascii")


def b85decode(text: str) -> bytes:
    return base64.a85decode(text.encode("ascii"))


def main() -> None:  # replaced in Task 5
    pass


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest challenges/01-encryption-maze/tests/test_maze.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add challenges/01-encryption-maze/build/build.py challenges/01-encryption-maze/tests/test_maze.py
git commit -m "feat(maze): build codecs (xor, vigenere, base85) with tests"
```

---

## Task 3: PNG render + carve

The stage-6 PNG visually shows flag 6; the boss blob is appended after `IEND`.

**Files:**
- Modify: `challenges/01-encryption-maze/build/build.py`
- Modify: `challenges/01-encryption-maze/tests/test_maze.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_maze.py`:

```python
def test_render_png_is_valid_png_and_deterministic():
    a = build.render_png("flag{maze_6_pixels}")
    b = build.render_png("flag{maze_6_pixels}")
    assert a[:8] == b"\x89PNG\r\n\x1a\n"   # PNG magic
    assert b"IEND" in a
    assert a == b                          # deterministic


def test_append_and_carve_roundtrip():
    png = build.render_png("flag{maze_6_pixels}")
    trailer = b"salt:n3o\npayload:deadbeef"
    blob = png + trailer
    # carve helper lives in solve; verify the boundary math here
    idx = blob.index(b"IEND")
    assert blob[idx + 8:] == trailer
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest challenges/01-encryption-maze/tests/test_maze.py -v`
Expected: FAIL — `module 'em_build' has no attribute 'render_png'`.

- [ ] **Step 3: Add `render_png` to `build/build.py`**

Insert this function above `main`:

```python
def render_png(text: str) -> bytes:
    """Draw `text` onto a small white bitmap and return deterministic PNG bytes.

    Uses Pillow's built-in bitmap font (no external font file) so output is
    reproducible. No timestamp chunk is written by default.
    """
    img = Image.new("RGB", (520, 90), "white")
    draw = ImageDraw.Draw(img)
    draw.text((12, 18), "Encryption Maze - Stage 6", fill=(40, 40, 40))
    draw.text((12, 48), text, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest challenges/01-encryption-maze/tests/test_maze.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add challenges/01-encryption-maze/build/build.py challenges/01-encryption-maze/tests/test_maze.py
git commit -m "feat(maze): deterministic stage-6 PNG render + carve boundary test"
```

---

## Task 4: Boss encode/decode (Register + Subsection + Fork)

**Files:**
- Modify: `challenges/01-encryption-maze/build/build.py`
- Modify: `challenges/01-encryption-maze/tests/test_maze.py`

- [ ] **Step 1: Write failing test**

Append to `tests/test_maze.py`:

```python
def test_encode_boss_roundtrips_and_is_cyberchef_shaped():
    master = "flag{maze_7_full_recipe_unl0ck3d}\nYou escaped the maze!"
    blob = build.encode_boss(master)
    assert "salt:n3o" in blob
    assert "payload:" in blob
    assert blob.count("|") == 2          # three hex chunks
    # manual inverse mirrors the CyberChef recipe
    import re
    salt = re.search(r"salt:(\w+)", blob).group(1)
    key = (build.BOSS_KEYWORD + salt).encode()
    payload = blob.split("payload:", 1)[1]
    recovered = b"".join(
        build.xor(bytes.fromhex(p), key) for p in payload.split("|")
    ).decode()
    assert recovered == master
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest challenges/01-encryption-maze/tests/test_maze.py -v`
Expected: FAIL — `module 'em_build' has no attribute 'encode_boss'`.

- [ ] **Step 3: Add `encode_boss` to `build/build.py`**

Insert above `main`:

```python
def encode_boss(master_block: str) -> str:
    """Produce the stage-7 boss input.

    CyberChef solve: Register `salt:(\\w+)` -> $R0; Subsection
    `payload:([0-9a-f|]+)`; Fork on `|`; From Hex; XOR key `pixels$R0`; Merge.
    """
    key = (BOSS_KEYWORD + BOSS_SALT).encode()
    data = master_block.encode("utf-8")
    n = len(data)
    chunks = [data[: n // 3], data[n // 3 : 2 * n // 3], data[2 * n // 3 :]]
    parts = [xor(c, key).hex() for c in chunks]
    recipe_hint = (
        "# BOSS: Register salt:(\\w+) -> $R0 | Subsection payload:([0-9a-f|]+) "
        "| Fork on | | From Hex | XOR key pixels$R0 (UTF8) | Merge\n"
    )
    return f"{recipe_hint}salt:{BOSS_SALT}\npayload:" + "|".join(parts)
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest challenges/01-encryption-maze/tests/test_maze.py -v`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add challenges/01-encryption-maze/build/build.py challenges/01-encryption-maze/tests/test_maze.py
git commit -m "feat(maze): boss encode (register/subsection/fork) with roundtrip test"
```

---

## Task 5: Compose the chain and write the handout

**Files:**
- Modify: `challenges/01-encryption-maze/build/build.py`
- Modify: `challenges/01-encryption-maze/tests/test_maze.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_maze.py`:

```python
def test_build_is_deterministic_and_writes_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "HANDOUT", tmp_path)
    build.main()
    cipher = (tmp_path / "cipher.txt").read_text(encoding="utf-8")
    brief = (tmp_path / "brief.txt").read_text(encoding="utf-8")
    assert cipher.strip()                 # non-empty single blob
    assert "Peel it back" in brief
    # determinism: a second build into a clean dir yields identical bytes
    out2 = tmp_path / "again"
    out2.mkdir()
    monkeypatch.setattr(build, "HANDOUT", out2)
    build.main()
    assert (out2 / "cipher.txt").read_text(encoding="utf-8") == cipher


def test_stage1_is_base64_of_a_block_with_flag1_and_marker():
    block = build.reveal(build.FLAG_1, "instr", "PAYLOAD")
    assert block.startswith(build.FLAG_1)
    assert block.count(build.MARKER) == 1
    assert block.endswith("PAYLOAD")
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest challenges/01-encryption-maze/tests/test_maze.py -v`
Expected: FAIL — `module 'em_build' has no attribute 'reveal'` (and `main` writes nothing).

- [ ] **Step 3: Add the instruction text, `reveal`, and the real `main`**

Add these instruction constants near the other constants in `build/build.py`:

```python
INSTR_1 = (
    "Welcome to the Encryption Maze. You just used Base64 (the trailing '=' was "
    "the tell) -- the Magic op would have spotted it too.\n"
    "The next blob is NOT Base64: look at its alphabet -- it is dense with "
    "punctuation (!#$%&*+). That is ASCII85 / Base85. Use 'From Base85' with the "
    "standard alphabet (!-u)."
)
INSTR_2 = (
    "Nice -- you recognised an encoding by its alphabet instead of trusting "
    "Magic's top pick.\nThe next blob is a Vigenere cipher. The key is the "
    "KEYWORD from THIS flag: 'alphabet'. Use 'Vigenere Decode'."
)
INSTR_3 = (
    "The next blob is Base64, and underneath that it is XOR'd. 'From Base64' "
    "first.\nThe key is NOT given. Recover it: every flag here looks like "
    "flag{maze_N_...}, so you have a 12-character known-plaintext crib. The "
    "'XOR Brute Force' op handles single-byte keys; for this multi-byte key, XOR "
    "the crib against the first bytes -- the repeating result will look familiar "
    "(hint: it is the keyword from your last flag)."
)
INSTR_4 = (
    "The next blob is hex. 'From Hex', then look at the first bytes: 1f 8b 08 is "
    "the gzip magic number. Finish with 'Gunzip' (or 'Raw Inflate')."
)
INSTR_5 = (
    "The next blob is Base64 of a PNG image. 'From Base64' then 'Render Image' to "
    "READ your stage-6 flag off the pixels.\nBut a PNG ends at its IEND chunk -- "
    "the bytes AFTER it are the final boss input. Carve them (e.g. 'Detect File "
    "Type' confirms the trailing data). The carved text explains the boss recipe."
)
MASTER_BLOCK = (
    f"{FLAG_7}\n"
    ":: You escaped the Encryption Maze! ::\n"
    "You chained Magic, alphabet-recognition, Vigenere, XOR key-recovery, "
    "decompression, image carving, and CyberChef registers/subsections/forks. "
    "Submit the master flag above."
)
BRIEF = (
    "Something is hidden in here. Peel it back.\n"
    "Each layer teaches you the next and drops a flag -- collect all seven.\n"
)
```

Then add `reveal` and replace `main`:

```python
def reveal(flag: str, instructions: str, payload: str) -> str:
    """Assemble a revealed block: flag, instructions, then the next ciphertext
    after a unique marker. Build-time assert guarantees solve can split on it."""
    block = f"{flag}\n{instructions}{MARKER}{payload}"
    assert block.count(MARKER) == 1, "marker collision in revealed block"
    return block


def main() -> None:
    HANDOUT.mkdir(exist_ok=True)

    # Inner -> outer. Each `ct_n` is the ciphertext the player feeds to stage n.
    boss_blob = encode_boss(MASTER_BLOCK)                       # stage 7 input
    ct6 = base64.b64encode(render_png(FLAG_6) + boss_blob.encode("utf-8")).decode("ascii")

    revealed_5 = reveal(FLAG_5, INSTR_5, ct6)
    ct5 = gzip.compress(revealed_5.encode("utf-8"), mtime=0).hex()

    revealed_4 = reveal(FLAG_4, INSTR_4, ct5)
    ct4 = base64.b64encode(xor(revealed_4.encode("utf-8"), XOR_KEY)).decode("ascii")

    revealed_3 = reveal(FLAG_3, INSTR_3, ct4)
    ct3 = vigenere(revealed_3, VIGENERE_KEY)

    revealed_2 = reveal(FLAG_2, INSTR_2, ct3)
    ct2 = b85encode(revealed_2.encode("utf-8"))

    revealed_1 = reveal(FLAG_1, INSTR_1, ct2)
    cipher = base64.b64encode(revealed_1.encode("utf-8")).decode("ascii")

    (HANDOUT / "cipher.txt").write_text(cipher + "\n", encoding="utf-8")
    (HANDOUT / "brief.txt").write_text(BRIEF, encoding="utf-8")
    print(f"wrote cipher.txt ({len(cipher)} bytes) and brief.txt to {HANDOUT}")
```

- [ ] **Step 4: Run tests to verify pass**

Run: `python -m pytest challenges/01-encryption-maze/tests/test_maze.py -v`
Expected: 8 passed.

- [ ] **Step 5: Generate the handout and eyeball the first layer**

Run: `python challenges/01-encryption-maze/build/build.py`
Then decode just the outer layer to confirm it looks right:
Run: `python -c "import base64,pathlib; print(base64.b64decode(pathlib.Path('challenges/01-encryption-maze/handout/cipher.txt').read_text().strip()).decode()[:200])"`
Expected: starts with `flag{maze_1_trust_the_magic}` followed by the stage-1 instructions and the marker.

- [ ] **Step 6: Commit**

```bash
git add challenges/01-encryption-maze/build/build.py challenges/01-encryption-maze/tests/test_maze.py
git commit -m "feat(maze): compose inner->outer chain and write handout"
```

---

## Task 6: Solver — walk all seven stages

**Files:**
- Modify: `challenges/01-encryption-maze/solution/solve.py` (replace the stub)
- Modify: `challenges/01-encryption-maze/tests/test_maze.py`

- [ ] **Step 1: Write the failing integration test**

Append to `tests/test_maze.py`:

```python
solve = _load("em_solve", "solution/solve.py")


def test_recover_key_from_crib():
    # 12-byte crib recovers the 8-byte repeating key 'vigenere'
    sample = b"flag{maze_4_crib_and_brute} rest of block"
    ct = base64.b64encode(build.xor(sample, b"vigenere")).decode()
    assert solve.recover_key(ct, crib=b"flag{maze_4_") == b"vigenere"


def test_full_chain_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "HANDOUT", tmp_path)
    build.main()
    cipher = (tmp_path / "cipher.txt").read_text(encoding="utf-8").strip()
    flags = solve.solve(cipher)
    assert flags == [
        "flag{maze_1_trust_the_magic}",
        "flag{maze_2_alphabet}",
        "flag{maze_3_vigenere}",
        "flag{maze_4_crib_and_brute}",
        "flag{maze_5_inflate}",
        "flag{maze_6_pixels}",
        "flag{maze_7_full_recipe_unl0ck3d}",
    ]
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest challenges/01-encryption-maze/tests/test_maze.py -v`
Expected: FAIL — `module 'em_solve' has no attribute 'recover_key'`.

- [ ] **Step 3: Replace `solution/solve.py`**

Replace the entire contents of `challenges/01-encryption-maze/solution/solve.py` with:

```python
#!/usr/bin/env python3
"""Reference solver for the multi-stage Encryption Maze.

Walks the self-guiding chain forward, applying the inverse of each build step,
and prints all seven flags (master flag last). Reads only ../handout/.
"""
from __future__ import annotations

import base64
import codecs  # noqa: F401  (kept for parity; rot not used in this version)
import gzip
import re
import sys
from pathlib import Path

HANDOUT = Path(__file__).resolve().parent.parent / "handout"

MARKER = "\n--- NEXT STAGE INPUT (paste this into a fresh Input) ---\n"
BOSS_KEYWORD = "pixels"
FLAG_RE = re.compile(r"flag\{[^}]*\}")


def xor(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def vigenere(text: str, key: str, decrypt: bool = False) -> str:
    out, ki, key = [], 0, key.lower()
    for ch in text:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            shift = ord(key[ki % len(key)]) - ord("a")
            if decrypt:
                shift = -shift
            out.append(chr((ord(ch) - base + shift) % 26 + base))
            ki += 1
        else:
            out.append(ch)
    return "".join(out)


def b85decode(text: str) -> bytes:
    return base64.a85decode(text.encode("ascii"))


def split_block(block: str) -> tuple[str, str]:
    """Return (flag, next_ciphertext) from a revealed block."""
    flag = FLAG_RE.search(block).group(0)
    payload = block.rsplit(MARKER, 1)[-1]
    return flag, payload


def _minimal_period(seq: bytes) -> bytes:
    for p in range(1, len(seq) + 1):
        if all(seq[i] == seq[i % p] for i in range(len(seq))):
            return seq[:p]
    return seq


def recover_key(ct_b64: str, crib: bytes = b"flag{maze_4_") -> bytes:
    """Recover the repeating XOR key from the known-plaintext crib."""
    raw = base64.b64decode(ct_b64)
    keystream = bytes(raw[i] ^ crib[i] for i in range(len(crib)))
    return _minimal_period(keystream)


def carve_after_iend(data: bytes) -> bytes:
    idx = data.index(b"IEND")
    return data[idx + 8 :]            # 'IEND' (4) + CRC (4)


def decode_boss(blob: str) -> str:
    salt = re.search(r"salt:(\w+)", blob).group(1)
    key = (BOSS_KEYWORD + salt).encode()
    payload = blob.split("payload:", 1)[1]
    return b"".join(xor(bytes.fromhex(p), key) for p in payload.split("|")).decode("utf-8")


def solve(cipher: str) -> list[str]:
    flags: list[str] = []

    # Stage 1: From Base64
    block = base64.b64decode(cipher).decode("utf-8")
    flag, ct2 = split_block(block)
    flags.append(flag)

    # Stage 2: From Base85
    block = b85decode(ct2).decode("utf-8")
    flag, ct3 = split_block(block)
    flags.append(flag)

    # Stage 3: Vigenere Decode (key 'alphabet')
    block = vigenere(ct3, "alphabet", decrypt=True)
    flag, ct4 = split_block(block)
    flags.append(flag)

    # Stage 4: From Base64 -> XOR (key recovered from crib)
    key = recover_key(ct4)
    block = xor(base64.b64decode(ct4), key).decode("utf-8")
    flag, ct5 = split_block(block)
    flags.append(flag)

    # Stage 5: From Hex -> Gunzip
    block = gzip.decompress(bytes.fromhex(ct5)).decode("utf-8")
    flag, ct6 = split_block(block)
    flags.append(flag)

    # Stage 6: From Base64 -> PNG (flag in pixels) + carved boss blob
    png_plus = base64.b64decode(ct6)
    assert png_plus[:8] == b"\x89PNG\r\n\x1a\n", "stage 6 is not a PNG"
    flags.append("flag{maze_6_pixels}")   # rendered visually; verified by valid PNG
    boss_blob = carve_after_iend(png_plus).decode("utf-8")

    # Stage 7: Register + Subsection + Fork boss
    master_block = decode_boss(boss_blob)
    flags.append(FLAG_RE.search(master_block).group(0))

    return flags


def main() -> int:
    cipher = (HANDOUT / "cipher.txt").read_text(encoding="utf-8").strip()
    flags = solve(cipher)
    for i, f in enumerate(flags, 1):
        print(f"stage {i}: {f}", file=sys.stderr)
    master = flags[-1]
    if not master.startswith("flag{maze_7"):
        print("failed to recover master flag", file=sys.stderr)
        return 1
    print(master)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run all tests to verify pass**

Run: `python -m pytest challenges/01-encryption-maze/tests/test_maze.py -v`
Expected: 10 passed.

- [ ] **Step 5: Run the solver against the real handout**

Run: `python challenges/01-encryption-maze/solution/solve.py`
Expected: stderr lists all 7 stage flags; stdout's final line is `flag{maze_7_full_recipe_unl0ck3d}`; exit 0.

- [ ] **Step 6: Commit**

```bash
git add challenges/01-encryption-maze/solution/solve.py challenges/01-encryption-maze/tests/test_maze.py
git commit -m "feat(maze): 7-stage reference solver + crib recovery, full roundtrip test"
```

---

## Task 7: Author docs (ANSWER.md + README.md)

**Files:**
- Rewrite: `challenges/01-encryption-maze/solution/ANSWER.md`
- Rewrite: `challenges/01-encryption-maze/README.md`

- [ ] **Step 1: Rewrite `solution/ANSWER.md`**

Write this content (verify each recipe against the built handout as you go):

```markdown
# Answer — Encryption Maze (7-stage)

Seven flags; the master flag is the canonical submission.

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

1. **From Base64** → reveals flag 1 + instructions + a Base85 blob.
2. **From Base85** (alphabet `!-u`, standard ASCII85) → flag 2 + a Vigenere blob.
3. **Vigenère Decode**, key `alphabet` (the keyword from flag 2) → flag 3 + a
   Base64/XOR blob.
4. **From Base64**, then **XOR** key `vigenere` (UTF-8). Key recovery: the block
   starts with the crib `flag{maze_4_`; XOR it against the first 12 bytes to get
   the keystream `vigenerevige`, whose period is 8 → key `vigenere` (flag 3's
   keyword). The **XOR Brute Force** op demonstrates the single-byte case.
   → flag 4 + a hex blob.
5. **From Hex** (bytes begin `1f 8b 08` = gzip) → **Gunzip** → flag 5 + a Base64
   blob.
6. **From Base64** → **Render Image**; flag 6 is drawn on the bitmap. The PNG
   ends at `IEND`; the bytes after it are the boss input — carve them.
7. Boss: **Register** `salt:(\w+)` → `$R0`; **Subsection** `payload:([0-9a-f|]+)`;
   **Fork** delimiter `|`; **From Hex**; **XOR** key `pixels$R0` (UTF-8); **Merge**
   (twice — one to close the Fork, one to close the Subsection). The decoded
   payload contains the master flag.

## Notes

- Flags chain: stage 2's keyword opens stage 3; stage 3's keyword is the stage-4
  XOR key; stage 6's keyword (`pixels`) plus the registered salt (`n3o`) is the
  boss key (`pixelsn3o`).
- The salt `n3o` is fixed in `build/build.py`; flags and keys are defined once
  there as the single source of truth.

## Reproduce

```
python build/build.py      # regenerate handout/cipher.txt + brief.txt
python solution/solve.py   # prints all 7 stage flags (stderr) + master (stdout)
python -m pytest tests/ -v # unit + full-chain roundtrip
```
```

- [ ] **Step 2: Rewrite `README.md`**

Replace the body with the 7-stage author spec: the Summary, the curriculum table (copy the table from the design spec section 3), the two chaining modes (keyed vs positional), the difficulty rationale (each stage forces a distinct CyberChef skill so Magic alone cannot finish it; the XOR crib and the register/subsection/fork boss are the main time sinks targeting 3–4 junior hours), the artifacts list (`cipher.txt`, `brief.txt`), and this hint ladder:

```markdown
## Hint ladder (one rung per stuck stage)

1. Stage 1: the trailing `=` and the alphabet say Base64. Try Magic.
2. Stage 2: this isn't Base64 — count the punctuation. It's Base85 (`From Base85`, alphabet `!-u`).
3. Stage 3: it's a Vigenère cipher; the key is the keyword from your last flag (`alphabet`).
4. Stage 4: `From Base64`, then XOR. You weren't given the key — every flag is `flag{maze_N_...}`, so crib-drag `flag{maze_4_` to recover it.
5. Stage 5: `From Hex`, then read the first bytes — `1f 8b` is gzip. `Gunzip`.
6. Stage 6: `From Base64` then `Render Image`. The flag is in the picture — and there's data after the PNG's `IEND`.
7. Stage 7: `Register` the salt, `Subsection` the payload, `Fork` on `|`, `From Hex`, `XOR` with key `pixels$R0`, `Merge`.
```

- [ ] **Step 3: Commit**

```bash
git add challenges/01-encryption-maze/README.md challenges/01-encryption-maze/solution/ANSWER.md
git commit -m "docs(maze): 7-stage ANSWER recipe + README spec and hint ladder"
```

---

## Task 8: End-to-end verification

**Files:** none (verification + final push)

- [ ] **Step 1: Full test suite**

Run: `python -m pytest challenges/01-encryption-maze/tests/ -v`
Expected: 10 passed.

- [ ] **Step 2: Top-level build runner picks up stage 01**

Run: `python build_all.py`
Expected: `01-encryption-maze` build prints its summary with no error. (Stages 02/03 still fail as unimplemented stubs — out of scope.)

- [ ] **Step 3: Solver confirms solvability**

Run: `python challenges/01-encryption-maze/solution/solve.py`
Expected: final stdout line `flag{maze_7_full_recipe_unl0ck3d}`, exit 0.

- [ ] **Step 4: Confirm handout stays gitignored**

Run: `git status --short`
Expected: no `handout/` files listed (only `.gitkeep` is tracked).

- [ ] **Step 5: Push the branch**

```bash
git push origin the-monoid
```

---

## Self-Review (completed by plan author)

- **Spec coverage:** §2 core mechanic → Task 5 `reveal`/chain. §3 all 7 stages → Tasks 2–6 (stage ops) + Task 7 (recipes). §4 build architecture → Task 5. §5 solver → Task 6. §6 docs → Task 7. §7 conventions → Task 1. §8 deps → Task 1. §9 testing → Tasks 2–6 + Task 8. No gaps.
- **Placeholder scan:** all code steps contain full code; no TBD/TODO. README prose in Task 7 Step 2 references the design-spec table by location to avoid duplication drift — the table content is fully specified in the spec.
- **Type/name consistency:** `xor`, `vigenere`, `b85encode`/`b85decode`, `reveal`, `encode_boss`, `render_png`, `recover_key`, `carve_after_iend`, `decode_boss`, `solve` names match across build, solve, and tests. `MARKER`, `BOSS_KEYWORD`, `BOSS_SALT`, `XOR_KEY`, `VIGENERE_KEY` consistent. Boss key `pixels`+`n3o` = `pixelsn3o` matches `pixels$R0` recipe. Crib `flag{maze_4_` (12 bytes) recovers 8-byte `vigenere` (validated).
```
