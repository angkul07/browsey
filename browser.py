from url import URL
import tkinter
import tkinter.font
from htmparser import HTMLParser
from layouts import DocumentLayout, paint_tree, Element
    
WIDTH, HEIGHT = 960, 720
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

# chapter 6 start

def tree_to_list(tree, list):
    list.append(tree)
    for child in tree.children:
        tree_to_list(child, list)
    return list

class CSSParser:
    def __init__(self, s):
        self.s = s
        self.i = 0

    def whitespace(self):
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1

    def literal(self, literal):
        if not (self.i < len(self.s) and self.s[self.i] == literal):
            raise Exception("Parsing error")
        self.i += 1

    def word(self):
        start = self.i
        while self.i < len(self.s):
            if self.s[self.i].isalnum() or self.s[self.i] in "#-.%":
                self.i += 1
            else:
                break
        if not (self.i > start):
            raise Exception("Parsing error")    
        return self.s[start:self.i]
    
    def ignore_until(self, chars):
        while self.i < len(self.s):
            if self.s[self.i] in chars:
                return self.s[self.i]
            else:
                self.i += 1
        return None
    
    def pair(self):
        prop = self.word()
        self.whitespace()
        self.literal(":")
        self.whitespace()
        val = self.word()
        return prop.casefold(), val
    
    def selector(self):
        out = TagSelector(self.word().casefold())
        self.whilespace()
        while self.i < len(self.s) and self.s[self.i] != "{":
            tag = self.word()
            descendant = TagSelector(tag.casefold())
            out = DescendantSelector(out, descendant)
            self.whitespace()
        return out
    
    def body(self):
        pairs = {}
        while self.i < len(self.s) and self.s[self.i] != "}":
            try:
                prop, val = self.pair()
                pairs[prop.casefold()] = val
                self.whitespace()
                self.literal(";")
                self.whitespace()
            except Exception:
                why = self.ignore_until([";", "}"])
                if why == ";":
                    self.literal(";")
                    self.whitespace()
                else:
                    break
        return pairs
    
    
    def parse(self):
        rules = []
        while self.i < len(self.s):
            try:
                self.whitespace()
                selector = self.selector()
                self.literal("{")
                self.whitespace()
                body = self.body()
                self.literal("}")
                rules.append((selector, body))
            except Exception:
                why = self.ignore_until(["}"])
                if why == "}":
                    self.literal("}")
                    self.whitespace()
                else:
                    break
        return rules
    
class TagSelector:
    def __init__(self, tag):
        self.tag = tag
        self.priority = 1

    def matches(self, node):
        return isinstance(node, Element) and self.tag == node.tag
    
class DescendantSelector:
    def __init__(self, ancestor, descendant):
        self.ancestor = ancestor
        self.descendant = descendant
        self.priority = ancestor.priority + descendant.priority


    def matches(self, node):
        if not self.descendant.matches(node): return False
        while node.parent:
            if self.ancestor.matches(node.parent): return True
            node = node.parent
        return False
    
INHERITED_PROPERTIES = {
    "font-size": "16px",
    "font-style": "normal",
    "font-weight": "normal",
    "color": "black",
}
    
def style(node, rules):
    node.style = {}

    for property, default_value in INHERITED_PROPERTIES.items():
        if node.parent:
            node.style[property] = node.parent.style[property]
        else:
            node.style[property] = default_value

    for selector, body in rules:
        if not selector.matches(node): continue
        for property, value in body.items():
            node.style[property] = value

    if isinstance(node, Element) and "style" in node.attributes:
        pairs = CSSParser(node.attributes["style"]).body()
        for property, value in pairs.items():
            node.style[property] = value

    if node.style["font-size"].endswith("%"):
        if node.parent:
            parent_font_size = node.parent.style["font-size"]
        else:
            parent_font_size = INHERITED_PROPERTIES["font-size"]
        node_pct = float(node.style["font-size"][:-1])/100
        parent_px = float(parent_font_size[:2])
        node.style["font-size"] = str(node_pct * parent_px) + "px"
        
    for child in node.children:
        style(child, rules)

def cascade_priority(rule):
    selector, body = rule
    return selector.priority
    

# chapter 6 end

DEFAULT_STYLE_SHEET = CSSParser(open("/home/angkul/my_data/coding/browser/browser.css").read()).parse()

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.title("Browsey")
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT,
            bg="white",
        )
        bar = tkinter.Scrollbar(self.window)
        bar.pack(side="right", fill= "y")
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.display_list = []
        
    def load(self, url):
        body = url.request()
        self.nodes = HTMLParser(body).parse()

        rules = DEFAULT_STYLE_SHEET.copy()
        links = [node.attributes["href"]
                 for node in tree_to_list(self.nodes, [])
                 if isinstance(node, Element)
                 and node.tag == "link"
                 and node.attributes.get("rel") == "stylesheet"
                 and "href" in node.attributes]
        for link in links:
            style_url = url.resolve(link)
            try:
                body = style_url.request()
            except:
                continue
            rules.extend(CSSParser(body).parse())
        style(self.nodes, sorted(rules, key=cascade_priority))
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
        self.draw()

    def scrolldown(self, e):
        max_y = max(self.document.height + 2*VSTEP - HEIGHT, 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)
        self.draw()

    def scrollup(self, e):
        self.scroll = max(self.scroll - SCROLL_STEP, 0)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for cmd in self.display_list:
            if cmd.top > self.scroll + HEIGHT: continue
            if cmd.bottom < self.scroll: continue
            cmd.execute(self.scroll, self.canvas)


if __name__ == "__main__":
    import sys
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()