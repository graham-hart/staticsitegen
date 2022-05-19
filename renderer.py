#!./env/bin/python

from asyncio.log import logger
from jinja2 import Environment, FileSystemLoader
import os
import shutil
import yaml
import mistletoe


# Global config stuff
NAV_LINKS = None
ENV = None
CONFIG = None
SITE_DIR = "site"
OUTPUT_DIR = "rendered"
TEMPLATES = None
FILE_TREE = None

HEADER_SPLITTER = "---"  # String to use to separate out header

def find_content_path(p):
    return os.path.join(SITE_DIR, 'content', p)

def find_rendered_path(p):
    path = os.path.join(OUTPUT_DIR, p)
    if path.endswith(".md"):
        return path.replace(".md", ".html")
    return path

def content_to_rendered_path(p):
    return find_rendered_path(p.removeprefix(os.path.join(SITE_DIR, "content")))

def rendered_to_content_path(p):
    return find_content_path(p.removeprefix(OUTPUT_DIR))


# Way to store directories/file trees
class Directory:
    def __init__(self, path, parent=None):
        self.path = path
        self.parent = parent
        self.files = []
        self.dirs = {}
    
    @property
    def fn(self):
        return os.path.split(self.path)[1]
    
    def load_tree(self, remove_str=None):
        remove_str = remove_str or self.path
        contents = os.listdir(self.path)
        for c in contents:
            fp = os.path.join(self.path, c)
            if os.path.isfile(fp):
                self.files.append(fp.removeprefix(remove_str).removeprefix("/"))
            else:
                nfp = fp.removeprefix(remove_str).removeprefix("/")
                self.dirs[nfp] = Directory(fp, parent=self)
                self.dirs[nfp].load_tree(remove_str=remove_str)

    def find_directory(self, path, depth=0):
        split_path = path.removeprefix("./").split("/")
        if len(split_path) == depth:
            return self
        return self.dirs[split_path[depth]].find_directory(path, depth=depth+1)
        
        


# Generate dictionary of metadata from file header
def gen_meta(header):
    meta = {}
    for ln in header.split("\n"):
        index = ln.find(":")
        if index > -1:
            meta[ln[:index].strip()] = ln[index+1:].strip()

    return meta

def get_file_meta(path):
    txt = open(path).read()
    header = txt.split(HEADER_SPLITTER)[1]
    return gen_meta(header)

def render_single_file(path, template=None):
    if os.path.exists(find_content_path(path)):
        path = find_content_path(path)
        text = open(path, "r").read() # Load text 
        content = ""
        meta = {}

        # Generate metadata and content
        try:
            s = text.split(HEADER_SPLITTER)
            meta = gen_meta(s[1])
            content = s[2]
        except:
            logger.warning(f"File {path} does not have metadata (or it's in the wrong format)")

        template = template or TEMPLATES[meta.get(
                "template", CONFIG["default_template"])]
        # TODO: Add audio and video embed support to rendering (https://github.com/miyuchina/mistletoe and https://talk.commonmark.org/t/embedded-audio-and-video/441)
        return template.render(content=mistletoe.markdown(content), nav_links=NAV_LINKS, meta=meta)
    else:
        template = TEMPLATES[CONFIG["landing_page_template"]]
        d = FILE_TREE.find_directory(os.path.split(path)[0])
        pages = []
        for file in d.files:
            fn = find_content_path(file)
            text = open(fn, "r").read()
            s = text.split(HEADER_SPLITTER)
            meta = gen_meta(s[1])
            content = s[2]
            pages.append({"title": meta["title"], "author":meta["author"], "preview":"", "link": f"{find_rendered_path(file).removeprefix('rendered')}"})
        return template.render(pages=pages, title=os.path.splitext(path)[0].title(), nav_links=NAV_LINKS)

# Recursive function to generate formatted html pages into out_path
# Options for multiple templates using the config, but this may require some tinkering
# Renders markdown to html


def generate_pages(current_dir, directory=None):
    directory = directory or FILE_TREE

    # Iterate through all paths in file tree at current directory level
    for f in directory.files:
        out = render_single_file(f)
        with open(os.path.join(OUTPUT_DIR, f"{os.path.splitext(f)[0]}.html"), "w") as file:
            file.write(out)

    for d in directory.dirs.keys():
        os.mkdir(os.path.join(OUTPUT_DIR, d))

        # Render landing page for folder
        out = render_single_file(os.path.join(
            d, "index.html"), template=TEMPLATES[CONFIG['landing_page_template']])
        with open(os.path.join(OUTPUT_DIR, d, 'index.html'), "w") as file:
            file.write(out)

        # Call function recursively on current path
        generate_pages(os.path.join(
            current_dir, f[1:]), directory=directory.dirs[d])

def setup(template_path):
    global ENV, CONFIG, TEMPLATES, NAV_LINKS, FILE_TREE
    file_loader = FileSystemLoader(template_path)
    ENV = Environment(loader=file_loader)
    CONFIG = yaml.load(open(f"{SITE_DIR}/config.yml"), Loader=yaml.SafeLoader)
    TEMPLATES = load_templates(template_path)
    NAV_LINKS = CONFIG['navbar'].items()
    FILE_TREE = Directory(f"{SITE_DIR}/content")
    FILE_TREE.load_tree()



def load_templates(path): # Load all templates into a dict
    templates = {}
    for t in os.listdir(path):
        templates[os.path.splitext(t)[0]] = ENV.get_template(t)
    return templates

def generate_site():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.mkdir(OUTPUT_DIR)

    # Copy src files to output
    shutil.copytree(f"{SITE_DIR}/src", f"{OUTPUT_DIR}/src") 

    generate_pages(f"{SITE_DIR}/content")


if __name__ == '__main__':
    setup('templates/')
    generate_site()

