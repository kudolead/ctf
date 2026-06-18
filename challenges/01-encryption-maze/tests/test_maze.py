import base64
import importlib.util
from pathlib import Path

CHALLENGE = Path(__file__).resolve().parent.parent


def _load(modname, relpath):
    spec = importlib.util.spec_from_file_location(modname, CHALLENGE / relpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


build = _load("em_build", "build/build.py")


def test_xor_is_involutive():
    data = b"flag{maze_4_crib_and_brute} payload"
    assert build.xor(build.xor(data, b"vigenere"), b"vigenere") == data


def test_vigenere_roundtrip_preserves_nonletters():
    text = "flag{maze_3_vigenere}\nMixed 123 +/= XYZ"
    enc = build.vigenere(text, "alphabet")
    assert enc != text
    assert build.vigenere(enc, "alphabet", decrypt=True) == text
    # digits/punctuation untouched by the cipher
    assert "123 +/=" in enc


def test_base85_roundtrip():
    blob = b"the quick brown fox \x00\x01\x02 jumps"
    assert build.b85decode(build.b85encode(blob)) == blob


def test_render_png_is_valid_png_and_deterministic():
    a = build.render_png("flag{maze_6_pixels}")
    b = build.render_png("flag{maze_6_pixels}")
    assert a[:8] == b"\x89PNG\r\n\x1a\n"   # PNG magic
    assert b"IEND" in a
    assert a == b                          # deterministic


def test_append_and_carve_roundtrip():
    png = build.render_png("flag{maze_6_pixels}")
    trailer = b"salt:n3o\npayload:deadbeef"
    blob = png + trailer
    # carve helper lives in solve; verify the boundary math here
    idx = blob.index(b"IEND")
    assert blob[idx + 8:] == trailer


def test_encode_boss_roundtrips_and_is_cyberchef_shaped():
    master = "flag{maze_7_full_recipe_unl0ck3d}\nYou escaped the maze!"
    blob = build.encode_boss(master)
    assert "salt:n3o" in blob
    assert "payload:" in blob
    assert blob.count("|") == 2          # three hex chunks
    # manual inverse mirrors the CyberChef recipe
    import re
    salt = re.search(r"salt:(\w+)", blob).group(1)
    key = (build.BOSS_KEYWORD + salt).encode()
    payload = blob.split("payload:", 1)[1]
    recovered = b"".join(
        build.xor(bytes.fromhex(p), key) for p in payload.split("|")
    ).decode()
    assert recovered == master


def test_build_is_deterministic_and_writes_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "HANDOUT", tmp_path)
    build.main()
    cipher = (tmp_path / "cipher.txt").read_text(encoding="utf-8")
    brief = (tmp_path / "brief.txt").read_text(encoding="utf-8")
    assert cipher.strip()                 # non-empty single blob
    assert "Peel it back" in brief
    # determinism: a second build into a clean dir yields identical bytes
    out2 = tmp_path / "again"
    out2.mkdir()
    monkeypatch.setattr(build, "HANDOUT", out2)
    build.main()
    assert (out2 / "cipher.txt").read_text(encoding="utf-8") == cipher


def test_stage1_is_base64_of_a_block_with_flag1_and_marker():
    block = build.reveal(build.FLAG_1, "instr", "PAYLOAD")
    assert block.startswith(build.FLAG_1)
    assert block.count(build.MARKER) == 1
    assert block.endswith("PAYLOAD")


solve = _load("em_solve", "solution/solve.py")


def test_recover_key_from_crib():
    # 12-byte crib recovers the 8-byte repeating key 'vigenere'
    sample = b"flag{maze_4_crib_and_brute} rest of block"
    ct = base64.b64encode(build.xor(sample, b"vigenere")).decode()
    assert solve.recover_key(ct, crib=b"flag{maze_4_") == b"vigenere"


def test_full_chain_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "HANDOUT", tmp_path)
    build.main()
    cipher = (tmp_path / "cipher.txt").read_text(encoding="utf-8").strip()
    flags = solve.solve(cipher)
    assert flags == [
        "flag{maze_1_trust_the_magic}",
        "flag{maze_2_alphabet}",
        "flag{maze_3_vigenere}",
        "flag{maze_4_crib_and_brute}",
        "flag{maze_5_inflate}",
        "flag{maze_6_pixels}",
        "flag{maze_7_full_recipe_unl0ck3d}",
    ]


def test_hints_file_is_base64_encoded_and_decodable(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "HANDOUT", tmp_path)
    build.main()
    text = (tmp_path / "hints.txt").read_text(encoding="utf-8")
    assert text.startswith("Hints: encoded using base64 to avoid spoiling")
    decoded = []
    for line in text.splitlines():
        if (not line or line.startswith("[") or line.startswith("Decode")
                or line.startswith("Hints:")):
            continue
        decoded.append(base64.b64decode(line).decode("utf-8"))
    assert len(decoded) >= 8                      # start hint + >=1 per stage
    assert "7" in decoded[0] or "seven" in decoded[0].lower()


def test_stage2_base85_is_cyberchef_safe(tmp_path, monkeypatch):
    # Stage-2 ASCII85 payload must have no 'z' zero-group abbreviation and no
    # whitespace, so CyberChef 'From Base85' (alphabet !-u) decodes it cleanly.
    monkeypatch.setattr(build, "HANDOUT", tmp_path)
    build.main()
    cipher = (tmp_path / "cipher.txt").read_text(encoding="utf-8").strip()
    block = base64.b64decode(cipher).decode("utf-8")
    ct2 = block.rsplit(build.MARKER, 1)[-1]
    assert "z" not in ct2
    assert not any(c.isspace() for c in ct2)
