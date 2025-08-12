"""Export notebook to Markdown/DOCX and JSONL."""
from __future__ import annotations

import json
import datetime as _dt
from typing import Any
import pathlib
import re
import uuid

from bs4 import BeautifulSoup
from markdownify import markdownify as md
from tqdm import tqdm

from .graph import (
    get_page_content_html,
    list_pages_in_section,
    list_sections_in_notebook,
)
from .utils import filename_from_url, slugify
try:  # optional at runtime
    from .db import DBManager  # type: ignore
except (ImportError, OSError):  # pragma: no cover
    DBManager = None  # type: ignore


def write_front_matter(info: dict) -> str:
    lines = ["---"]
    for k, v in info.items():
        if isinstance(v, str):
            v = v.replace("\n", " ").strip()
        lines.append(f"{k}: {v}")
    lines.append("---\n")
    return "\n".join(lines)


def onenote_html_to_markdown(
    token: str, html: str, assets_dir: pathlib.Path
) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(["img", "object"]):
        url_attr = None
        for attr in ["data-fullres-src", "data-src", "src", "data"]:
            if tag.has_attr(attr):
                url_attr = attr
                break
        if not url_attr:
            continue

        res_url = tag.get(url_attr)
        if not res_url or not res_url.startswith("http"):
            continue

        fallback_name = f"res-{uuid.uuid4().hex}"
        local_name = filename_from_url(res_url, fallback_name)
        local_path = assets_dir / local_name

        try:
            from .graph import graph_get

            assets_dir.mkdir(parents=True, exist_ok=True)
            r = graph_get(token, res_url, stream=True)
            cd = r.headers.get("Content-Disposition", "")
            if "filename=" in cd:
                fn = cd.split("filename=")[-1].strip('"; ')
                if fn:
                    local_path = local_path.with_name(fn)
            with open(local_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            rel_path = local_path.relative_to(assets_dir.parent).as_posix()
            if tag.name == "img":
                tag["src"] = rel_path
                for a in [
                    "data-fullres-src",
                    "data-src",
                ]:
                    if a in tag.attrs:
                        del tag.attrs[a]
            elif tag.name == "object":
                tag["data"] = rel_path
        except (OSError, ValueError):
            # Leave absolute URL if download fails
            pass

    for meta in soup.find_all("meta"):
        meta.decompose()

    body_html = str(soup)

    markdown = md(
        body_html,
        heading_style="ATX",
        bullets="*",
        strip=["span", "div"],
    )

    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip() + "\n"
    return markdown


def export_notebook(
    token: str,
    notebook_id: str,
    notebook_name: str,
    out_root: pathlib.Path,
    merge: bool,
    out_formats: set[str],
    build_db: bool = False,
    db_path: pathlib.Path | None = None,
    since: str | None = None,
    index_only: bool = False,
):
    per_page_dir = out_root / "pages"
    per_page_dir.mkdir(parents=True, exist_ok=True)
    assets_root = out_root / "assets"
    assets_root.mkdir(parents=True, exist_ok=True)

    all_pages_records: list[dict] = []
    compiled_md_parts: list[str] = []

    sections = []
    if not index_only:
        sections = list_sections_in_notebook(token, notebook_id)

    # Parse since timestamp if provided
    since_ts: _dt.datetime | None = None
    if since:
        try:
            since_ts = _dt.datetime.fromisoformat(
                since.replace("Z", "+00:00")
            )
        except ValueError:
            print(
                "[WARN] Could not parse --since value '"
                + since
                + "' (expected ISO8601). Ignoring."
            )

    db: Any = None
    if build_db and DBManager is not None:
        default_catalog = (out_root / ".." / "catalog.sqlite").resolve()
        catalog_path = db_path or default_catalog
        db = DBManager(catalog_path)
        # Upsert notebook metadata
        db.upsert_notebook(
            {
                "id": notebook_id,
                "name": notebook_name,
                "slug": slugify(notebook_name),
                "created": "",
                "modified": "",
            }
        )

    # For per-section JSONL aggregation
    section_page_records: dict[str, list[dict]] = {}

    created_count = 0
    updated_count = 0
    skipped_count = 0

    for section in tqdm(sections, desc=f"Sections in {notebook_name}"):
        section_name = section.get("displayName") or "Untitled Section"
        section_id = section.get("id")
        if not section_id:
            continue
        if db:
            db.upsert_section(
                {
                    "id": section_id,
                    "notebook_id": notebook_id,
                    "name": section_name,
                    "slug": slugify(section_name),
                    "created": section.get("createdDateTime", ""),
                    "modified": section.get("lastModifiedDateTime", ""),
                }
            )

        pages = (
            list_pages_in_section(token, str(section_id))
            if not index_only
            else []
        )
        for page in tqdm(pages, desc=f"Pages in {section_name}", leave=False):
            page_id = page.get("id")
            if not page_id:
                continue
            page_id = str(page_id)
            title = page.get("title") or "Untitled Page"
            created = page.get("createdDateTime", "")
            modified = page.get("lastModifiedDateTime", "")
            web_url = (
                page.get("links", {})
                .get("oneNoteWebUrl", {})
                .get("href", "")
            )
            client_url = (
                page.get("links", {})
                .get("oneNoteClientUrl", {})
                .get("href", "")
            )

            safe_title = slugify(title)
            page_base = f"{safe_title}-{page_id[:8]}"
            md_path = per_page_dir / f"{page_base}.md"
            page_assets_dir = assets_root / page_id
            page_assets_dir.mkdir(parents=True, exist_ok=True)

            # Incremental skip check
            state = db.get_page_state(page_id) if db else None
            modified_dt: _dt.datetime | None = None
            try:
                if modified:
                    modified_dt = _dt.datetime.fromisoformat(
                        modified.replace("Z", "+00:00")
                    )
            except ValueError:
                modified_dt = None

            if (
                since_ts
                and modified_dt
                and modified_dt < since_ts
                and not state
            ):
                # Page older than window and not seen before: skip exporting
                skipped_count += 1
                continue

            skip_due_to_unchanged = False
            if state and state.modified == modified:
                # We'll still open file if missing; otherwise skip
                if state.content_hash and md_path.exists():
                    skipped_count += 1
                    continue
                skip_due_to_unchanged = True

            html = get_page_content_html(token, page_id)
            collected_assets: list[dict] = []
            md_body = onenote_html_to_markdown(token, html, page_assets_dir)

            content_hash = (
                DBManager.hash_content(md_body)
                if db and DBManager is not None
                else ""
            )

            fm = write_front_matter(
                {
                    "notebook": notebook_name,
                    "section": section_name,
                    "title": title,
                    "page_id": page_id,
                    "created": created,
                    "modified": modified,
                    "web_url": web_url,
                    "client_url": client_url,
                    "content_hash": content_hash,
                }
            )

            md_full = fm + f"# {title}\n\n" + md_body
            md_path.write_text(md_full, encoding="utf-8")

            if db and DBManager is not None:
                if (
                    state
                    and state.content_hash
                    and state.content_hash != content_hash
                ):
                    updated_count += 1
                elif not state:
                    created_count += 1
                elif skip_due_to_unchanged:
                    skipped_count += 1
                db.upsert_page(
                    {
                        "id": page_id,
                        "section_id": section_id,
                        "notebook_id": notebook_id,
                        "title": title,
                        "slug": safe_title,
                        "created": created,
                        "modified": modified,
                        "md_path": str(md_path),
                        "merged_path": "",  # filled later if merge
                        "jsonl_path": "",  # per-page JSONL not tracked yet
                        "content_hash": content_hash,
                        "word_count": len(md_body.split()),
                        "page_order": 0,
                    }
                )
                if collected_assets:
                    db.upsert_assets(page_id, collected_assets)

            rec_obj = {
                "notebook": notebook_name,
                "section": section_name,
                "title": title,
                "page_id": page_id,
                "created": created,
                "modified": modified,
                "path": str(md_path),
                "web_url": web_url,
                "client_url": client_url,
            }
            all_pages_records.append(rec_obj)
            section_page_records.setdefault(section_id, []).append(rec_obj)

            if merge:
                compiled_md_parts.append(f"\n\n# {title}\n\n")
                compiled_md_parts.append(md_body)

    (out_root / "index.json").write_text(
        json.dumps(all_pages_records, indent=2), encoding="utf-8"
    )

    # Per-section JSONL files
    for section in sections:
        section_id = section.get("id")
        if not section_id:
            continue
        recs = section_page_records.get(section_id) or []
        if not recs:
            continue
        section_slug = slugify(section.get("displayName") or section_id)
        jsonl_file = out_root / section_slug / "section.jsonl"
        jsonl_file.parent.mkdir(parents=True, exist_ok=True)
        with open(jsonl_file, "w", encoding="utf-8") as sf:
            for rec in recs:
                try:
                    content = pathlib.Path(rec["path"]).read_text(
                        encoding="utf-8"
                    )
                except OSError:
                    content = ""
                obj = {
                    "id": rec["page_id"],
                    "title": rec["title"],
                    "notebook": rec["notebook"],
                    "section": rec["section"],
                    "created": rec["created"],
                    "modified": rec["modified"],
                    "content": content,
                }
                sf.write(json.dumps(obj, ensure_ascii=False) + "\n")

    if merge:
        compiled_md = (
            f"# Notebook: {notebook_name}\n\n" + "\n".join(compiled_md_parts)
        )
        compiled_md_path = out_root / f"{slugify(notebook_name)}-compiled.md"
        compiled_md_path.write_text(compiled_md, encoding="utf-8")

        if "docx" in out_formats:
            try:
                import pypandoc  # type: ignore

                docx_path = out_root / (
                    f"{slugify(notebook_name)}-compiled.docx"
                )
                pypandoc.convert_text(
                    compiled_md,
                    "docx",
                    format="md",
                    outputfile=str(docx_path),
                )
            except (OSError, RuntimeError) as e:
                print(
                    f"[WARN] DOCX conversion failed (pandoc/pypandoc): {e}"
                )

    jsonl_path = out_root / f"{slugify(notebook_name)}-pages.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for rec in all_pages_records:
            try:
                content = pathlib.Path(rec["path"]).read_text(encoding="utf-8")
            except OSError:
                content = ""
            obj = {
                "id": rec["page_id"],
                "title": rec["title"],
                "notebook": rec["notebook"],
                "section": rec["section"],
                "created": rec["created"],
                "modified": rec["modified"],
                "content": content,
            }
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    if db:
        db.commit()
        db.close()
        print(
            "[catalog] pages created: "
            + str(created_count)
            + ", updated: "
            + str(updated_count)
            + ", skipped: "
            + str(skipped_count)
        )
    return all_pages_records
