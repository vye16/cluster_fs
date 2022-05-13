import io
import os
import sys
import html
import urllib
from http.server import HTTPServer, SimpleHTTPRequestHandler


class ImageDirRequestHandler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        try:
            file_list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None

        file_list.sort(key=lambda a: a.lower())
        r = []
        displaypath = html.escape(urllib.parse.unquote(self.path))
        enc = sys.getfilesystemencoding()
        title = "Directory listing for {}".format(displaypath)
        r.append("<!DOCTYPE html>\n<html>\n<head>")
        r.append(
            '<meta http-equiv="Content-Type" '
            'content="text/html; charset={}">'.format(enc)
        )
        r.append("<style> img { image-rendering: pixelated; } </style>")
        r.append("<title>{}</title>\n</head>".format(os.path.basename(title)))
        r.append(
            '<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>'
        )
        r.append("<body>\n<h1>{}</h1>".format(title))
        ## keep a link to go back to parent
        parent = os.path.dirname(path.rstrip("/"))
        parent_name = "{}/".format(os.path.basename(parent))
        parent_path = "../../{}".format(parent_name)
        r.append(
            '<hr>\nback to parent: <a href="{}">{}</a>\n'.format(parent_path, parent)
        )
        r.append("<hr>\n<ul>")

        for name in file_list:
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
                token = show_image(linkname)
            elif isvideo(name):
                token = show_video(linkname)
            else:
                token = show_file_link(linkname, displayname)
            r.append(token)
        r.append("</ul>\n<hr>\n</body>\n</html>\n")
        encoded = "\n".join(r).encode(enc)
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset={}".format(enc))
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f


IMG_EXT = set(["jpg", "jpeg", "png", "gif", "bmp"])


def isimage(path):
    ext = path.split(".")[-1].lower()
    return ext in IMG_EXT


def isvideo(path):
    ext = path.split(".")[-1].lower()
    return ext == "mp4"


def show_file_link(linkname, displayname):
    return '<li><a href="{}">{}</a></li>'.format(
        urllib.parse.quote(linkname),
        html.escape(displayname),
    )


def show_image(linkname, td_style="", height=400):
    filename = os.path.basename(linkname)
    #     img_str = '<img src="{}" height="{}px">'.format(linkname, height)
    img_str = '<img src="{}">'.format(linkname)
    ref_str = '<a href="{}" download>{}</a>'.format(
        urllib.parse.quote(linkname),
        filename,
    )
    return "\t\t<td {} align=center> {} <br> {} <br> </td>".format(
        td_style,
        ref_str,
        img_str,
    )


def show_video(linkname, autoplay=True, td_style=""):
    filename = os.path.basename(linkname)
    ext = filename.split(".")[-1].lower()
    vid_str = '<video controls autoplay><source src="{}" type="video/{}"></video>'.format(
        linkname, ext
    )
    ref_str = '<a href="{}" download>{}</a>'.format(
        urllib.parse.quote(linkname),
        filename,
    )
    return "\t\t<td {} align=center> {} <br> {} <br> </td>".format(
        td_style,
        ref_str,
        vid_str,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--root", default="/home/vye/moving-layers")
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
