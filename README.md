# CTF — Training Range

A small capture-the-flag set for graduating analysts. Four challenges spanning
forensics, blue-team log analysis, and reverse engineering. Each challenge is
self-contained under `challenges/` and produces participant-facing files from a
build script.

> **Status:** skeleton. Folder structure, author specs, and the build/solve
> script contracts are in place. The artifact generators and solvers are stubs
> (`raise NotImplementedError`) — fill them in per each challenge README.

## Challenges

| # | Name | Category | Skill exercised |
|---|------|----------|-----------------|
| 01 | [Encryption Maze](challenges/01-encryption-maze/README.md) | Forensics | CyberChef, identifying layered encodings/ciphers |
| 02 | [DNS Logs](challenges/02-dns-logs/README.md) | Blue team | DNS query analysis, spotting data exfiltration in a pcap |
| 03 | [SIEM Password Hunt](challenges/03-siem-password-hunt/README.md) | Blue team / IR | Tracking an attacker through SIEM logs to assemble a zip password |

> A fourth challenge (reverse-engineering a sample to write a decryptor) is
> planned but not yet in this repo.

## Layout

```
ctf/
├── README.md            # this file
├── CONVENTIONS.md       # flag format + build/solve contracts
├── requirements.txt     # shared Python dependencies
├── build_all.py         # builds every challenge's handout
└── challenges/
    └── NN-name/
        ├── README.md    # author spec (intended mechanics, flag, hints)
        ├── build/build.py    # generates participant files into ../handout/
        ├── handout/          # generated participant files (gitignored)
        └── solution/
            ├── solve.py  # reads handout/, prints the recovered flag
            └── ANSWER.md # flag + walkthrough
```

## Target environment

Challenges are authored for participants working on **Linux / Kali** with
standard tooling (Wireshark/tshark, John the Ripper, binwalk, CyberChef,
`python3`). Build and solve tooling is **Python 3**.

## Getting started (authors)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 build_all.py            # builds all handouts (once generators are implemented)
```

See [CONVENTIONS.md](CONVENTIONS.md) for the rules every challenge follows.
