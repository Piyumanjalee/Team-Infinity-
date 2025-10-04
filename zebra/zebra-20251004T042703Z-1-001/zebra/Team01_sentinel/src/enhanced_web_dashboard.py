#!/usr/bin/env python3
"""
Enhanced Web Dashboard with File Upload Capability
================================================
Allows manual data upload and works with both existing and new datasets
"""

import json
import webbrowser
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
import os
import cgi
import tempfile
import urllib.parse
import shutil

class UploadHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/dashboard':
            self.serve_dashboard()
        elif self.path == '/upload':
            self.serve_upload_page()
        elif self.path == '/api/analyze':
            self.run_analysis()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/upload':
            self.handle_file_upload()
        else:
            self.send_error(404)

    def serve_dashboard(self):
        """Serve the main dashboard"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html_content = self.generate_dashboard_html()
        self.wfile.write(html_content.encode('utf-8'))

    def serve_upload_page(self):
        """Serve the file upload page"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html_content = self.generate_upload_html()
        self.wfile.write(html_content.encode('utf-8'))

    def handle_file_upload(self):
        """Handle file uploads"""
        try:
            content_type = self.headers['content-type']
            if not content_type.startswith('multipart/form-data'):
                self.send_error(400, "Bad Request: Expected multipart/form-data")
                return

            # Create uploads directory if it doesn't exist
            upload_dir = "data/uploads"
            os.makedirs(upload_dir, exist_ok=True)

            # Parse the multipart form data
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )

            uploaded_files = []
            
            # Handle each uploaded file
            for field_name in form:
                field = form[field_name]
                if field.filename:
                    filename = field.filename
                    # Save the uploaded file
                    file_path = os.path.join(upload_dir, filename)
                    with open(file_path, 'wb') as f:
                        f.write(field.file.read())
                    uploaded_files.append(filename)

            # Redirect to dashboard with success message
            self.send_response(302)
            self.send_header('Location', f'/?uploaded={len(uploaded_files)}')
            self.end_headers()

        except Exception as e:
            self.send_error(500, f"Upload failed: {str(e)}")

    def run_analysis(self):
        """Run analysis via API call"""
        try:
            # Import and run analysis
            import subprocess
            result = subprocess.run(['python', 'enhanced_master_analysis.py'], 
                                  capture_output=True, text=True)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))

    def generate_dashboard_html(self):
        """Generate main dashboard HTML"""
        # Load analysis results
        try:
            with open('inventory_analysis_report.json', 'r') as f:
                inventory_report = json.load(f)
        except:
            inventory_report = {"shrinkage_events": [], "summary": {"initial_inventory": 0, "final_inventory": 0, "net_change": 0}}

        events = inventory_report.get('shrinkage_events', [])
        summary = inventory_report.get('summary', {})
        
        # Calculate metrics
        total_events = len(events)
        high_risk = len([e for e in events if e.get('severity') == 'HIGH'])
        medium_risk = len([e for e in events if e.get('severity') == 'MEDIUM'])
        products_affected = len(set(e.get('product', '') for e in events))
        
        initial_inv = summary.get('initial_inventory', 0)
        final_inv = summary.get('final_inventory', 0)
        net_change = summary.get('net_change', 0)
        shrinkage_rate = abs(net_change) / max(initial_inv, 1) * 100 if initial_inv > 0 else 0
        
        # Sort events by decrease percentage
        sorted_events = sorted(events, key=lambda x: x.get('decrease_percentage', 0), reverse=True)[:5]
        
        # Check if we have uploaded files
        upload_status = ""
        query = urllib.parse.urlparse(self.path).query
        if query:
            params = urllib.parse.parse_qs(query)
            if 'uploaded' in params:
                upload_count = params['uploaded'][0]
                upload_status = f'<div class="upload-success">✅ Successfully uploaded {upload_count} files!</div>'

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Sentinel - Enhanced Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .controls {{
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        
        .btn {{
            background: linear-gradient(45deg, #007bff, #0056b3);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,123,255,0.3);
        }}
        
        .btn:hover {{
            background: linear-gradient(45deg, #0056b3, #004494);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,123,255,0.4);
        }}
        
        .btn-upload {{
            background: linear-gradient(45deg, #28a745, #1e7e34);
        }}
        
        .btn-upload:hover {{
            background: linear-gradient(45deg, #1e7e34, #155724);
        }}
        
        .btn-analyze {{
            background: linear-gradient(45deg, #ffc107, #e0a800);
        }}
        
        .btn-analyze:hover {{
            background: linear-gradient(45deg, #e0a800, #d39e00);
        }}
        
        .upload-success {{
            background: rgba(40, 167, 69, 0.2);
            border: 2px solid #28a745;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
            font-weight: bold;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-card h3 {{
            font-size: 1.2em;
            margin-bottom: 15px;
            color: #ffd700;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .fraud-alerts {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            margin-bottom: 30px;
        }}
        
        .fraud-alerts h3 {{
            color: #ff6b6b;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        
        .alert-item {{
            background: rgba(255, 107, 107, 0.1);
            border-left: 4px solid #ff6b6b;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
        }}
        
        .data-sources {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            margin-bottom: 30px;
        }}
        
        .data-sources h3 {{
            color: #4ecdc4;
            margin-bottom: 15px;
            font-size: 1.5em;
        }}
        
        .source-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .source-item {{
            background: rgba(78, 205, 196, 0.1);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .loading {{
            display: none;
            text-align: center;
            padding: 20px;
        }}
        
        .loading.show {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ PROJECT SENTINEL - ENHANCED</h1>
            <p>Retail Fraud Detection System with Data Upload</p>
            <div class="status">OPERATIONAL</div>
            <p style="margin-top: 10px; font-size: 0.9em;">Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="controls">
                <a href="/upload" class="btn btn-upload">📤 Upload Data Files</a>
                <button onclick="runAnalysis()" class="btn btn-analyze">🔍 Run Analysis</button>
                <button onclick="location.reload()" class="btn">🔄 Refresh Dashboard</button>
            </div>
            
            {upload_status}
        </div>
        
        <div class="loading" id="loading">
            <h3>🔄 Running Analysis...</h3>
            <p>Please wait while we analyze your data...</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>📊 Total Events</h3>
                <div class="stat-value">{total_events}</div>
                <div class="stat-label">Fraud events detected</div>
            </div>
            
            <div class="stat-card">
                <h3>🏪 Products Affected</h3>
                <div class="stat-value">{products_affected}</div>
                <div class="stat-label">Unique products</div>
            </div>
            
            <div class="stat-card">
                <h3>📈 Initial Inventory</h3>
                <div class="stat-value">{initial_inv:,}</div>
                <div class="stat-label">Items at start</div>
            </div>
            
            <div class="stat-card">
                <h3>🔍 Shrinkage Rate</h3>
                <div class="stat-value">{shrinkage_rate:.2f}%</div>
                <div class="stat-label">Inventory loss rate</div>
            </div>
        </div>
        
        <div class="data-sources">
            <h3>📁 Data Sources Status</h3>
            <div class="source-grid">
                {self.generate_data_source_status()}
            </div>
        </div>
        
        <div class="fraud-alerts">
            <h3>🚨 Top Fraud Alerts</h3>
            {self.generate_alert_html(sorted_events)}
        </div>
    </div>
    
    <script>
        function runAnalysis() {{
            document.getElementById('loading').classList.add('show');
            
            fetch('/api/analyze')
            .then(response => response.json())
            .then(data => {{
                document.getElementById('loading').classList.remove('show');
                if (data.success) {{
                    alert('Analysis completed successfully!');
                    location.reload();
                }} else {{
                    alert('Analysis failed: ' + (data.error || 'Unknown error'));
                }}
            }})
            .catch(error => {{
                document.getElementById('loading').classList.remove('show');
                alert('Error: ' + error.message);
            }});
        }}
        
        // Auto-refresh every 60 seconds
        setTimeout(() => {{
            location.reload();
        }}, 60000);
    </script>
</body>
</html>
"""

    def generate_upload_html(self):
        """Generate file upload page HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Data Files - Project Sentinel</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        
        .upload-form {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        
        .file-group {
            margin-bottom: 25px;
        }
        
        .file-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #ffd700;
        }
        
        .file-input {
            width: 100%;
            padding: 10px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 1em;
        }
        
        .file-input::-webkit-file-upload-button {
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 3px;
            cursor: pointer;
            margin-right: 10px;
        }
        
        .btn {
            background: linear-gradient(45deg, #28a745, #1e7e34);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1.1em;
            font-weight: bold;
            margin: 10px 5px;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            background: linear-gradient(45deg, #1e7e34, #155724);
            transform: translateY(-2px);
        }
        
        .btn-back {
            background: linear-gradient(45deg, #6c757d, #5a6268);
        }
        
        .btn-back:hover {
            background: linear-gradient(45deg, #5a6268, #495057);
        }
        
        .instructions {
            background: rgba(255, 193, 7, 0.1);
            border: 2px solid #ffc107;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        
        .instructions h3 {
            color: #ffc107;
            margin-bottom: 15px;
        }
        
        .instructions ul {
            margin-left: 20px;
        }
        
        .instructions li {
            margin-bottom: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📤 Upload Data Files</h1>
            <p>Upload your retail fraud detection data files</p>
        </div>
        
        <div class="instructions">
            <h3>📋 Instructions:</h3>
            <ul>
                <li><strong>inventory_snapshots.jsonl</strong> - Inventory level data over time</li>
                <li><strong>pos_transactions.jsonl</strong> - Point-of-sale transaction records</li>
                <li><strong>product_recognition.jsonl</strong> - Product recognition confidence scores</li>
                <li><strong>queue_monitoring.jsonl</strong> - Customer queue and dwell time data</li>
                <li><strong>rfid_readings.jsonl</strong> - RFID tag reading events</li>
            </ul>
            <p><strong>Note:</strong> Files must be in JSONL format (one JSON object per line)</p>
        </div>
        
        <form class="upload-form" method="post" enctype="multipart/form-data">
            <div class="file-group">
                <label for="inventory">📦 Inventory Snapshots:</label>
                <input type="file" name="inventory_snapshots.jsonl" class="file-input" accept=".jsonl">
            </div>
            
            <div class="file-group">
                <label for="pos">🛒 POS Transactions:</label>
                <input type="file" name="pos_transactions.jsonl" class="file-input" accept=".jsonl">
            </div>
            
            <div class="file-group">
                <label for="recognition">📱 Product Recognition:</label>
                <input type="file" name="product_recognition.jsonl" class="file-input" accept=".jsonl">
            </div>
            
            <div class="file-group">
                <label for="queue">👥 Queue Monitoring:</label>
                <input type="file" name="queue_monitoring.jsonl" class="file-input" accept=".jsonl">
            </div>
            
            <div class="file-group">
                <label for="rfid">📡 RFID Readings:</label>
                <input type="file" name="rfid_readings.jsonl" class="file-input" accept=".jsonl">
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <button type="submit" class="btn">📤 Upload Files</button>
                <a href="/" class="btn btn-back">← Back to Dashboard</a>
            </div>
        </form>
    </div>
</body>
</html>
"""

    def generate_data_source_status(self):
        """Generate data source status indicators"""
        sources = [
            ("inventory_snapshots.jsonl", "📦 Inventory"),
            ("pos_transactions.jsonl", "🛒 POS Transactions"),
            ("product_recognition.jsonl", "📱 Recognition"),
            ("queue_monitoring.jsonl", "👥 Queue Data"),
            ("rfid_readings.jsonl", "📡 RFID Data")
        ]
        
        html = ""
        for filename, display_name in sources:
            # Check both original location and uploads
            original_path = f"data/input/{filename}"
            upload_path = f"data/uploads/{filename}"
            
            if os.path.exists(upload_path):
                status = "🟢 Uploaded"
                source = "Custom"
            elif os.path.exists(original_path):
                status = "🟡 Default"
                source = "Built-in"
            else:
                status = "🔴 Missing"
                source = "None"
            
            html += f"""
            <div class="source-item">
                <strong>{display_name}</strong><br>
                <span style="font-size: 0.9em;">{status}</span><br>
                <small>{source}</small>
            </div>
            """
        
        return html

    def generate_alert_html(self, events):
        """Generate HTML for fraud alerts"""
        if not events:
            return "<p>No fraud events detected</p>"
        
        html = ""
        for i, event in enumerate(events[:5], 1):
            html += f"""
            <div class="alert-item">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="font-weight: bold; font-size: 1.1em;">{i}. {event.get('product', 'Unknown')}</span>
                    <span style="background: #ff6b6b; color: white; padding: 3px 10px; border-radius: 15px; font-size: 0.8em;">{event.get('severity', 'MEDIUM')}</span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; font-size: 0.9em;">
                    <div><strong>Time:</strong> {event.get('timestamp', 'N/A')}</div>
                    <div><strong>Decrease:</strong> {event.get('decrease_percentage', 0):.1f}%</div>
                    <div><strong>Quantity:</strong> {event.get('previous_qty', 0)} → {event.get('current_qty', 0)}</div>
                </div>
            </div>
            """
        
        return html

def start_enhanced_server():
    """Start the enhanced web server with upload capability"""
    server = HTTPServer(('localhost', 8080), UploadHandler)
    print("🌐 Starting enhanced web dashboard server...")
    print("📊 Dashboard URL: http://localhost:8080")
    print("📤 Upload Page: http://localhost:8080/upload")
    print("🔄 Server supports file uploads and manual data entry")
    print("⏹️  Press Ctrl+C to stop the server")
    
    # Open browser automatically
    threading.Timer(1.0, lambda: webbrowser.open('http://localhost:8080')).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()

if __name__ == "__main__":
    start_enhanced_server()
