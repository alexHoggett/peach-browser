import tkinter
from url import URL

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

def lex(body):
   text = ""
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
            text += "<" if entity == "lt;" else ">"
            in_entity = False
            entity = ""
      elif not in_tag:
         text += c
   return text

def layout(text, width):
   display_list = []
   cursor_x, cursor_y = HSTEP, VSTEP
   for c in text:
      if c == '\n':
         cursor_y += (VSTEP * 1.1)
         cursor_x = HSTEP
      else:
         display_list.append((cursor_x, cursor_y, c))
         cursor_x += HSTEP

      if cursor_x >= width - HSTEP:
         cursor_y += VSTEP
         cursor_x = HSTEP
   return display_list

class Browser:
   def __init__(self):
      self.window = tkinter.Tk()

      self.width = WIDTH
      self.height = HEIGHT

      self.canvas = tkinter.Canvas(
         self.window,
         width=self.width,
         height=self.height
      )
      self.canvas.pack(fill=tkinter.BOTH, expand=True)
      self.scroll = 0

      self.window.bind("<Down>", self.scrolldown)
      self.window.bind("<Up>", self.scrollup)
      self.window.bind("<MouseWheel>", self.scrollwheel)
      self.window.bind("<Configure>", self.resize)

   def load(self, url):
      self.text = lex(url.request())
      self.display_list = layout(self.text, self.width)
      self.draw()

   def draw(self):
      # Clear the canvas
      self.canvas.delete("all")

      # Draw text to the screen
      for x, y, c in self.display_list:
         if y > self.scroll + self.height: continue
         if y + VSTEP < self.scroll: continue
         self.canvas.create_text(x, y - self.scroll, text=c)

      # Draw the scrollbar
      self.content_height = max(y for x, y, c in self.display_list) + VSTEP
      scrollbar_position, scrollbar_height = self.calculate_scrollbar()
      self.canvas.create_rectangle(self.width - 10, scrollbar_position, self.width, scrollbar_position + scrollbar_height, fill="gray")

   def scrolldown(self, e):
      max_scroll = max(0, self.content_height - self.height)
      self.scroll = min(self.scroll + SCROLL_STEP, max_scroll)
      self.draw()

   def scrollup(self, e):
      self.scroll = max(self.scroll - SCROLL_STEP, 0)
      self.draw()

   def scrollwheel(self, e):
      if self.scroll >= 0 - 5 and self.scroll <= HEIGHT + 5:
         self.scroll -= e.delta * 5
         self.draw()

   def resize(self, e):
      self.width, self.height = e.width, e.height
      self.display_list = layout(self.text, self.width)
      self.draw()
   
   def calculate_scrollbar(self):
       # Check if all content will fit on screen
      if self.content_height <= self.height:
         scrollbar_height = self.height
         scrollbar_position = 0
      else:
         scrollbar_height = (self.height / self.content_height) * self.height
         # How much can the thumb travel
         track_range = self.height - scrollbar_height
         scrollbar_position = (self.scroll / (self.content_height - self.height)) * track_range
      
      return scrollbar_position, scrollbar_height
      
if __name__ == "__main__":
   import sys
   if len(sys.argv) == 1:
      # No arguements so provide a default file
      Browser().load(URL("https://browser.engineering/examples/xiyouji.html"))
   else:
      Browser().load(URL(sys.argv[1]))

   tkinter.mainloop()