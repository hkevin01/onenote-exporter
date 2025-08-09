"""Thin Microsoft Graph helpers."""
from __future__ import annotations

import time
from collections.abc import Mapping

import requests

GRAPH_ROOT = "https://graph.microsoft.com/v1.0"


def graph_get(
    token: str,
    url: str,
    params: Mapping[str, str] | None = None,
    stream: bool = False,
):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        url,
        headers=headers,
        params=params,
        stream=stream,
        timeout=30,
    )
    if resp.status_code == 429:
        retry = int(resp.headers.get("Retry-After", "2"))
        time.sleep(retry)
        resp = requests.get(
            url,
            headers=headers,
            params=params,
            stream=stream,
            timeout=30,
        )
    resp.raise_for_status()
    return resp


def list_notebooks(token: str):
    url = f"{GRAPH_ROOT}/me/onenote/notebooks"
    notebooks: list[dict] = []
    while url:
        r = graph_get(token, url)
        data = r.json()
        notebooks.extend(data.get("value", []))
        url = data.get("@odata.nextLink")
    return notebooks


def list_sections_in_notebook(token: str, notebook_id: str):
    url = f"{GRAPH_ROOT}/me/onenote/notebooks/{notebook_id}/sections"
    sections: list[dict] = []
    while url:
        r = graph_get(token, url)
        data = r.json()
        sections.extend(data.get("value", []))
        url = data.get("@odata.nextLink")
    return sections


def list_pages_in_section(token: str, section_id: str):
    url = f"{GRAPH_ROOT}/me/onenote/sections/{section_id}/pages"
    params: dict[str, str] | None = {
        "$top": "200",
        "$orderby": "createdDateTime asc",
    }
    pages: list[dict] = []
    while url:
        r = graph_get(token, url, params=params)
        data = r.json()
        pages.extend(data.get("value", []))
        url = data.get("@odata.nextLink")
        params = None
    return pages


def get_page_content_html(token: str, page_id: str) -> str:
    url = f"{GRAPH_ROOT}/me/onenote/pages/{page_id}/content"
    r = graph_get(token, url)
    return r.text
