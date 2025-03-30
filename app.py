import http.server
import os
import sys
import stat
from urllib.parse import unquote
from jinja2 import Environment, FileSystemLoader
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "assets")

# Set up the Jinja2 environment using the templates folder.
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests properly."""
        decoded_path = unquote(self.path)
        full_path = os.path.join(os.getcwd(), decoded_path.lstrip("/"))
        
        if decoded_path.startswith("/assets/"):
            self.serve_static_file(decoded_path)
        elif os.path.isdir(full_path):
            self.serve_directory_list(full_path)
        elif decoded_path == "/":
            self.serve_html("index.html", {})
        elif os.path.isfile(full_path):
            self.serve_file(full_path)
        else:
            self.serve_html("404.html", {}, status=404)
    
    def format_size(self, size):
        """Format file size into human-readable form."""
        if size < 1024:
            return f"{size} bytes"
        elif size < 1048576:
            return f"{size / 1024:.2f} KB"
        elif size < 1073741824:
            return f"{size / 1048576:.2f} MB"
        else:
            return f"{size / 1073741824:.2f} GB"
    
    def get_permissions(self, path):
        """Return a list of permission strings for a file."""
        st_mode = os.stat(path).st_mode
        permissions = []
        if st_mode & stat.S_IRUSR:
            permissions.append("Read")
        if st_mode & stat.S_IWUSR:
            permissions.append("Write")
        if st_mode & stat.S_IXUSR:
            permissions.append("Execute")
        return permissions

    def serve_html(self, page, context=None, status=200):
        """Render an HTML template using Jinja2."""
        context = context or {}
        try:
            template = env.get_template(page)
            html = template.render(context)
        except Exception as e:
            html = f"<h1>Error rendering template</h1><p>{e}</p>"
            status = 500
        self.send_response(status)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def serve_static_file(self, path):
        """Serve static assets (CSS, JS, images, etc.)."""
        file_path = os.path.join(BASE_DIR, path.lstrip("/"))
        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.send_response(200)
            if file_path.endswith(".css"):
                self.send_header("Content-type", "text/css")
            elif file_path.endswith(".js"):
                self.send_header("Content-type", "application/javascript")
            elif file_path.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg")):
                self.send_header("Content-type", f"image/{file_path.split('.')[-1]}")
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.serve_html("404.html", {}, status=404)

    def serve_directory_list(self, directory_path):
        """Generate a directory listing and render it using a template."""
        try:
            entries = sorted(os.listdir(directory_path))
            items = []
            parent_dir = os.path.dirname(self.path)  # Parent URL

            # Get the current directory path relative to the server root.
            current_path = os.path.relpath(directory_path, start=os.getcwd())

            # Inject server IP and port into the current path
            server_address = f"{self.server.server_address[0]}:{self.server.server_address[1]}"
            full_current_path = f"http://{server_address}/{current_path}"

            for entry in entries:
                full_entry_path = os.path.join(directory_path, entry)
                # Build URL and ensure spaces are encoded.
                entry_url = os.path.join(self.path, entry).replace(" ", "%20")
                size = self.format_size(os.path.getsize(full_entry_path)) if os.path.isfile(full_entry_path) else "-"
                permissions = self.get_permissions(full_entry_path)
                item = {
                    "name": entry,
                    "url": entry_url,
                    "size": size,
                    "permissions": permissions,
                    "is_dir": os.path.isdir(full_entry_path),
                    "can_read": "Read" in permissions,
                    "can_write": "Write" in permissions,
                    "can_execute": "Execute" in permissions,
                }
                items.append(item)
            context = {
                "parent_dir": parent_dir,
                "items": items,
                "current_path": full_current_path  # Add full URL as current path
            }
            self.serve_html("directory.html", context)
        except Exception as e:
            self.serve_html("404.html", {}, status=404)

    def serve_file(self, file_path):
        """Serve a file for download."""
        self.send_response(200)
        self.send_header("Content-Disposition", f'attachment; filename="{os.path.basename(file_path)}"')
        self.send_header("Content-type", "application/octet-stream")
        self.end_headers()
        with open(file_path, "rb") as f:
            self.wfile.write(f.read())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple HTTP file server")
    parser.add_argument("directory", help="Path to the directory to serve")
    parser.add_argument("--ip", default="0.0.0.0", help="IP address to bind the server (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server (default: 8000)")

    args = parser.parse_args()

    # Expand user directory if '~' is used
    directory = os.path.expanduser(args.directory)
    
    # Check if the directory exists before changing into it
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        sys.exit(1)

    os.chdir(directory)

    # Print out the IP and port information
    print(f"Serving HTTP on {args.ip} port {args.port} (http://{args.ip}:{args.port}/) ...")

    # Create and run the HTTP server
    handler = CustomHTTPRequestHandler
    http.server.test(HandlerClass=handler, port=args.port, bind=args.ip)