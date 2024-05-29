from flask import (
    Flask,
    make_response,
    render_template,
    send_file,
)
from flask.views import MethodView
import os
import re
import stat
import json
import mimetypes
import sys
import urllib

app = Flask(__name__)


def get_type(path):
    if os.path.isdir(path):
        return "dir"
    if os.path.islink(path):
        return "link"

    IMG_EXT = set([".jpg", ".jpeg", ".png", ".gif"])
    VID_EXT = set([".mp4", ".webm", ".mov"])
    GLB_EXT = set([".glb", ".gltf"])

    ext = os.path.splitext(path)[-1].lower()
    if ext in IMG_EXT:
        return "image"
    if ext in VID_EXT:
        return "video"
    if ext in GLB_EXT:
        return "glb"

    return "file"


class PathView(MethodView):
    def __init__(self, root):
        self.root = root

    def get(self, p=""):
        path = os.path.join(self.root, p)
        print(path)

        def get_urlname(name):
            # url from the root path
            return os.path.join("/", p, name)

        if os.path.isdir(path):
            title = f"Contents of {path}"
            contents = []
            for filename in sorted(os.listdir(path)):
                if filename.startswith("."):
                    continue

                # absolute path
                filepath = os.path.join(path, filename)
                urlname = get_urlname(filename)

                stat_res = os.stat(filepath)
                filetype = get_type(filepath)
                displayname = filename
                if filetype == "dir":
                    displayname = f"{filename}/"
                elif filetype == "link":
                    displayname = f"{filename}@"

                info = {
                    "filename": filename,
                    "displayname": displayname,
                    "url": urllib.parse.quote(urlname),
                    "filetype": filetype,
                    "mtime": stat_res.st_mtime,
                    "size": stat_res.st_size,
                }

                contents.append(info)

            parent = os.path.dirname(p.rstrip("/"))
            page = render_template(
                "index.html",
                title=title,
                parent=os.path.join(self.root, parent),
                parent_url=urllib.parse.quote(os.path.join("/", parent)),
                contents=contents,
            )
            res = make_response(page, 200)

        elif os.path.isfile(path):
            print(path)
            res = send_file(os.path.abspath(path), as_attachment=True)

        else:
            res = make_response("Not found", 404)
        return res


def main():
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--root", help="Root of filesystem browser.", default=os.path.abspath("."))
    parser.add_argument("--bind", help="Host to bind server to.", default="localhost")
    parser.add_argument("--port", help="Port to bind server to.", default="8081")
    args = parser.parse_args()

    path_view = PathView.as_view("path_view", args.root)
    app.add_url_rule("/", view_func=path_view)
    app.add_url_rule("/<path:p>", view_func=path_view)

    app.run(args.bind, args.port, threaded=True, debug=True)


if __name__ == "__main__":
    main()
