from url import *
import tkinter
import tkinter.font
from htmparser import *
from layouts import *
from author_styles import *
from adding_tabs import Chrome, Tab
    
WIDTH, HEIGHT = 960, 720
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

# start of chapter 7



# end of chapter 7

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.title("00s Browser")
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT,
            bg="white",
        )
        bar = tkinter.Scrollbar(self.window)
        bar.pack(side="right", fill= "y")
        self.canvas.pack()
        self.window.bind("<Down>", self.handle_down)
        self.window.bind("<Up>", self.handle_up)
        self.window.bind("<Button-1>", self.handle_click)
        self.window.bind("<Key>", self.handle_key)
        self.window.bind("<Return>", self.handle_enter)
        self.window.bind("<BackSpace>", self.backspace)

        self.tabs = []
        self.active_tab = None
        self.chrome = Chrome(self)

    def handle_down(self, e):
        self.active_tab.scrolldown()
        self.draw()

    def handle_up(self, e):
        self.active_tab.scrollup()
        self.draw()

    def handle_click(self, e):
        if e.y < self.chrome.bottom:
            self.chrome.click(e.x, e.y)
        else:
            tab_y = e.y - self.chrome.bottom
            self.active_tab.click(e.x, tab_y)
        self.draw()

    def handle_key(self, e):
        if len(e.char) == 0: return
        if not (0x20 <= ord(e.char) < 0x7f): return
        self.chrome.keypress(e.char)
        self.draw()

    def handle_enter(self, e):
        self.chrome.enter()
        self.draw()

    def backspace(self, e):
        self.chrome.do_backspace(e.char)
        self.draw()

    def new_tab(self, url):
        new_tab = Tab(HEIGHT - self.chrome.bottom)
        new_tab.load(url)
        self.active_tab = new_tab
        self.tabs.append(new_tab)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        self.active_tab.draw(self.canvas, self.chrome.bottom)
        for cmd in self.chrome.paint():
            cmd.execute(0, self.canvas)



if __name__ == "__main__":
    import sys
    Browser().new_tab(URL(sys.argv[1]))
    tkinter.mainloop()