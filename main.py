#!./env/bin/python

from jinja2 import Environment, FileSystemLoader
import os
import shutil

def crawl_dir(path, remove_str=None):
    if remove_str is None:
        remove_str = path
    tree = {}
    contents = os.listdir(path)
    for c in contents:
        fp = os.path.join(path, c)
        if os.path.isfile(fp):
            tree[fp.replace(remove_str, "")] = open(fp).read()
        else:
            tree[fp.replace(remove_str, "")] = crawl_dir(fp, remove_str=remove_str)
    return tree

def gen_navbar_links(file_tree):
    nav_links = []
    nav_links.append(("Home", "/"))
    for i in file_tree.keys():
        fn = os.path.split(i)[-1]
        nav_links.append((os.path.splitext(fn)[0].title(), f"{os.path.splitext(i)[0]}.html"))
    return nav_links

def main():
    if not os.path.exists("generated"):
        os.mkdir("generated")
    # elif input("Do you wish to overwrite folder 'generated/'? [y/n]").lower() == 'n':
    #     return 

    # Jinja2 Setup
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)

    # Open Template
    template = env.get_template('tmp.html')

    # Copy src files to generated
    if os.path.exists("generated/src"):
        shutil.rmtree("generated/src")
    shutil.copytree("site/src", "generated/src") 

    # Generate file tree
    file_tree = crawl_dir('site/content')

    # Generate navbar links
    nav_links = gen_navbar_links(file_tree)

    # Generate index.html
    out = template.render(length=20, nav_links=nav_links, title="Home")
    with open("generated/index.html", "w") as f:
        f.write(out)

if __name__ == '__main__':
    main()
