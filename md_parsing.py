from mistletoe.span_token import SpanToken
from mistletoe.html_renderer import HTMLRenderer
from mistletoe import Document
import re

class Media(SpanToken):
    pattern = re.compile("!v\(\w*\.\w*\)")
    parse_inner = False
    def __init__(self, match):
        self.target = match.group(2)

class MediaRenderer(HTMLRenderer):
    def __init__(self):
        super().__init__(Media)

    def render_media(self, token):
        print(token.target)
        return "A"

if __name__ == '__main__':
    with open('site/content/index.md', "r") as file:
        with MediaRenderer() as renderer:
            rendered = renderer.render(Document(file))
            print(rendered)