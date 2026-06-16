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
