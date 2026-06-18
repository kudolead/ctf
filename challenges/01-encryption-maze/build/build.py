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

# Unguided maze: each stage reveals only its flag and the next ciphertext.
# No in-band "use op X" instructions -- the player must recognise every layer
# cold. The per-stage solution lives only in solution/ANSWER.md (author key).
MASTER_BLOCK = (
    f"{FLAG_7}\n"
    ":: You escaped the Encryption Maze! ::"
)
BRIEF = (
    "Something is hidden in here. Peel it back.\n"
    "Seven flags are buried in the layers -- recognise each one yourself.\n"
    "Stuck? hints.txt has base64-encoded nudges; decode only the one you need.\n"
)

# Spoiler-protected hint ladder. Each hint is base64-encoded on its own line in
# handout/hints.txt so a player can decode just the one they need. The first
# ("Start") hint reveals how many layers the chain has.
HINTS = [
    ("Start", [
        "This is a 7-stage chain: you peel 7 encodings/ciphers in sequence, and "
        "each stage drops one flag (7 total). Work outside-in -- decode one "
        "layer, read its flag, feed the leftover blob into the next stage.",
    ]),
    ("Stage 1", [
        "Trailing '=' padding and an A-Za-z0-9+/ alphabet point to one very "
        "common encoding.",
        "It's Base64. Use 'From Base64' (the Magic op also catches it).",
    ]),
    ("Stage 2", [
        "This blob is dense with punctuation (! # $ % & * ...), not just letters "
        "and digits -- so it is not Base64.",
        "A printable alphabet running roughly from '!' to 'u' is ASCII85 / Base85.",
        "Use 'From Base85' with the standard alphabet (!-u).",
    ]),
    ("Stage 3", [
        "Mostly letters, shifted around -- a classic cipher. But the shift is not "
        "constant, so it is not Caesar/ROT.",
        "It's Vigenere (a repeating keyword). Use 'Vigenere Decode'.",
        "The key is a word you already earned: the keyword inside your previous "
        "(stage-2) flag -- 'alphabet'.",
    ]),
    ("Stage 4", [
        "Two layers here. The outer is Base64 again -- 'From Base64' gives raw, "
        "non-printable bytes.",
        "Those bytes are XOR'd with a short repeating key, which you are NOT given.",
        "You know the text starts with 'flag{maze_4_' (12 chars). XOR that crib "
        "against the first bytes to recover the key ('vigenere'), then XOR the "
        "whole blob with it (key type UTF8).",
    ]),
    ("Stage 5", [
        "The next blob is only 0-9 and a-f -- that is hexadecimal. 'From Hex' first.",
        "Inspect the first decoded bytes: 1f 8b 08. That is a file magic number.",
        "1f 8b = gzip. Finish with 'Gunzip' (or 'Raw Inflate').",
    ]),
    ("Stage 6", [
        "Base64 again -- decode it, then check the file signature (it starts with "
        "the PNG magic bytes).",
        "'From Base64' then 'Render Image' shows the flag drawn in the picture.",
        "A PNG ends at its IEND chunk; data is appended AFTER it. Carve the bytes "
        "past IEND (skip IEND plus its 4-byte CRC) -- that is the final boss input.",
    ]),
    ("Stage 7", [
        "The carved text is 'salt:<word>' then 'payload:<hex>|<hex>|<hex>'. This "
        "needs CyberChef flow-control ops, not a plain decode.",
        "Register the salt into $R0 (regex salt:(\\w+)). Subsection just the "
        "payload (regex payload:([0-9a-f|]+)). Fork on '|'. Then 'From Hex'.",
        "XOR each chunk, key 'pixels$R0' UTF8 (stage keyword 'pixels' + the "
        "registered salt). Merge to close the Fork, Merge again to close the "
        "Subsection -- the master flag appears in the output.",
    ]),
]


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
    return f"salt:{BOSS_SALT}\npayload:" + "|".join(parts)


def render_hints() -> str:
    """Render handout/hints.txt: a heading plus, per step, each hint base64-
    encoded on its own line so a player can decode only the nudge they need."""
    lines = [
        "Hints: encoded using base64 to avoid spoiling",
        "",
        "Decode the base64 line(s) under a step (From Base64) only when you are "
        "stuck on that step. Hints go from gentle to specific.",
        "",
    ]
    for label, hints in HINTS:
        lines.append(f"[{label}]")
        for hint in hints:
            lines.append(base64.b64encode(hint.encode("utf-8")).decode("ascii"))
        lines.append("")
    return "\n".join(lines)


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

    revealed_5 = reveal(FLAG_5, "", ct6)
    ct5 = gzip.compress(revealed_5.encode("utf-8"), mtime=0).hex()

    revealed_4 = reveal(FLAG_4, "", ct5)
    ct4 = base64.b64encode(xor(revealed_4.encode("utf-8"), XOR_KEY)).decode("ascii")

    revealed_3 = reveal(FLAG_3, "", ct4)
    ct3 = vigenere(revealed_3, VIGENERE_KEY)

    revealed_2 = reveal(FLAG_2, "", ct3)
    ct2 = b85encode(revealed_2.encode("utf-8"))

    revealed_1 = reveal(FLAG_1, "", ct2)
    cipher = base64.b64encode(revealed_1.encode("utf-8")).decode("ascii")

    (HANDOUT / "cipher.txt").write_text(cipher + "\n", encoding="utf-8")
    (HANDOUT / "brief.txt").write_text(BRIEF, encoding="utf-8")
    (HANDOUT / "hints.txt").write_text(render_hints(), encoding="utf-8")
    print(f"wrote cipher.txt ({len(cipher)} bytes), brief.txt, and hints.txt to {HANDOUT}")


if __name__ == "__main__":
    main()
