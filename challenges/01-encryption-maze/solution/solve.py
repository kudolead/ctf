#!/usr/bin/env python3
"""Reference solver for Encryption Maze.

STATUS: stub. Reverse the cascade from build/build.py and print the flag.

Contract (see /CONVENTIONS.md):
- Read only from ../handout/.
- Print the recovered flag as the final stdout line.
- Exit non-zero if the flag cannot be recovered.
"""
from __future__ import annotations

import sys
from pathlib import Path

HANDOUT = Path(__file__).resolve().parent.parent / "handout"


def decode_layers(blob: str) -> str:
    """Reverse the encoding cascade (Base64 -> hex -> Base32 -> ROT13 -> XOR).

    TODO: implement the exact inverse of build/build.py:encode_layers.
    """
    raise NotImplementedError("Implement the decoding cascade for Encryption Maze")


def main() -> int:
    cipher = (HANDOUT / "cipher.txt").read_text(encoding="utf-8").strip()
    flag = decode_layers(cipher)
    if not flag.startswith("flag{"):
        print("failed to recover flag", file=sys.stderr)
        return 1
    print(flag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
