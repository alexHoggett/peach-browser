import pytest
from browser import URL

def test_valid_url():
   url = URL("http://example.com/path/somewhere")
   assert url.scheme == "http"
   assert url.host == "example.com"
   assert url.path == "/path/somewhere"

def test_valid_url_with_no_path():
    url = URL("http://example.com")
    assert url.scheme == "http"
    assert url.host == "example.com"
    assert url.path == "/"

def test_valid_url_with_https():
    url = URL("https://example.com")
    assert url.scheme == "https"
    assert url.host == "example.com"
    assert url.path == "/"

def test_missing_scheme():
    with pytest.raises(ValueError):  # Will raise an error if no scheme is provided
        URL("example.com/path")