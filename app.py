import http.server
import os
import sys

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Handle the root directory listing with custom styles
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(self.get_directory_list().encode('utf-8'))
        else:
            # If the path is a directory, handle it with custom HTML
            if os.path.isdir(self.path.strip('/')):
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(self.get_directory_list().encode('utf-8'))
            else:
                # For other requests (files), let the default handler take care of it
                super().do_GET()

    def format_size(self, size):
        """Format size in bytes to KB, MB, or GB."""
        if size < 1024:
            return f"{size} bytes"
        elif size < 1048576:  # 1024 * 1024
            return f"{size / 1024:.2f} KB"
        elif size < 1073741824:  # 1024 * 1024 * 1024
            return f"{size / 1048576:.2f} MB"
        else:
            return f"{size / 1073741824:.2f} GB"

    def get_directory_list(self):
        """Generate a styled HTML list of files and their sizes."""
        directory_path = os.getcwd() + self.path
        try:
            entries = os.listdir(directory_path)
            entries.sort()
            response = """
            <html>
                <head>
                    <title>Directory Listing</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            background-color: #f4f4f4;
                            margin: 0;
                            padding: 20px;
                        }
                        h2 {
                            color: #333;
                        }
                        ul {
                            list-style-type: none;
                            padding: 0;
                        }
                        li {
                            background: #fff;
                            margin: 10px 0;
                            padding: 10px;
                            border-radius: 5px;
                            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                            transition: background 0.3s;
                        }
                        li:hover {
                            background: #e2e2e2;
                        }
                        a {
                            text-decoration: none;
                            font-weight: bold;
                        }
                        .directory {
                            color: #28a745; /* Green for directories */
                        }
                        .file {
                            color: #007BFF; /* Blue for files */
                        }
                        .size {
                            font-size: 0.9em;
                            color: #666;
                        }
                    </style>
                </head>
                <body>
                    <h2>Directory Listing</h2>
                    <ul>
            """
            for entry in entries:
                full_path = os.path.join(directory_path, entry)
                size = os.path.getsize(full_path)
                formatted_size = self.format_size(size)
                
                if os.path.isdir(full_path):
                    entry_display = f'<a href="{entry}/" class="directory">{entry}/</a>'
                else:
                    entry_display = f'<a href="{entry}" class="file">{entry}</a>'
                
                response += f'<li>{entry_display} <span class="size">— {formatted_size}</span></li>'
            
            response += """
                    </ul>
                </body>
            </html>
            """
            return response
        except Exception as e:
            return f"<html><body><h2>Error: {str(e)}</h2></body></html>"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 app.py <path_to_directory>")
        sys.exit(1)

    # Get the directory from command line argument
    directory = sys.argv[1]
    # Ensure the path is correctly expanded
    os.chdir(os.path.expanduser(directory))  # Expand user if ~ is used
    http.server.test(HandlerClass=CustomHTTPRequestHandler)

