import pathlib

from onenote_exporter.db import DBManager


def test_upsert_idempotent(tmp_path: pathlib.Path):
    db_path = tmp_path / "cat.sqlite"
    db = DBManager(db_path)
    db.upsert_notebook(
        {"id": "n1", "name": "NB", "slug": "nb", "created": "", "modified": ""}
    )
    db.upsert_section({
        "id": "s1",
        "notebook_id": "n1",
        "name": "Sec",
        "slug": "sec",
        "created": "",
        "modified": "",
    })
    page = {
        "id": "p1",
        "section_id": "s1",
        "notebook_id": "n1",
        "title": "Title",
        "slug": "title",
        "created": "",
        "modified": "t1",
        "md_path": "p1.md",
        "merged_path": "",
        "jsonl_path": "",
        "content_hash": "abc",
        "word_count": 10,
        "page_order": 0,
    }
    db.upsert_page(page)
    db.upsert_page({**page, "title": "Title2"})
    state = db.get_page_state("p1")
    assert state is not None
    assert state.modified == "t1"
    assert state.content_hash == "abc"
    db.commit()
    db.close()
