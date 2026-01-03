# dashboard/server.py
import http.server
import socketserver
import webbrowser
import logging

# Setup a specific logger for the server
logger = logging.getLogger("PhishingAgent")

def serve_dashboard(port=8000, directory="dashboard"):
    """
    Starts a local HTTP server to host the dashboard directory.
    This blocks execution until stopped by the user.
    """
    
    # Custom handler to serve files from the specific 'dashboard' directory
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)
        
        # Suppress default HTTP request logs to keep console clean
        def log_message(self, format, *args):
            pass

        def do_POST(self):
            if self.path == '/clear':
                from processing.queue_manager import clear_db
                from dashboard.renderer import render_dashboard
                
                # Clear the DB
                clear_db()
                
                # Re-render an empty dashboard immediately
                render_dashboard([])
                
                # Send response
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
            else:
                self.send_error(404)

        def end_headers(self):
            self.send_header('Content-Security-Policy', "default-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'")
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('X-Frame-Options', 'DENY')
            super().end_headers()

    # Allow reuse of the port to prevent "Address already in use" errors
    socketserver.TCPServer.allow_reuse_address = True

    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            url = f"http://localhost:{port}/report.html"
            logger.info("---")
            logger.info(f"🚀 Dashboard is live at: {url}")
            logger.info("Press Ctrl+C to stop the server and exit.")
            logger.info("---")
            
            # Automatically open the default web browser
            webbrowser.open(url)
            
            # Start the server loop
            httpd.serve_forever()
            
    except OSError as e:
        logger.error(f"Could not start server on port {port}: {e}")
    except KeyboardInterrupt:
        logger.info("\nStopping dashboard server...")