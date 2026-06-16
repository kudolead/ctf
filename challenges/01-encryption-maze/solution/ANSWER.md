# Answer — Encryption Maze

**Flag:** `flag{REPLACE_ME_encryption_maze}`

## CyberChef recipe (outer → inner)

1. From Base64
2. From Hex
3. From Base32
4. ROT13
5. XOR — Key: `<key>` (UTF-8)

> Replace the flag and key once `build/build.py` is implemented. Keep this in
> sync with the cascade so `solve.py` reproduces it.

## Walkthrough notes

- The *Magic* op in CyberChef detects each layer; participants can lean on it.
- Mention the key-recovery step explicitly if you use a multi-byte XOR key.
