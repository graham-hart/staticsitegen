# Static Site Generator

## File Structure:

```
site/
    - content/
        - about.md
        - index.md
        - blogs/
            - b1.md
            - b2.md
    - src/
        script.js
        style.css
```

This will generate:

```
rendered/
    - about.html
    - index.html
    - blogs/
        - blogs.html
        - b1.html
        - b2.html
    - src/
        script.js
        style.css
```

## Setup

Written in python3.9.4. Hasn't been tested for other version compatibility.
Requirements: 
- Jinja2 
- Mistletoe 
- PyYAML 

## Usage

All markdown files must have a header delimeted by three dashed lines (---). Use the above directory structure for your project, or copy my example (which doesn't exist as of yet). Customize templates, css, etc. It'll look better that way, I promise.

The navbar will include all links inside the `content/` directory. To block certain directories from being included, simply add a file named `__navignore__` inside that directory.

To render once, run the file `renderer.py`. Currently, arguments are not implemented, so your project directory will need to be called `site`. To run with a webserver, run `webserver.py`. It takes arguments for port, debug mode, and input directory. In debug mode, webpages are rendered on the fly only when they are requested. This should only be used for testing, because it will put a lot of strain on the server if many people are requesting the page at the same time.
