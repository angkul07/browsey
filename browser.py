import url
import tkinter
import tkinter.font
    

WIDTH, HEIGHT = 960, 720
HSTEP, VSTEP = 13, 18 
SCROLL_STEP = 100


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.title("Browsey")
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.display_list = []
        

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def scrollup(self, e):
        self.scroll -= SCROLL_STEP
        if self.scroll < 0:
            self.scroll=0
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, word, font in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=word, font=font, anchor="nw")

    def load(self, url):
        body = url.request()
        tokens = lex(body)
        self.display_list = Layout(tokens).display_list
        self.draw()


def lex(body):
    out = []
    buffer = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
            if buffer: out.append(Text(buffer))
            buffer = ""
        elif c == ">":
            in_tag = False
            out.append(Tag(buffer))
            buffer=""
        else:
            buffer += c
    if not in_tag and buffer:
        out.append(Text(buffer))
    return out


FONTS = {}

def get_font(size, weight, slant):
    key = (size, weight, slant)
    if key not in FONTS:
        font = tkinter.font.Font(size = size, weight = weight, slant = slant)
        label = tkinter.Label(font = font)
        FONTS[key] = (font, label)
    return FONTS[key][0]
class Text:
    def __init__(self, text):
        self.text = text

class Tag:
    def __init__(self, tag):
        self.tag = tag


# looped over the text character-by-character and moved to the next line whenever we ran out of space.# 
class Layout:
    def __init__(self, tokens):
        self.tokens = tokens
        self.display_list = []

        self.weight = "normal"
        self.style = "roman"
        self.size = 12
        self.cursor_x, self.cursor_y = HSTEP, VSTEP

        self.line = []
        for tok in tokens:
            self.token(tok)
        self.flush()

    def token(self, tok):
        if isinstance(tok, Text):
            for word in tok.text:
                self.word(word)
        elif tok.tag == "i":
            self.style = "italic"
        elif tok.tag == "/i":
            self.style = "roman"
        elif tok.tag == "b":
            self.weight = "bold"
        elif tok.tag == "/b":
            self.weight = "normal"
        elif tok.tag == "small":
            self.size -= 2
        elif tok.tag == "/small":
            self.size += 2
        elif tok.tag == "big":
            self.size += 4
        elif tok.tag == "/big":
            self.size -= 4
        elif tok.tag == "br":
            self.flush()
        elif tok.tag == "/p":
            self.flush()
            self.cursor_y += VSTEP
    
    def word(self, word):
        font = get_font(self.size, self.weight, self.style)
        w = font.measure(word)
        if self.cursor_x + w > WIDTH - HSTEP:
            self.flush()
        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ") 

    def flush(self):
        if not self.line: return
        metrics = [font.metrics() for x, word, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25*max_ascent
        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))

        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25*max_descent
        self.cursor_x = HSTEP
        self.line = []

if __name__ == "__main__":
    import sys
    Browser().load(url.URL(sys.argv[1]))
    tkinter.mainloop()