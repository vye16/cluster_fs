import io
import os
import math
import sys
import html
import urllib
from jinja2 import Template
from http.server import HTTPServer, SimpleHTTPRequestHandler


SRC_DIR = os.path.abspath("__file__/..")


class ImageDirRequestHandler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        try:
            file_list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None

        file_list.sort(key=lambda a: a.lower())
        displaypath = html.escape(urllib.parse.unquote(self.path))
        enc = sys.getfilesystemencoding()
        title = "Directory listing for {}".format(displaypath)
        parent = os.path.dirname(path.rstrip("/"))
        parent_name = "{}/".format(os.path.basename(parent))
        parent_path = "../../{}".format(parent_name)

        elements = []
        for name in file_list:
            if name.startswith("."):  # skip hidden files
                continue

            fullname = os.path.join(path, name)
            displayname = linkname = name

            # Append / for directories or @ for symbolic links
            # (a link to a directory displays with @ and links with /)
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"

            if os.path.islink(fullname):
                displayname = name + "@"

            if isimage(name):
                filetype = "image"
            elif isvideo(name):
                filetype = "video"
            elif isglb(name):
                filetype = "glb"
            else:
                filetype = "file"

            url = urllib.parse.quote(linkname)
            filename = os.path.basename(linkname)
            elements.append({
                "filetype": filetype,
                "filename": filename,
                "linkname": linkname,
                "displayname": displayname,
                "url": url
            })
        
        with open(os.path.join(SRC_DIR, "templates/simple_index.html"), "r") as f:
            template = Template(f.read())

        rendered = template.render(
            title=title,
            enc=enc,
            parent=parent,
            parent_path=parent_path,
            elements=elements,
        )

        encoded = rendered.encode(enc)
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset={}".format(enc))
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f


def isimage(path):
    IMG_EXT = set(["jpg", "jpeg", "png", "gif", "bmp"])
    ext = path.split(".")[-1].lower()
    return ext in IMG_EXT


def isvideo(path):
    ext = path.split(".")[-1].lower()
    return ext == "mp4"


def isglb(path):
    GLB_EXT = set(["glb", "gltf"])
    ext = path.split(".")[-1].lower()
    return ext in GLB_EXT


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--root", default=os.path.expanduser("~"))
    parser.add_argument("--height", type=int, default=400)
    args = parser.parse_args()

    # Make sure the server is created at current directory
    os.chdir(args.root)
    # Create server object listening the port 80
    server_object = HTTPServer(
        server_address=("", args.port), RequestHandlerClass=ImageDirRequestHandler
    )
    # Start the web server
    server_object.serve_forever()
