"""
Vercel Serverless Function Entry Point for AirFusion Environmental Intelligence.
Serves the web gateway and redirects to active deployment.

SERVERLESS HYGIENE GUARANTEES:
1. Purely stateless execution — zero reliance on local disk or SQLite databases.
2. Read-only operation: passes public/index.html to response stream.
3. Telemetry database logging operates exclusively in the local Streamlit application
   (airfusion/src/database.py & airfusion/app/Home.py).
"""

from http.server import BaseHTTPRequestHandler
from pathlib import Path

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

        html_file = Path(__file__).resolve().parent.parent / "public" / "index.html"
        if html_file.exists():
            with open(html_file, "r", encoding="utf-8") as f:
                html_content = f.read()
        else:
            html_content = """<!DOCTYPE html>
<html>
<head><title>AirFusion — Environmental Intelligence</title></head>
<body style="font-family: sans-serif; text-align: center; padding: 40px;">
  <h1>AirFusion — Environmental Intelligence</h1>
  <p>Autonomous environmental intelligence and real-time air quality forecasting platform.</p>
  <a href="https://github.com/akshatk1997/airfusion">View on GitHub &rarr;</a>
</body>
</html>"""

        self.wfile.write(html_content.encode('utf-8'))
