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
