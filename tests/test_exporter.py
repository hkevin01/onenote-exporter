from typing import ClassVar

try:
    from onenote_exporter.exporter import (
        onenote_html_to_markdown,
        write_front_matter,
    )
except ImportError:  # fallback for editors that don't set PYTHONPATH
    import pathlib
    import sys

    ROOT = pathlib.Path(__file__).resolve().parents[1]
    SRC = ROOT / "src"
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    from onenote_exporter.exporter import (  # type: ignore
        onenote_html_to_markdown,
        write_front_matter,
    )


def test_front_matter_simple():
    fm = write_front_matter({"title": "Hello", "a": 1})
    assert fm.startswith("---\n")
    assert "title: Hello" in fm
    assert fm.endswith("---\n\n")


def test_html_to_markdown_download_links(monkeypatch, tmp_path):
    # Minimal HTML with image
    html = (
        '<html><body><img src="http://example.com/img.png"/>'
        "</body></html>"
    )

    class DummyResp:
        headers: ClassVar[dict[str, str]] = {
            "Content-Disposition": "filename=img.png"
        }

        def iter_content(self, _chunk_size=8192):
            yield b"data"

        def raise_for_status(self):
            return

    def fake_get(*_args, **_kwargs):
        return DummyResp()

    monkeypatch.setattr("onenote_exporter.exporter.graph_get", fake_get)

    assets_dir = tmp_path / "assets"
    md = onenote_html_to_markdown("token", html, assets_dir)
    # The image src should be rewritten to relative assets path
    assert "assets/" in md
