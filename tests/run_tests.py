#!/usr/bin/env python
"""Integration tests, run via `nix run .#tests`."""

import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
FIELD_SEP = "\x1f"


def build(md: Path) -> Path:
    r = subprocess.run(
        [sys.executable, str(ROOT / "main.py"), md.name],
        cwd=md.parent,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, f"{md.name} failed:\n{r.stdout}{r.stderr}"
    apkg = md.with_suffix(".apkg")
    assert apkg.exists(), f"{apkg.name} was not written"
    return apkg


def read_apkg(apkg: Path):
    with tempfile.TemporaryDirectory() as d:
        zipfile.ZipFile(apkg).extractall(d)
        db = sqlite3.connect(os.path.join(d, "collection.anki2"))
        notes = [flds.split(FIELD_SEP) for (flds,) in db.execute("SELECT flds FROM notes")]
        db.close()
        media = Path(d, "media").read_text()
    return notes, media


def field(notes, needle):
    for q, a in notes:
        if needle in q or needle in a:
            return q, a
    raise AssertionError(f"no note contains {needle!r}")


def test_example(work: Path):
    notes, media = read_apkg(build(work / "example" / "Example.md"))
    assert len(notes) >= 5, f"expected cards, got {len(notes)}"
    assert "0.png" in media or ".png" in media, "image missing from package media"
    q, a = field(notes, "tables")
    assert "<table>" in a, "table was not rendered"


def test_math(work: Path):
    notes, _ = read_apkg(build(work / "tests" / "math.md"))
    q, a = field(notes, "Little Question")
    assert r"\(A_z = \set{}\)" in a, f"inline math broken: {a}"
    assert r"\(B_y = 42\)" in a, f"inline math broken: {a}"
    assert "<em>markdown italics</em>" in a, "real emphasis lost"
    assert "$" not in a, f"unconverted math delimiter: {a}"


def test_dollar(work: Path):
    notes, _ = read_apkg(build(work / "tests" / "dollar.md"))
    q, a = field(notes, "prices")
    assert r"\(a_b\)" in q, f"math in heading broken: {q}"
    assert "<em>" not in q, f"underscore leaked as emphasis: {q}"
    assert "$5 prices" in q, f"price converted to math: {q}"
    assert "$5 and $10" in a, f"prices converted to math: {a}"
    assert "$20,000 and $30,000" in a, f"prices converted to math: {a}"
    assert r"\(x_y\)" in a and r"\(E = mc^2\)" in a, f"inline math broken: {a}"
    assert r"\[F_g = m g\]" in a, f"block math broken: {a}"


def main():
    tests = [test_example, test_math, test_dollar]
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        shutil.copytree(ROOT / "example", work / "example")
        for root, dirs, files in os.walk(work):
            for p in dirs + files:
                os.chmod(Path(root, p), 0o755)
        (work / "tests").mkdir()
        for md in (ROOT / "tests").glob("*.md"):
            shutil.copy(md, work / "tests" / md.name)

        failed = 0
        for t in tests:
            try:
                t(work)
                print(f"PASS {t.__name__}")
            except AssertionError as e:
                print(f"FAIL {t.__name__}: {e}")
                failed += 1
    print(f"{len(tests) - failed}/{len(tests)} tests passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
