import socket
import ssl
import os

class URL:
   def __init__(self, url):
      # Handle data scheme first
      if url.startswith("data:"):
         self.scheme, rest = url.split(":", 1)
         assert self.scheme == "data"

         # Split into metadata (before ",") and data (after ",")
         metadata, self.data = rest.split(",", 1)

         # Check for optional base64 encoding
         if ";base64" in metadata:
               self.media_type, self.is_base64 = metadata.rsplit(";base64", 1)
               self.is_base64 = True
         else:
               self.media_type = metadata
               self.is_base64 = False

         self.host = None
         self.path = None
         self.port = None
         return

      # Handle regular URL schemes (http, https, file)
      # i.e. scheme://host.org/path
      self.scheme, url = url.split("://", 1)
      assert self.scheme in ["http", "https", "file"]

      if "/" not in url:
         url = url + "/"
      self.host, url = url.split("/", 1)
      self.path = "/" + url

      # Set default ports for http/https
      if self.scheme == "http":
         self.port = 80
      elif self.scheme == "https":
         self.port = 443

      #  Defining custom ports, i.e. http://example.org:8080/index.html
      if ":" in self.host:
         self.host, port = self.host.split(":", 1)
         self.port = int(port)

   def request(self):
      if self.scheme == "file":
         with open(self.path[1:], 'r') as file:
            return file.read()
      elif self.scheme == "data":
         return self.data

      s = socket.socket(
         family=socket.AF_INET,
         type=socket.SOCK_STREAM,
         proto=socket.IPPROTO_TCP
      )

      s.connect((self.host, self.port))
      if self.scheme == "https":
         ctx = ssl.create_default_context()
         s = ctx.wrap_socket(s, server_hostname=self.host)

      headers = {
         'Host': self.host,
         'Connection': 'close',
         'User-Agent': 'shabib'
      }

      # Construct request
      request = "GET {} HTTP/1.1\r\n".format(self.path)
      request += "".join(f"{key}: {value}\r\n" for key, value in headers.items())
      request += "\r\n"

      s.send(request.encode("utf8"))

      response = s.makefile("r", encoding="utf8", newline="\r\n")
      statusline = response.readline()
      version, status, explanation = statusline.split(" ", 2)
      response_headers = {}
      while True:
         line = response.readline()
         if line == "\r\n": break
         header, value = line.split(":", 1)
         response_headers[header.casefold()] = value.strip()

      assert "transfer-encoding" not in response_headers
      assert "content-encoding" not in response_headers

      content = response.read()
      s.close()

      return content
   
def show(body):
   in_tag = False
   in_entity = False
   entity = ""
   for c in body:
      if c == "<":
         in_tag = True
      elif c == ">":
         in_tag = False
      elif c == "&":
         in_entity = True
      elif in_entity:
         entity += c
         if entity in ("lt;", "gt;"):
            print("<" if entity == "lt;" else ">", end="")
            in_entity = False
            entity = ""
      elif not in_tag:
         print(c, end="")

def load(url):
   body = url.request()
   show(body)

if __name__ == "__main__":
   import sys
   if len(sys.argv) == 1:
      # No arguements so provide a default file
      file_path = os.path.join(os.getcwd(), "test-content/sample.txt")
      load(URL(f"file:///{file_path}"))
   else:
      load(URL(sys.argv[1]))