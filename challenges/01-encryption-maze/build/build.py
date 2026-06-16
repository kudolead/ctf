#!/usr/bin/env python3
"""Build the Encryption Maze handout.

Implements the layered-encoding cascade from ../README.md and writes the
artifacts into ../handout/.

Cascade (innermost transform applied first; outermost is what the participant
first sees). Build order:

    plaintext FLAG
      -> XOR with a short repeating key            (innermost)
      -> Base58 encode (Bitcoin alphabet)
      -> ROT13
      -> reverse the string                        (red-herring / discipline)
      -> Hex encode
      -> Base64 encode                             (outermost)

solution/solve.py reverses this exactly.

Contract (see /CONVENTIONS.md):
- FLAG is the single source of truth.
- Write only into the sibling handout/ directory.
- Deterministic output (no randomness).
"""
from __future__ import annotations

import base64
import codecs
from pathlib import Path

FLAG = "flag{p33l_th3_3ncrypt10n_m4z3}"

# Short repeating XOR key. Participants recover this from the `flag{` crib once
# they have peeled back to the XOR layer.
XOR_KEY = b"maze"

HANDOUT = Path(__file__).resolve().parent.parent / "handout"

# Bitcoin / IPFS Base58 alphabet — the default CyberChef "From/To Base58" uses.
_B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def _xor(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def _b58encode(data: bytes) -> str:
    """Base58 encode (Bitcoin alphabet), preserving leading-zero bytes as '1'."""
    n = int.from_bytes(data, "big")
    out = ""
    while n > 0:
        n, rem = divmod(n, 58)
        out = _B58_ALPHABET[rem] + out
    # Leading zero bytes -> leading '1' characters.
    pad = len(data) - len(data.lstrip(b"\x00"))
    return "1" * pad + out


def encode_layers(plaintext: str) -> str:
    """Apply the outer->inner encoding cascade and return the final blob."""
    # Layer 6 (innermost): XOR the raw plaintext bytes with the repeating key.
    step = _xor(plaintext.encode("utf-8"), XOR_KEY)

    # Layer 5: Base58 encode -> printable ASCII text.
    step_s = _b58encode(step)

    # Layer 4: ROT13 (only rotates A-Z/a-z; Base58 digits pass through).
    step_s = codecs.encode(step_s, "rot_13")

    # Layer 3: reverse the string (red herring — looks like data, isn't a codec).
    step_s = step_s[::-1]

    # Layer 2: Hex encode.
    step_s = step_s.encode("utf-8").hex()

    # Layer 1 (outermost): Base64 encode.
    blob = base64.b64encode(step_s.encode("utf-8")).decode("ascii")
    return blob


def main() -> None:
    HANDOUT.mkdir(exist_ok=True)
    blob = encode_layers(FLAG)
    (HANDOUT / "cipher.txt").write_text(blob + "\n", encoding="utf-8")
    (HANDOUT / "brief.txt").write_text(
        "Something is hidden in here. Peel it back.\n", encoding="utf-8"
    )
    print(f"wrote cipher.txt ({len(blob)} bytes) and brief.txt to {HANDOUT}")


if __name__ == "__main__":
    main()
