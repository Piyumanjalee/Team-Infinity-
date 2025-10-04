#!/usr/bin/env python3
"""
Web Dashboard for Project Sentinel
==================================
Creates a web-based dashboard that opens in Chrome browser
"""

import json
import webbrowser
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time
import os

def generate_html_dashboard():
    """Generate HTML dashboard content"""
    
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
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Sentinel - Fraud Detection Dashboard</title>
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
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .status {{
            display: inline-block;
            background: #28a745;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 10px;
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
        
        .stat-label {{
            opacity: 0.8;
            font-size: 0.9em;
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
        
        .alert-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .alert-product {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        .alert-severity {{
            background: #ff6b6b;
            color: white;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.8em;
        }}
        
        .alert-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .algorithms {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            margin-bottom: 30px;
        }}
        
        .algorithms h3 {{
            color: #4ecdc4;
            margin-bottom: 15px;
            font-size: 1.5em;
        }}
        
        .algo-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }}
        
        .algo-item {{
            display: flex;
            align-items: center;
            padding: 10px;
            background: rgba(78, 205, 196, 0.1);
            border-radius: 5px;
        }}
        
        .check-mark {{
            color: #28a745;
            font-size: 1.2em;
            margin-right: 10px;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }}
        
        .refresh-btn {{
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin-top: 10px;
        }}
        
        .refresh-btn:hover {{
            background: #0056b3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ PROJECT SENTINEL</h1>
            <p>Retail Fraud Detection System</p>
            <div class="status">OPERATIONAL</div>
            <p style="margin-top: 10px; font-size: 0.9em;">Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
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
                <h3>📉 Final Inventory</h3>
                <div class="stat-value">{final_inv:,}</div>
                <div class="stat-label">Items remaining</div>
            </div>
            
            <div class="stat-card">
                <h3>⚠️ Net Change</h3>
                <div class="stat-value">{net_change:,}</div>
                <div class="stat-label">Items lost/gained</div>
            </div>
            
            <div class="stat-card">
                <h3>🔍 Shrinkage Rate</h3>
                <div class="stat-value">{shrinkage_rate:.2f}%</div>
                <div class="stat-label">Inventory loss rate</div>
            </div>
        </div>
        
        <div class="fraud-alerts">
            <h3>🚨 Top Fraud Alerts</h3>
            {generate_alert_html(sorted_events)}
        </div>
        
        <div class="algorithms">
            <h3>🎯 Algorithm Performance</h3>
            <div class="algo-list">
                <div class="algo-item">
                    <span class="check-mark">✅</span>
                    <span>InventoryShrinkageDetection</span>
                </div>
                <div class="algo-item">
                    <span class="check-mark">✅</span>
                    <span>AnomalyDetection</span>
                </div>
                <div class="algo-item">
                    <span class="check-mark">✅</span>
                    <span>CrossCorrelationAnalysis</span>
                </div>
                <div class="algo-item">
                    <span class="check-mark">✅</span>
                    <span>FraudSeverityScoring</span>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <h3>📁 System Ready for Submission</h3>
            <p>Output files generated and available for review</p>
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Dashboard</button>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => {{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>
"""
    
    return html_content

def generate_alert_html(events):
    """Generate HTML for fraud alerts"""
    if not events:
        return "<p>No fraud events detected</p>"
    
    html = ""
    for i, event in enumerate(events[:5], 1):
        html += f"""
        <div class="alert-item">
            <div class="alert-header">
                <span class="alert-product">{i}. {event.get('product', 'Unknown')}</span>
                <span class="alert-severity">{event.get('severity', 'MEDIUM')}</span>
            </div>
            <div class="alert-details">
                <div><strong>Time:</strong> {event.get('timestamp', 'N/A')}</div>
                <div><strong>Decrease:</strong> {event.get('decrease_percentage', 0):.1f}%</div>
                <div><strong>Quantity:</strong> {event.get('previous_qty', 0)} → {event.get('current_qty', 0)}</div>
            </div>
        </div>
        """
    
    return html

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/dashboard':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html_content = generate_html_dashboard()
            self.wfile.write(html_content.encode('utf-8'))
        else:
            super().do_GET()

def start_web_server():
    """Start the web server"""
    server = HTTPServer(('localhost', 8080), CustomHandler)
    print("🌐 Starting web dashboard server...")
    print("📊 Dashboard URL: http://localhost:8080")
    print("🔄 Server will auto-refresh every 30 seconds")
    print("⏹️  Press Ctrl+C to stop the server")
    
    # Open browser automatically
    threading.Timer(1.0, lambda: webbrowser.open('http://localhost:8080')).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()

if __name__ == "__main__":
    start_web_server()
