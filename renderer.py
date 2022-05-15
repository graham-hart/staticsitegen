#!./env/bin/python

from asyncio.log import logger
from re import TEMPLATE
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

# Generate a file tree where keys are file names and values are contents
# Structure:
"""
{
        'directory/': {
        'file_1': 'file_1_contents', 
        'file_2': 'file_2_contents', 
        'sub_directory': {
            'file_3': 'file_3_contents'
        }
    }
}
"""

def gen_file_tree(path, remove_str=None):
    if remove_str is None:
        remove_str = path
    tree = {}
    contents = os.listdir(path)
    for c in contents:
        fp = os.path.join(path, c)
        if os.path.isfile(fp):
            tree[fp.replace(remove_str, "")] = open(fp).read()
        else:
            tree[fp.replace(remove_str, "")] = gen_file_tree(fp, remove_str=remove_str)
    return tree

# Generate dictionary of metadata from file header
def gen_meta(header):
    meta = {}
    for ln in header.split("\n"):
        index = ln.find(":")
        if index > -1:
            meta[ln[:index].strip()] = ln[index+1:].strip()

    return meta


# TODO: Add support for rendering files that don't exist (aka landing pages for different directories that should be auto-generated)
def render_single_file(path, text=None, template=None):
    HEADER_SPLITTER = "---" # String to use to separate out header
    template = template or TEMPLATES[CONFIG["default_template"]] # Find template if none given
    text = text or open(path, "r").read() # Load text if none given

    # Generate metadata and content
    try:
        s = text.split(HEADER_SPLITTER)
        meta = gen_meta(s[1])
        content = '\n'.join(s[2:])
    except:
        logger.warning(f"File {path} does not have metadata (or it's in the wrong format)")


    # TODO: Add audio and video embed support to rendering (https://github.com/miyuchina/mistletoe and https://talk.commonmark.org/t/embedded-audio-and-video/441)
    rendered = mistletoe.markdown(content)

    # Render page and save to file
    out = template.render(content=rendered, nav_links=NAV_LINKS, meta=meta)
    return out

# Recursive function to generate formatted html pages into out_path
# Options for multiple templates using the config, but this may require some tinkering
# Renders markdown to html

def generate_pages(current_dir, file_tree=None):
    file_tree = file_tree or FILE_TREE
    # Load config
    local_conf = None
    if "config.yml" in os.listdir(current_dir):
        with open(os.path.join(current_dir, 'config.yml')) as f:
            local_conf = yaml.load(f, Loader=yaml.SafeLoader)
    

    # Iterate through all paths in file tree at current directory level
    for f in file_tree.keys():

        # If current path is a folder
        if type(file_tree[f]) is dict:

            os.mkdir(f"{OUTPUT_DIR}{f}/")
            
            # Render landing page for folder 
            # TODO: Add more customizability for this option
            out = render_single_file(f"{OUTPUT_DIR}{f}/index.md",
                               template=TEMPLATES['base.html'])
            with open(f"{OUTPUT_DIR}{f}/index.html", "w") as file:
                file.write(out)

            # Call function recursively on current path
            generate_pages(os.path.join(current_dir, f[1:]), file_tree=file_tree[f])
        elif f.endswith('.md'):
            # Figure out which template to use
            template = TEMPLATES[local_conf.get('template', CONFIG['default_template'])] if local_conf else TEMPLATES[CONFIG['default_template']]
            out = render_single_file(f, text=file_tree[f], template=template)
            with open(f"{OUTPUT_DIR}/{os.path.splitext(f)[0]}.html", "w") as file:
                file.write(out)

def setup(template_path):
    global ENV, CONFIG, TEMPLATES, NAV_LINKS, FILE_TREE
    file_loader = FileSystemLoader(template_path)
    ENV = Environment(loader=file_loader)
    CONFIG = yaml.load(open(f"{SITE_DIR}/config.yml"), Loader=yaml.SafeLoader)
    TEMPLATES = load_templates(template_path)
    NAV_LINKS = CONFIG['navbar'].items()
    FILE_TREE = gen_file_tree(f"{SITE_DIR}/content")



def load_templates(path): # Load all templates into a dict
    templates = {}
    for t in os.listdir(path):
        templates[t] = ENV.get_template(t)
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

