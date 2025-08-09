from onenote_exporter.utils import slugify


def test_slugify_basic():
    assert slugify("Hello World!") == "hello-world"


def test_slugify_empty():
    assert slugify("") == "untitled"
