import socket
import ssl
import os
import gzip

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
      assert self.scheme in ["http", "https", "file", "view-source:http"]

      if "/" not in url:
         url = url + "/"
      self.host, url = url.split("/", 1)
      self.path = "/" + url

      # Set default ports for http/https
      if self.scheme in ("view-source:http", "http"):
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

      # To-Do: Check if we already have a socket connection

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
         'Connection': 'keep-alive',
         'User-Agent': 'shabib',
         'Accept-Encoding': 'gzip'
      }

      # Construct request
      request = "GET {} HTTP/1.1\r\n".format(self.path)
      request += "".join(f"{key}: {value}\r\n" for key, value in headers.items())
      request += "\r\n"

      s.send(request.encode("utf8"))

      response = s.makefile("rb")
      statusline = response.readline().strip()
      version, status, explanation = statusline.decode("utf8").split(" ", 2)
      response_headers = {}
      while True:
         line = response.readline().strip()

         if line == b"": break

         header, value = line.decode('utf8').split(":", 1)
         response_headers[header.casefold()] = value.strip()

      # Check for a redirect
      if status.startswith("3"):
         location = response_headers.get("location")
         # Determine if the location is a full URL or relative
         redirect_url = location if "http://" in location else f"{self.scheme}://{self.host}{location}"
         redirect = URL(redirect_url)
         
         # Request the content from the redirect URL
         return redirect.request()
      
      # Check encoding methods
      is_gzip = response_headers.get("content-encoding") == "gzip"
      is_chunked = response_headers.get("transfer-encoding") == "chunked"

      content = b""

      if is_chunked:
         # Read chunks until termination
         print('chunked')
         while True:
            chunk_size = int(response.readline().strip(), 16)  # Read hex size
            if chunk_size == 0:  
                break  # End of chunks
            chunk = response.read(chunk_size)  # Read chunk data
            content += chunk
            response.readline()  # Consume trailing CRLF

      else:  # If not chunked, read by content-length
         content_length = int(response_headers.get("content-length", 0))
         if content_length:
            content = response.read(content_length)

      self.socket = s

      # Decompress if gzip-encoded
      if is_gzip:
         content = gzip.decompress(content)

      return content.decode("utf8")
   
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
   if url.scheme == "view-source:http":
      print(body)
      return
   
   show(body)

if __name__ == "__main__":
   import sys
   if len(sys.argv) == 1:
      # No arguements so provide a default file
      file_path = os.path.join(os.getcwd(), "test-content/sample.txt")
      load(URL(f"file:///{file_path}"))
   else:
      load(URL(sys.argv[1]))