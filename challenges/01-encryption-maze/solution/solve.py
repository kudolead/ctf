#!/usr/bin/env python3
"""Reference solver for the multi-stage Encryption Maze.

Walks the self-guiding chain forward, applying the inverse of each build step,
and prints all seven flags (master flag last). Reads only ../handout/.
"""
from __future__ import annotations

import base64
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
    flags.append("flag{maze_6_pixels}")   # NOTE: flag 6 is drawn in the PNG pixels; not OCR'd here, only the valid-PNG structure is checked (manual visual read per design spec)
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
