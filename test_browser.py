import pytest
from browser import URL
from unittest.mock import patch, MagicMock
from io import StringIO
import subprocess

@pytest.fixture
def mock_http_socket():
    with patch("socket.socket") as mock_socket_class:
        # Mock socket instance
        mock_socket_instance = MagicMock()
        mock_socket_class.return_value = mock_socket_instance

        # Simulated HTTP response
        fake_response = StringIO(
            "HTTP/1.0 200 OK\r\n"
            "Content-Length: 13\r\n"
            "\r\n"
            "<div>Hello, world!</div>"
        )
        mock_socket_instance.makefile.return_value = fake_response

        yield mock_socket_instance

@pytest.fixture
def mock_https_socket():
    with patch("socket.socket") as mock_socket_class, \
        patch("ssl.create_default_context") as mock_ssl_context:
    
        # Mock socket instance
        mock_socket_instance = MagicMock()
        mock_socket_class.return_value = mock_socket_instance

        # Mock SSL context and wrap_socket
        mock_ssl_instance = MagicMock()
        mock_ssl_context.return_value = mock_ssl_instance
        mock_ssl_instance.wrap_socket.return_value = mock_socket_instance  # Make sure wrap_socket returns our mock

        # Simulated HTTPS response
        fake_response = StringIO(
            "HTTP/1.0 200 OK\r\n"
            "Content-Length: 13\r\n"
            "\r\n"
            "<div>Hello, more secure world!</div>"
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

def test_basic_http_response(mock_http_socket):
    url = URL("http://example.com/path")
    body = url.request()
    
    assert body == "<div>Hello, world!</div>"
    mock_http_socket.send.assert_called()
    mock_http_socket.connect.assert_called_with(("example.com", 80))

def test_basic_https_response(mock_https_socket):
    url = URL("https://example.com/path")
    body = url.request()
    
    assert body == "<div>Hello, more secure world!</div>"
    mock_https_socket.connect.assert_called_with(("example.com", 443))
    mock_https_socket.send.assert_called()

def test_basic_custom_ports():
    # To Do
    assert True

def test_execution_with_no_args():
    result = subprocess.run(
        ["python3", "browser.py"],
        capture_output=True,
        text=True
    )

    assert result.stdout.strip() == "hello world"
    assert result.returncode == 0

def test_basic_data_scheme():
    url = URL("data:text/html,Hello world!")
    body = url.request()

    assert url.host == None
    assert url.path == None
    assert url.port == None
    assert url.scheme == "data"
    assert body == "Hello world!"

def test_basic_entities():
    result = subprocess.run(
        ["python3", "browser.py", "data:text/html,&lt;div&gt;"],
        capture_output=True,
        text=True
    )

    assert result.stdout.strip() == "<div>"
    assert result.returncode == 0

def test_basic_view_source_scheme():
    url = URL("view-source:http://example.org/")
    body = url.request()

    assert url.scheme == "view-source:http"
    assert url.host == "example.org"
    assert url.path == "/"

def test_view_source_http_request(mock_http_socket):
    url = URL("view-source:http://example.org/")
    body = url.request()
    
    assert body == "<div>Hello, world!</div>"
    mock_http_socket.send.assert_called()
    mock_http_socket.connect.assert_called_with(("example.org", 80))