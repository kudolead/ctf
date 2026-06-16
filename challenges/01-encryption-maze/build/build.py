#!/usr/bin/env python3
"""Build the Encryption Maze handout.

STATUS: stub. Implement the layered-encoding cascade described in
../README.md, then write the artifacts into ../handout/.

Contract (see /CONVENTIONS.md):
- FLAG is the single source of truth.
- Write only into the sibling handout/ directory.
- Deterministic output (no randomness, or seed it).
"""
from __future__ import annotations

from pathlib import Path

FLAG = "flag{REPLACE_ME_encryption_maze}"

HANDOUT = Path(__file__).resolve().parent.parent / "handout"


def encode_layers(plaintext: str) -> str:
    """Apply the outer->inner encoding cascade and return the final blob.

    TODO: implement the chain from README (XOR -> ROT13 -> Base32 -> hex ->
    Base64) so that solution/solve.py reverses it exactly.
    """
    raise NotImplementedError("Implement the encoding cascade for Encryption Maze")


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
