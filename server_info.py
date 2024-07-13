from url import *
import tkinter
import tkinter.font
from htmparser import *
from layouts import get_font, INPUT_WIDTH_PX, Rect, DrawRect, DrawText
from author_styles import *
from adding_tabs import DrawLine

class InputLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.children = []
        self.parent = parent
        self.previous = previous
        self.x = None
        self.y = None
        self.width = None
        self.height = None
        self.font = None

    def layout(self):
        weight = self.node.style["font-weight"]
        style = self.node.style["font-style"]
        if style == "normal": style = "roman"
        size = int(float(self.node.style["font-size"][:-2])*.75)
        self.font = get_font(size, weight, style)

        # size of the form box
        self.width = INPUT_WIDTH_PX

        if self.previous:
            space = self.previous.font.measure(" ")
            self.x = self.previous.x + space + self.previous.width
        else:
            self.x = self.parent.x

        self.height = self.font.metrics("linespace")

    def should_paint(self):
        return True
    
    def self_rect(self):
        return Rect(self.x, self.y, self.x+self.width, self.y+self.height)

    def paint(self):
        cmds = []
        bgcolor = self.node.style.get("background-color", "transparent")

        if bgcolor != "transparent":
            rect = DrawRect(self.self_rect(), bgcolor)
            cmds.append(rect)

        if self.node.tag == "input":
            text = self.node.attributes.get("value", "")
        elif self.node.tag == "button":
            if len(self.node.tag) == 1 and \
                isinstance(self.node.children[0], Text):
                text = self.node.childer[0].text
        else:
            print("Ignoring HTML contents inside button")
            text = ""

        color = self.node.style["color"]
        cmds.append(DrawText(self.x, self.y, text, self.font, color))

        if self.node.is_focused:
            cx = self.x + self.font.measure(text)
            cmds.append(DrawLine(cx, self.y, cx, self.y + self.height, "black", 1))

        return cmds