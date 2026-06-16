#!/usr/bin/env python3
"""Reference solver for Encryption Maze.

Reverses the cascade from build/build.py and prints the flag.

Reverse order (outermost peeled first):

    blob
      -> From Base64
      -> From Hex
      -> reverse the string
      -> ROT13
      -> From Base58
      -> XOR with the recovered key                (innermost)

Contract (see /CONVENTIONS.md):
- Read only from ../handout/.
- Print the recovered flag as the final stdout line.
- Exit non-zero if the flag cannot be recovered.
"""
from __future__ import annotations

import base64
import codecs
import sys
from pathlib import Path

HANDOUT = Path(__file__).resolve().parent.parent / "handout"

_B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_B58_INDEX = {c: i for i, c in enumerate(_B58_ALPHABET)}

# The XOR key a participant recovers from the `flag{...}` known-plaintext crib.
XOR_KEY = b"maze"


def _xor(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def _b58decode(s: str) -> bytes:
    n = 0
    for ch in s:
        n = n * 58 + _B58_INDEX[ch]
    # Reconstruct the big-endian byte string.
    body = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
    # Leading '1' chars map back to leading zero bytes.
    pad = len(s) - len(s.lstrip("1"))
    return b"\x00" * pad + body


def _minimal_period(seq: bytes) -> bytes:
    """Return the shortest prefix whose repetition reproduces seq."""
    for p in range(1, len(seq) + 1):
        if all(seq[i] == seq[i % p] for i in range(len(seq))):
            return seq[:p]
    return seq


def recover_key(blob: str, crib: bytes = b"flag{") -> bytes:
    """Demonstrate key recovery: derive the repeating XOR key from the crib.

    Peels every layer except the final XOR, then XORs the known plaintext
    prefix against the cipher bytes to reveal the keystream. The keystream
    repeats with the key's period, so we reduce it to its shortest cycle —
    exactly what a participant does after noticing the recovered bytes repeat.
    """
    step = base64.b64decode(blob)             # From Base64
    step = bytes.fromhex(step.decode("ascii"))  # From Hex
    step = step[::-1]                          # un-reverse
    step = codecs.encode(step.decode("utf-8"), "rot_13")  # ROT13
    xored = _b58decode(step)                   # From Base58 -> XOR'd bytes
    # keystream[i] = cipher[i] ^ plaintext[i] over the crib region.
    keystream = bytes(xored[i] ^ crib[i] for i in range(len(crib)))
    return _minimal_period(keystream)


def decode_layers(blob: str, key: bytes) -> str:
    """Reverse the full cascade and return the recovered plaintext."""
    step = base64.b64decode(blob)               # From Base64
    step = bytes.fromhex(step.decode("ascii"))   # From Hex
    step = step[::-1]                            # un-reverse (red herring)
    step = codecs.encode(step.decode("utf-8"), "rot_13")  # ROT13
    raw = _b58decode(step)                       # From Base58
    return _xor(raw, key).decode("utf-8")        # XOR


def main() -> int:
    cipher = (HANDOUT / "cipher.txt").read_text(encoding="utf-8").strip()

    # Recover the key from the crib (proves the intended key-recovery path),
    # then use it to peel the final layer.
    key = recover_key(cipher)
    # The repeating key is the shortest period of the recovered bytes; for the
    # 5-byte crib that already yields the full key here.
    flag = decode_layers(cipher, key)

    if not flag.startswith("flag{"):
        print("failed to recover flag", file=sys.stderr)
        return 1
    print(f"recovered XOR key: {key!r}", file=sys.stderr)
    print(flag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
