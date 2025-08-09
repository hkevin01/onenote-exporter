"""Export notebook to Markdown/DOCX and JSONL."""
from __future__ import annotations

import json
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
):
    per_page_dir = out_root / "pages"
    per_page_dir.mkdir(parents=True, exist_ok=True)
    assets_root = out_root / "assets"
    assets_root.mkdir(parents=True, exist_ok=True)

    all_pages_records: list[dict] = []
    compiled_md_parts: list[str] = []

    sections = list_sections_in_notebook(token, notebook_id)

    for section in tqdm(sections, desc=f"Sections in {notebook_name}"):
        section_name = section.get("displayName") or "Untitled Section"
        section_id = section.get("id")
        if not section_id:
            continue

        pages = list_pages_in_section(token, str(section_id))
        for page in tqdm(pages, desc=f"Pages in {section_name}", leave=False):
            page_id = page.get("id")
            if not page_id:
                continue
            page_id = str(page_id)
            title = page.get("title") or "Untitled Page"
            created = page.get("createdDateTime", "")
            modified = page.get("lastModifiedDateTime", "")
            web_url = (
                page.get("links", {}).get("oneNoteWebUrl", {}).get("href", "")
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

            html = get_page_content_html(token, page_id)
            md_body = onenote_html_to_markdown(token, html, page_assets_dir)

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
                }
            )

            md_full = fm + f"# {title}\n\n" + md_body
            md_path.write_text(md_full, encoding="utf-8")

            all_pages_records.append(
                {
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
            )

            if merge:
                compiled_md_parts.append(f"\n\n# {title}\n\n")
                compiled_md_parts.append(md_body)

    (out_root / "index.json").write_text(
        json.dumps(all_pages_records, indent=2), encoding="utf-8"
    )

    if merge:
        compiled_md = (
            f"# Notebook: {notebook_name}\n\n" + "\n".join(compiled_md_parts)
        )
        compiled_md_path = out_root / f"{slugify(notebook_name)}-compiled.md"
        compiled_md_path.write_text(compiled_md, encoding="utf-8")

        if "docx" in out_formats:
            try:
                import pypandoc

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

    return all_pages_records
