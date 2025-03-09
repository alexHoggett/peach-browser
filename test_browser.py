import pytest
from browser import URL
from unittest.mock import patch, MagicMock
from io import StringIO

@pytest.fixture
def mock_socket():
    with patch("socket.socket") as mock_socket_class:
        mock_socket_instance = MagicMock()
        mock_socket_class.return_value = mock_socket_instance

        fake_response = StringIO(
            "HTTP/1.0 200 OK\r\n"
            "Content-Length: 13\r\n"
            "\r\n"
            "Hello, world!"
        )
        mock_socket_instance.makefile.return_value = fake_response

        yield mock_socket_instance

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

def test_http_response(mock_socket):
    url = URL("http://example.com/path")
    body = url.request()
    
    assert body == "Hello, world!"
    mock_socket.send.assert_called()
    mock_socket.connect.assert_called_with(("example.com", 80))