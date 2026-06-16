#!/usr/bin/env python3
"""Build the SIEM Password Hunt handout.

STATUS: stub. Generate a consistent multi-source log set that plants three
password fragments at three intrusion checkpoints, plus an AES-encrypted zip
containing the flag.

Contract (see /CONVENTIONS.md):
- FLAG and PASSWORD are the single source of truth.
- Write only into the sibling handout/ directory.
- Keep the timeline internally consistent (timestamps, hostnames, users).
"""
from __future__ import annotations

from pathlib import Path

FLAG = "flag{REPLACE_ME_siem_password_hunt}"

# Password fragments, one per checkpoint. Join rule lives in ANSWER.md.
PART1 = "REPLACE1"  # initial access (web/auth)
PART2 = "REPLACE2"  # execution / persistence (process log)
PART3 = "REPLACE3"  # exfiltration (proxy/dns)
PASSWORD = PART1 + PART2 + PART3

HANDOUT = Path(__file__).resolve().parent.parent / "handout"


def write_logs(logs_dir: Path) -> None:
    """Emit the synthetic SIEM logs with the three fragments planted.

    TODO: build auth.log, web access log, process-events JSONL, and a proxy log
    that together tell one coherent intrusion story, each checkpoint carrying
    its (encoded) fragment.
    """
    raise NotImplementedError("Generate the SIEM logs for SIEM Password Hunt")


def write_zip(zip_path: Path) -> None:
    """Create an AES-encrypted zip containing flag.txt, locked with PASSWORD.

    TODO:
        import pyzipper
        with pyzipper.AESZipFile(zip_path, "w",
                                 compression=pyzipper.ZIP_DEFLATED,
                                 encryption=pyzipper.WZ_AES) as zf:
            zf.setpassword(PASSWORD.encode())
            zf.writestr("flag.txt", FLAG + "\\n")
    """
    raise NotImplementedError("Build the encrypted evidence.zip for SIEM Password Hunt")


def main() -> None:
    HANDOUT.mkdir(exist_ok=True)
    write_logs(HANDOUT / "logs")
    write_zip(HANDOUT / "evidence.zip")
    (HANDOUT / "brief.txt").write_text(
        "Reconstruct the attack. The password to the evidence archive was "
        "scattered across three stages of the intrusion.\n",
        encoding="utf-8",
    )
    print(f"wrote logs/, evidence.zip, and brief.txt to {HANDOUT}")


if __name__ == "__main__":
    main()
