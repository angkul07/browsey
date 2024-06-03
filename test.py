import socket
import ssl
import tkinter
import tkinter.font


class URL:
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https"]
        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    def request(self):
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
        s.connect((self.host, self.port))   #tells the socket to connect to other computer
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)
        # Request and response 
        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
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

        # read data
        content = response.read()
        s.close()
        return content
    
def lex(body):
    text = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            text += c
    return text

WIDTH, HEIGHT = 960, 720
HSTEP, VSTEP = 13, 18 
SCROLL_STEP = 100




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
        self.window.bind("<Up>", self.scrollup)
        # self.display_list = []
        

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
        for x, y, word in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=word, anchor="nw")

    def load(self, url):
        body = url.request()
        text = lex(body)
        self.display_list = layout(text)
        self.draw()

# looped over the text character-by-character and moved to the next line whenever we ran out of space.# 
def layout(text):
    font = tkinter.font.Font()
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP

    # for word in text.split():
    #     w = font.measure(word)
    #     display_list.append((cursor_x, cursor_y, word))
        # cursor_x += w + font.measure(" ")

    for word in text:
        w = font.measure(word)
        display_list.append((cursor_x, cursor_y, word))
        cursor_x += w + font.measure(" ") 
        if cursor_x + w >= WIDTH - HSTEP:
            cursor_y += font.metrics("linespace")*1.25
            cursor_x = HSTEP
    return display_list


if __name__ == "__main__":
    import sys
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()