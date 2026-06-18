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
# handout/hints.txt so a player can decode just the one they need. The hints
# point at the clue but never name the encoding/cipher/op/key -- the solver
# makes the final leap. Use Hint N as you peel the Nth layer. The first
# ("Start") hint only reveals how many layers the chain has.
HINTS = [
    ("Start", [
        "This chain is 7 layers nested one inside another. Peeling a layer "
        "reveals that layer's flag plus the blob for the next layer -- seven "
        "flags in all, each layer a different kind of encoding or cipher.",
    ]),
    ("Encoding 1", [
        "Trailing '=' padding and an A-Za-z0-9+/ alphabet point to one very "
        "common encoding.",
        "It is the web's default way of packing binary into printable text; your "
        "tool's auto-detect ('Magic') will flag it at once.",
    ]),
    ("Encoding 2", [
        "This blob is dense with punctuation (! # $ % & * ...), not just letters "
        "and digits -- so it is not Base64.",
        "The printable characters run roughly from '!' to 'u'; that wider range "
        "is your clue -- a denser alphabet packs more bits per character.",
        "It is a more compact cousin of the previous encoding, common in "
        "PostScript/PDF. Match its alphabet and reverse it.",
    ]),
    ("Encoding 3", [
        "Now it reads as mostly letters with the rhythm of real words underneath, "
        "but every letter looks shifted.",
        "The shift is not constant across the message -- it repeats on a fixed "
        "cycle, which rules out a single fixed shift (the Caesar/ROT family).",
        "A short keyword sets that cycle, and you have already earned a word that "
        "fits, very recently. Feed that word to the matching classic-cipher "
        "decoder.",
    ]),
    ("Encoding 4", [
        "Two layers stacked. Undo the familiar outer text-encoding first; "
        "underneath is raw, non-printable bytes.",
        "Raw bytes mean a byte-level operation, not another text codec -- a "
        "simple reversible combiner driven by a short repeating key you are not "
        "given.",
        "You know exactly how every flag in this maze begins. Line that known "
        "prefix against the first bytes; combining them exposes the repeating key "
        "-- which, again, is a word you already collected.",
    ]),
    ("Encoding 5", [
        "This blob uses only 0-9 and a-f: that tells you how the bytes are "
        "written, not what they mean. Turn it into raw bytes first.",
        "Read the first raw bytes -- a short, recognisable signature sits right "
        "at the start. Many formats announce themselves that way.",
        "That signature marks compressed data. Identify it and apply the matching "
        "inflate/expansion step.",
    ]),
    ("Encoding 6", [
        "Undo the familiar outer text-encoding again, then compare the leading "
        "bytes with known file signatures.",
        "This layer is a picture -- render/preview it; the flag is drawn on the "
        "image, not written as text.",
        "The data runs longer than the picture needs: something is appended AFTER "
        "the image's end-of-file marker. Carve those trailing bytes for the next "
        "input.",
    ]),
    ("Encoding 7", [
        "The recovered text has a clearly labelled token on one line and, on "
        "another, a list of byte-chunks separated by a delimiter. This is not a "
        "single decode.",
        "Plan: capture that token aside for reuse, narrow your operations to only "
        "the chunk list, then split it on the delimiter so each chunk is handled "
        "on its own.",
        "Each chunk is the same reversible byte-combiner from earlier; build its "
        "key by joining a word from this stage's flag with the captured token. "
        "Your tool's flow-control features (capture-to-a-variable, "
        "operate-on-a-substring, split-then-rejoin) do all of it.",
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
        "Decode a hint (From Base64) only when you are stuck. Hints are grouped "
        "per encoding and go gentle -> specific within a group; none name the "
        "answer. [Start] only tells you how many layers there are.",
        "",
    ]
    for label, hints in HINTS:
        lines.append(f"[{label}]")
        for i, hint in enumerate(hints, 1):
            b64 = base64.b64encode(hint.encode("utf-8")).decode("ascii")
            lines.append(f"Hint {i}: {b64}")
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
