from url import *
import tkinter
import tkinter.font
from htmparser import *
import layouts
from author_styles import *
import urllib.parse

WIDTH, HEIGHT = 960, 720
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

# To fix circular import:Creating get_font and FONTS for this file
FONTS = {}

def get_font(size, weight, slant):
    key = (size, weight, slant)
    if key not in FONTS:
        font = tkinter.font.Font(size = size, weight = weight, slant = slant)
        label = tkinter.Label(font = font)
        FONTS[key] = (font, label)
    return FONTS[key][0]

class Chrome:
    def __init__(self, browser):
        self.browser = browser
        # enter url in address bar
        self.focus = None
        self.address_bar = ""

        self.font = get_font(18, "normal", "roman")
        self.font_height = self.font.metrics("linespace")

        # detemine where the tab bar starts and ends
        self.padding = 5
        self.tabbar_top = 0
        self.tabbar_bottom = self.font_height + 2*self.padding

        # adding padding around the new-tab button
        plus_width = self.font.measure("+") + 2*self.padding
        self.newtab_rect = Rect(
            self.padding, self.padding,
            self.padding + plus_width,
            self.padding + self.font_height
        )
        # self.bottom = self.tabbar_bottom

        self.urlbar_top = self.tabbar_bottom
        self.urlbar_bottom = self.urlbar_top + \
            self.font_height + 2 * self.padding

        # navigation history: address bar that shows the current URL
        back_width = self.font.measure("<") + 2*self.padding
        self.back_rect = Rect(
            self.padding,
            self.urlbar_top + self.padding,
            self.padding + back_width,
            self.urlbar_bottom - self.padding
        )

        self.address_rect = Rect(
            self.back_rect.top + self.padding,
            self.urlbar_top + self.padding,
            WIDTH - self.padding,
            self.urlbar_bottom - self.padding
        )
        
        self.bottom = self.urlbar_bottom

    def tab_rect(self, i):
        tabs_start = self.newtab_rect.right + self.padding
        tab_width = self.font.measure("Tab X") + 2*self.padding
        return Rect(
            tabs_start + tab_width * i, self.tabbar_top,
            tabs_start + tab_width * (i+1), self.tabbar_bottom
        )
    
    def paint(self):
        cmds = []
        # make sure that the browser chrome is always drawn on top of the page contents
        cmds.append(layouts.DrawRect(
            Rect(0, 0, WIDTH, self.bottom), "white"
        ))
        cmds.append(DrawLine(
            0, self.bottom, WIDTH, self.bottom, "black", 1
        ))

        cmds.append(DrawOutline(self.newtab_rect, "black", 1))
        cmds.append(layouts.DrawText(
            self.newtab_rect.left + self.padding,
            self.newtab_rect.top,
            "+", self.font, "black"
        ))

        for i, tab in enumerate(self.browser.tabs):
            bounds = self.tab_rect(i)
            cmds.append(DrawLine(
                bounds.right, 0, bounds.right, bounds.bottom,
                "black", 1))
            cmds.append(DrawLine(
                bounds.left, 0, bounds.left, bounds.bottom,
                "black", 1))
            cmds.append(layouts.DrawText(
                bounds.left + self.padding, bounds.top + self.padding,
                "Tab {}".format(i), self.font, "black"))
            
            if tab == self.browser.active_tab:
                cmds.append(DrawLine(
                    0, bounds.bottom, bounds.left, bounds.bottom, "black", 1
                ))
                cmds.append(DrawLine(
                    bounds.right, bounds.bottom, WIDTH, bounds.bottom, "black", 1
                ))

        # painting lhe back button
        cmds.append(DrawOutline(self.back_rect, "black", 1))
        cmds.append(layouts.DrawText(
            self.back_rect.left + self.padding,
            self.back_rect.top,
            "<", self.font, "black"
        ))

        # address bar getting the current tab's URL from the browser
        cmds.append(DrawOutline(self.address_rect, "black", 1))
        if self.focus == "address bar":
            cmds.append(layouts.DrawText(
                self.address_rect.left + self.padding,
                self.address_rect.top,
                self.address_bar, self.font, "black"))
            
            # adding a cursor in the address bar
            w = self.font.measure(self.address_bar)
            cmds.append(DrawLine(self.address_rect.left + self.padding + w,
                                self.address_rect.top,
                                self.address_rect.left + self.padding + w,
                                self.address_rect.bottom,
                                "red", 1))
        else:
            url = str(self.browser.active_tab.url)
            cmds.append(layouts.DrawText(
                self.address_rect.left + self.padding,
                self.address_rect.top,
                url, self.font, "black"
            ))

        return cmds
    
    def click(self, x, y):
        self.focus = None
        if self.newtab_rect.containsPoint(x, y):
            self.browser.new_tab(URL("https://google.com"))
        elif self.back_rect.containsPoint(x, y):
            self.browser.active_tab.go_back()
        elif self.address_rect.containsPoint(x, y):
            self.focus = "address bar"
            self.address_bar = ""
        else:
            for i, tab in enumerate(self.browser.tabs):
                if self.tab_rect(i).containsPoint(x, y):
                    self.browser.active_tab = tab
                    break

    def keypress(self, char):
        if self.focus == "address bar":
            self.address_bar += char
            return True
        return False
    
    def blur(self):
        self.focus = None

    def do_backspace(self, char):
        if self.focus == "address bar":
            self.address_bar = self.address_bar[0:(len(self.address_bar)-1)]

    def enter(self):
        if self.focus == "address bar":
            self.browser.active_tab.load(URL(self.address_bar))
            self.focus = None

# DrawOutline class draws a rectangular border
class DrawOutline:
    def __init__(self, rect, color, thickness):
        self.rect = rect
        self.color = color
        self.thickness = thickness

    def execute(self, scroll, canvas):
        canvas.create_rectangle(
            self.rect.left, self.rect.top - scroll,
            self.rect.right, self.rect.bottom - scroll,
            width = self.thickness,
            outline = self.color
        )

class DrawLine:
    def __init__(self, x1, y1, x2, y2, color, thickness):
        self.rect = Rect(x1, y1, x2, y2)
        self.color = color
        self.thickness = thickness

    def execute(self, scroll, canvas):
        canvas.create_line(
            self.rect.left, self.rect.top - scroll,
            self.rect.right, self.rect.bottom - scroll,
            fill = self.color, width=self.thickness
        )

# Store rectangles representing the size of various elements in browser chrome
class Rect:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def containsPoint(self, x, y):
        return x >= self.left and x < self.right \
        and y >= self.top and y < self.bottom
    

DEFAULT_STYLE_SHEET = CSSParser(open("browser.css").read()).parse()

class Tab:
    def __init__(self, tab_height):
        self.url = None
        self.history = []
        self.tab_height = tab_height
        self.focus = None

        
    def load(self, url, payload=None):
        self.scroll = 0
        self.url = url
        self.history.append(url)
        body = url.request(payload)
        self.nodes = HTMLParser(body).parse()

        self.rules = DEFAULT_STYLE_SHEET.copy()
        links = [node.attributes["href"]
                 for node in tree_to_list(self.nodes, [])
                 if isinstance(node, Element)
                 and node.tag == "link"
                 and node.attributes.get("rel") == "stylesheet"
                 and "href" in node.attributes]
        for link in links:
            try:
                body = url.resolve(link).request()
            except:
                continue
            self.rules.extend(CSSParser(body).parse())

        self.render()
    
    def render(self):
        style(self.nodes, sorted(self.rules, key=cascade_priority))
        self.document = layouts.DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        layouts.paint_tree(self.document, self.display_list)

    def keypress(self, char):
        if self.focus:
            self.focus.attributes["value"] += char
            self.render()

    def draw(self, canvas, offset):
        for cmd in self.display_list:
            if cmd.rect.top > self.scroll + self.tab_height: continue
            if cmd.rect.bottom < self.scroll: continue
            cmd.execute(self.scroll - offset, canvas)

    def scrolldown(self):
        max_y = max(self.document.height + 2*VSTEP - self.tab_height, 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)

    def scrollup(self):
        self.scroll = max(self.scroll - SCROLL_STEP, 0)


    def click(self, x, y):
        self.focus = None
        y += self.scroll
        objs = [obj for obj in tree_to_list(self.document, [])
                if obj.x <= x < obj.x + obj.width
                and obj.y <= y < obj.y + obj.height]
        if not objs: return
        elt = objs[-1].node
        while elt:
            if isinstance(elt, Text):
                pass
            elif elt.tag == "a" and "href" in elt.attributes:
                url = self.url.resolve(elt.attributes["href"])
                return self.load(url)
            elif elt.tag == "input":
                elt.attributes["value"] = ""
                if self.focus:
                    self.focus.is_focused = False
                self.focus = elt
                elt.is_focused = True
                return self.render()
            elif elt.tag == "button":
                while elt:
                    if elt.tag == "form" and "action" in elt.attributes:
                        return self.submit_form(elt)
                    elt = elt.parent
            elt = elt.parent

    def submit_form(self, elt):
        inputs = [node for node in tree_to_list(elt, [])
                  if isinstance(node, Element)
                  and node.tag == "input"
                  and "name" in node.attributes]
        
        body = ""
        for input in inputs:
            name = input.attributes["name"]
            value = input.attributes.get("value", "")
            name = urllib.parse.quote(name)
            value = urllib.parse.quote(value)
            body += "&" + name + "=" + value
        body = body[1:]

        # making a POST request
        url = self.url.resolve(elt.attributes["action"])
        self.load(url, body)

    def go_back(self):
        if len(self.history) > 1:
            self.history.pop()
            back = self.history.pop()
            self.load(back)