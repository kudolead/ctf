# Conventions

Rules every challenge in this repo follows. Keep them consistent so the
top-level runner and graders work uniformly.

## Flag format

```
flag{lowercase_with_underscores}
```

- Lowercase, words separated by `_`. Leet is fine (`flag{dns_3xfil_d3tected}`).
- Exactly one flag per challenge.
- The canonical flag for each challenge lives in its `solution/ANSWER.md`. The
  build script should treat the flag as the single source of truth (define it
  once at the top of `build/build.py`).

## Folder layout (per challenge)

```
NN-name/
├── README.md         # author spec — see template in each challenge
├── build/
│   └── build.py      # generates participant files
├── handout/          # OUTPUT: participant-facing files (gitignored)
│   └── .gitkeep
└── solution/
    ├── solve.py      # reference solver
    └── ANSWER.md     # flag + walkthrough
```

- `NN-name` is a zero-padded order prefix plus a kebab-case name.
- Nothing in `handout/` is committed except `.gitkeep`; it is regenerated.

## Build contract

Every `build/build.py`:

- Defines the flag once (e.g. `FLAG = "flag{...}"`).
- Exposes `def main() -> None:` and runs it under `if __name__ == "__main__":`.
- Writes **only** into its sibling `handout/` directory. Resolve that path
  relative to the script file, not the current working directory, so it works
  no matter where it is invoked from.
- Is deterministic where practical (seed any RNG) so handouts are reproducible.
- Prints a short summary of what it wrote.

## Solve contract

Every `solution/solve.py`:

- Reads **only** from its sibling `../handout/` directory.
- Recovers and prints the flag to stdout (and nothing else on the final line),
  so it can double as an automated check that the handout is solvable.
- Exits non-zero if it cannot recover the flag.

## Top-level runner

- `build_all.py` discovers `challenges/NN-*/build/build.py` in sorted order and
  runs each in its own process. A future `solve_all.py` can mirror this to
  verify every handout is solvable end-to-end.

## Dependencies

Shared Python deps live in the root `requirements.txt`. If a challenge needs
something unusual, note it in that challenge's README and add it to the root
file.
