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

def layout(text):
   display_list = []
   cursor_x, cursor_y = HSTEP, VSTEP
   for c in text:
      display_list.append((cursor_x, cursor_y, c))
      cursor_x += HSTEP
      if cursor_x >= WIDTH - HSTEP:
         cursor_y += VSTEP
         cursor_x = HSTEP
   return display_list

class Browser:
   def __init__(self):
      self.window = tkinter.Tk()
      self.canvas = tkinter.Canvas(
         self.window,
         width=WIDTH,
         height=HEIGHT
      )
      self.canvas.pack()
      self.scroll = 0
      self.window.bind("<Down>", self.scrolldown)

   def load(self, url):
      text = lex(url.request())
      self.display_list = layout(text)
      self.draw()

   def draw(self):
      self.canvas.delete("all")
      for x, y, c in self.display_list:
         self.canvas.create_text(x, y - self.scroll, text=c)

   def scrolldown(self, e):
      self.scroll += SCROLL_STEP
      self.draw()

      
if __name__ == "__main__":
   import sys
   Browser().load(URL(sys.argv[1]))
   tkinter.mainloop()