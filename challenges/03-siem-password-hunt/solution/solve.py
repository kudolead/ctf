#!/usr/bin/env python3
"""Reference solver for SIEM Password Hunt.

STATUS: stub. Parse the logs, recover the three fragments, assemble the
password, open evidence.zip, and print the flag.

Contract (see /CONVENTIONS.md):
- Read only from ../handout/.
- Print the recovered flag as the final stdout line.
- Exit non-zero if the flag cannot be recovered.
"""
from __future__ import annotations

import sys
from pathlib import Path

HANDOUT = Path(__file__).resolve().parent.parent / "handout"


def recover_fragments(logs_dir: Path) -> tuple[str, str, str]:
    """Return (part1, part2, part3) recovered from the three checkpoints.

    TODO: parse each log source, locate + decode the planted fragment.
    """
    raise NotImplementedError("Recover the three password fragments")


def open_flag(zip_path: Path, password: str) -> str:
    """Open the AES zip with `password` and return flag.txt contents.

    TODO: pyzipper.AESZipFile(...).read("flag.txt") with setpassword.
    """
    raise NotImplementedError("Open evidence.zip and read the flag")


def main() -> int:
    p1, p2, p3 = recover_fragments(HANDOUT / "logs")
    password = p1 + p2 + p3  # keep join rule in sync with build/build.py + ANSWER.md
    flag = open_flag(HANDOUT / "evidence.zip", password).strip()
    if not flag.startswith("flag{"):
        print("failed to recover flag", file=sys.stderr)
        return 1
    print(flag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
