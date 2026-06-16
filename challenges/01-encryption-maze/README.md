# 01 — Encryption Maze

**Category:** Forensics
**Difficulty:** Easy → Medium (scales with number of layers)
**Flag:** `flag{...}` — canonical value in [`solution/ANSWER.md`](solution/ANSWER.md)

## Summary

Participants receive a single blob of text/data that has been run through a
*chain* of encodings and light ciphers. They must peel the layers one at a time
— ideally in [CyberChef](https://gchq.github.io/CyberChef/) — until the flag
falls out. The point is **recognizing** each layer from its shape, not brute
force.

## Learning objectives

- Identify common encodings by sight: Base64, Base32, Base58, hex, URL,
  decimal/octal, Morse.
- Recognize classic ciphers: ROT13/Caesar, Atbash, XOR with a short key, vigenère.
- Drive CyberChef: stacking operations, "Magic" detection, and the recipe view.
- Understand that "encryption maze" = layered obfuscation, peeled outside-in.

## Intended mechanics

A clean cascade where each layer's output is obviously the next layer's input.
Suggested recipe (outer → inner), tune length to set difficulty:

1. Start with `FLAG` plaintext.
2. XOR with a single-byte or short repeating key.
3. ROT13 (or Caesar shift N).
4. Base32 encode.
5. Hex encode.
6. Base64 encode  ← this is what the participant first sees.

To **solve**, reverse the list: Base64 decode → from hex → Base32 decode →
ROT13 → XOR (same key). CyberChef's *Magic* op should hint each step.

### Difficulty knobs

- Number of layers (3 = easy, 6+ = medium).
- Swap a recognizable layer (Base64) for a less common one (Base58, Base85).
- Use a multi-byte XOR key so participants must recover the key.
- Add a red-herring layer that looks like encoding but is identity (e.g. a
  reversible transpose) to test discipline.

## Artifacts to generate (`build/build.py` → `handout/`)

- `cipher.txt` — the final encoded blob (single line).
- `brief.txt` — flavor + the only hint they get up front: "Something is hidden
  in here. Peel it back." (Keep tool hints out of the handout; those live in the
  hint ladder below.)

## Solution outline

See [`solution/solve.py`](solution/solve.py) for the programmatic reverse, and
[`solution/ANSWER.md`](solution/ANSWER.md) for the CyberChef recipe and flag.

## Hint ladder

1. "It's layers. What does the very first character pattern look like?"
2. "Drop it into CyberChef and try the *Magic* operation."
3. "After Base64 you'll see hex. Keep going — Base32 is next."
4. "The innermost layer is an XOR. The key is short."
