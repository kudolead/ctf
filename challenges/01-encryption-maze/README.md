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

A cascade where each layer's output feeds the next, with two layers chosen to
defeat blind *Magic* spamming. **As-built** recipe (innermost applied first;
outermost is what the participant first sees):

1. Start with `FLAG` plaintext.
2. XOR with a short repeating key (`maze`).  ← key recovery, the main time sink
3. Base58 encode (Bitcoin alphabet).         ← Magic ranks below Base64
4. ROT13.
5. Reverse the string.                        ← red herring: not a codec
6. Hex encode.
7. Base64 encode.                             ← this is what the participant first sees.

To **solve**, reverse the list: From Base64 → From Hex → Reverse → ROT13 →
From Base58 → XOR (key `maze`). *Magic* peels the Base64/Hex/ROT13 layers but
stalls on the Reverse and under-ranks the Base58, so the participant must reason
about layer shape. The flag and key are the single source of truth in
`build/build.py`; see `solution/ANSWER.md` for the full recipe and intermediate
values.

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

1. "It's layers. What does the very first character pattern look like?" (Base64 — note the `=` padding.)
2. "Drop it into CyberChef and try the *Magic* operation. It'll peel a couple, then go quiet."
3. "After Base64 you'll see hex. After hex it looks like a token but nothing decodes — what if the order is just flipped?" (Reverse.)
4. "That alphanumeric string has no `0`, `O`, `I`, or `l`. That's not Base64 — look at the alphabet." (ROT13 then Base58.)
5. "The innermost layer is a repeating-key XOR. You know the plaintext starts with `flag{` — use that crib to recover the key, then watch it repeat."
