#!/usr/bin/env python3
"""Build every challenge handout.

Discovers ``challenges/NN-*/build/build.py`` in sorted order and runs each in
its own subprocess so a failure in one challenge does not abort the rest.

Usage:
    python3 build_all.py            # build all
    python3 build_all.py 02 04      # build only challenges whose prefix matches
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHALLENGES = ROOT / "challenges"


def discover(filters: list[str]) -> list[Path]:
    builds = sorted(CHALLENGES.glob("*/build/build.py"))
    if not filters:
        return builds
    return [b for b in builds if any(b.parent.parent.name.startswith(f) for f in filters)]


def main() -> int:
    filters = sys.argv[1:]
    builds = discover(filters)
    if not builds:
        print("No matching challenge build scripts found.", file=sys.stderr)
        return 1

    failures = 0
    for build in builds:
        challenge = build.parent.parent.name
        print(f"\n=== building {challenge} ===")
        result = subprocess.run([sys.executable, str(build)], cwd=build.parent)
        if result.returncode != 0:
            failures += 1
            print(f"!!! {challenge} build failed (exit {result.returncode})", file=sys.stderr)

    print(f"\nDone. {len(builds) - failures}/{len(builds)} challenges built.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
