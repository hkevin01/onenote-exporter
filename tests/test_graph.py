import json
from types import SimpleNamespace

import pytest

from onenote_exporter.graph import (
    graph_get,
    list_notebooks,
    list_pages_in_section,
    list_sections_in_notebook,
)


class HTTPError(Exception):
    pass


class DummyResp:
    def __init__(
        self,
        status_code=200,
        json_data=None,
        text_data="",
        headers=None,
    ):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text_data
        self.headers = headers or {}

    def json(self):
        # match requests.Response API
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise HTTPError(f"HTTP {self.status_code}")

    def iter_content(self, _chunk_size=8192):
        yield b""


def test_graph_get_handles_429(monkeypatch):
    calls = {"count": 0}

    def fake_get(*_args, **_kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            return DummyResp(status_code=429, headers={"Retry-After": "0"})
        return DummyResp(status_code=200, json_data={"ok": True})

    monkeypatch.setattr("requests.get", fake_get)

    resp = graph_get("token", "http://example.com")
    assert resp.status_code == 200


def test_list_helpers_paginate(monkeypatch):
    pages = [
        {"@odata.nextLink": "page2", "value": [{"id": 1}]},
        {"@odata.nextLink": None, "value": [{"id": 2}]},
    ]

    def fake_get(*_args, **_kwargs):
        data = pages.pop(0)
        return DummyResp(json_data=data)

    monkeypatch.setattr("requests.get", fake_get)

    token = "t"
    nbs = list_notebooks(token)
    assert [v["id"] for v in nbs] == [1, 2]

    sections_pages = [
        {"@odata.nextLink": "page2", "value": [{"id": "s1"}]},
        {"@odata.nextLink": None, "value": [{"id": "s2"}]},
    ]

    def fake_get2(*_args, **_kwargs):
        data = sections_pages.pop(0)
        return DummyResp(json_data=data)

    monkeypatch.setattr("requests.get", fake_get2)
    secs = list_sections_in_notebook(token, "nb1")
    assert [v["id"] for v in secs] == ["s1", "s2"]

    section_pages = [
        {"@odata.nextLink": "page2", "value": [{"id": "p1"}]},
        {"@odata.nextLink": None, "value": [{"id": "p2"}]},
    ]

    def fake_get3(*_args, **_kwargs):
        data = section_pages.pop(0)
        return DummyResp(json_data=data)

    monkeypatch.setattr("requests.get", fake_get3)
    pages = list_pages_in_section(token, "s1")
    assert [v["id"] for v in pages] == ["p1", "p2"]
