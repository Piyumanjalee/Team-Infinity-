#!/usr/bin/env python3
"""
Project Sentinel - Modern Dark Theme Dashboard
===========================================
Advanced retail fraud detection system with manual data entry
"""

import json
import webbrowser
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import os
import urllib.parse
import subprocess

class ModernDashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path.startswith('/?'):
            self.serve_main_dashboard()
        elif self.path == '/manual-entry':
            self.serve_manual_entry()
        elif self.path == '/api/analyze':
            self.run_analysis_api()
        elif self.path == '/api/manual-analyze':
            self.run_manual_analysis()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/api/save-manual':
            self.save_manual_data()
        else:
            self.send_error(404)

    def serve_main_dashboard(self):
        """Serve the modern main dashboard"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html_content = self.generate_modern_dashboard()
        self.wfile.write(html_content.encode('utf-8'))

    def serve_manual_entry(self):
        """Serve manual data entry page"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html_content = self.generate_manual_entry_page()
        self.wfile.write(html_content.encode('utf-8'))

    def save_manual_data(self):
        """Save manually entered data"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            # Create manual data directory
            os.makedirs("data/manual", exist_ok=True)
            
            # Save each data type to separate files
            for data_type, content in data.items():
                if content.strip():
                    filename = f"data/manual/{data_type}.jsonl"
                    with open(filename, 'w') as f:
                        f.write(content)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "message": "Data saved successfully"}).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))

    def run_analysis_api(self):
        """Run analysis on original dataset"""
        try:
            result = subprocess.run(['python', 'enhanced_master_analysis.py'], 
                                  capture_output=True, text=True, cwd='.')
            
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

    def run_manual_analysis(self):
        """Run analysis on manually entered data"""
        try:
            result = subprocess.run(['python', 'manual_data_analysis.py'], 
                                  capture_output=True, text=True, cwd='.')
            
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

    def generate_modern_dashboard(self):
        """Generate modern dark theme dashboard"""
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

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Sentinel - Advanced Fraud Detection</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background: #0a0a0a;
            color: #ffffff;
            overflow-x: hidden;
            min-height: 100vh;
        }}
        
        .bg-pattern {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 40% 80%, rgba(120, 219, 226, 0.3) 0%, transparent 50%);
            z-index: -1;
        }}
        
        .navbar {{
            background: rgba(15, 15, 15, 0.9);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 1000;
        }}
        
        .nav-container {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 2rem;
        }}
        
        .logo {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .logo-icon {{
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
        }}
        
        .logo-text {{
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .nav-actions {{
            display: flex;
            gap: 1rem;
        }}
        
        .btn {{
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-family: inherit;
            font-size: 0.9rem;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4);
        }}
        
        .btn-secondary {{
            background: rgba(255, 255, 255, 0.05);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .btn-secondary:hover {{
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-2px);
        }}
        
        .btn-success {{
            background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
            color: white;
        }}
        
        .btn-success:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(86, 171, 47, 0.4);
        }}
        
        .btn-warning {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }}
        
        .btn-warning:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(240, 147, 251, 0.4);
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .hero-section {{
            text-align: center;
            margin: 3rem 0;
        }}
        
        .hero-title {{
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .hero-subtitle {{
            font-size: 1.25rem;
            color: #a0a0a0;
            margin-bottom: 2rem;
        }}
        
        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(86, 171, 47, 0.1);
            border: 1px solid rgba(86, 171, 47, 0.3);
            padding: 0.5rem 1rem;
            border-radius: 50px;
            color: #56ab2f;
            font-weight: 600;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
            margin: 3rem 0;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 2rem;
            backdrop-filter: blur(20px);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(255, 255, 255, 0.2);
        }}
        
        .stat-icon {{
            width: 60px;
            height: 60px;
            background: rgba(102, 126, 234, 0.1);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            margin-bottom: 1.5rem;
            color: #667eea;
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            color: #ffffff;
        }}
        
        .stat-label {{
            color: #a0a0a0;
            font-weight: 500;
        }}
        
        .data-sources-section {{
            margin: 4rem 0;
        }}
        
        .section-title {{
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 2rem;
            text-align: center;
        }}
        
        .sources-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
        }}
        
        .source-card {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
        }}
        
        .source-card:hover {{
            transform: translateY(-3px);
            background: rgba(255, 255, 255, 0.05);
        }}
        
        .source-status {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 0.5rem;
        }}
        
        .status-active {{ background: #56ab2f; }}
        .status-uploaded {{ background: #667eea; }}
        .status-missing {{ background: #f5576c; }}
        
        .alerts-section {{
            margin: 4rem 0;
        }}
        
        .alert-card {{
            background: rgba(245, 87, 108, 0.1);
            border: 1px solid rgba(245, 87, 108, 0.2);
            border-left: 4px solid #f5576c;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }}
        
        .alert-card:hover {{
            background: rgba(245, 87, 108, 0.15);
            transform: translateX(5px);
        }}
        
        .alert-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}
        
        .alert-title {{
            font-weight: 600;
            font-size: 1.1rem;
        }}
        
        .severity-badge {{
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            background: #f5576c;
            color: white;
        }}
        
        .alert-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            font-size: 0.9rem;
            color: #a0a0a0;
        }}
        
        .loading-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 2000;
        }}
        
        .loading-content {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 3rem;
            text-align: center;
            backdrop-filter: blur(20px);
        }}
        
        .spinner {{
            width: 60px;
            height: 60px;
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1.5rem;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .notification {{
            position: fixed;
            top: 100px;
            right: 2rem;
            background: rgba(86, 171, 47, 0.9);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            backdrop-filter: blur(20px);
            transform: translateX(400px);
            transition: transform 0.3s ease;
            z-index: 1500;
        }}
        
        .notification.show {{
            transform: translateX(0);
        }}
        
        .notification.error {{
            background: rgba(245, 87, 108, 0.9);
        }}
        
        @media (max-width: 768px) {{
            .hero-title {{
                font-size: 2.5rem;
            }}
            
            .nav-container {{
                padding: 0 1rem;
            }}
            
            .container {{
                padding: 1rem;
            }}
            
            .nav-actions {{
                flex-direction: column;
                gap: 0.5rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="bg-pattern"></div>
    
    <nav class="navbar">
        <div class="nav-container">
            <div class="logo">
                <div class="logo-icon">🛡️</div>
                <div class="logo-text">PROJECT SENTINEL</div>
            </div>
            <div class="nav-actions">
                <button onclick="runOriginalAnalysis()" class="btn btn-primary">
                    <i class="fas fa-play"></i> Analyze Dataset
                </button>
                <a href="/manual-entry" class="btn btn-success">
                    <i class="fas fa-keyboard"></i> Manual Entry
                </a>
                <button onclick="location.reload()" class="btn btn-secondary">
                    <i class="fas fa-refresh"></i> Refresh
                </button>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="hero-section">
            <h1 class="hero-title">Advanced Fraud Detection</h1>
            <p class="hero-subtitle">Real-time retail security monitoring with AI-powered analytics</p>
            <div class="status-badge">
                <i class="fas fa-circle"></i>
                System Operational
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <div class="stat-value">{total_events}</div>
                <div class="stat-label">Fraud Events Detected</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-box"></i>
                </div>
                <div class="stat-value">{products_affected}</div>
                <div class="stat-label">Products Affected</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-chart-line"></i>
                </div>
                <div class="stat-value">{initial_inv:,}</div>
                <div class="stat-label">Initial Inventory</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-percentage"></i>
                </div>
                <div class="stat-value">{shrinkage_rate:.1f}%</div>
                <div class="stat-label">Shrinkage Rate</div>
            </div>
        </div>

        <div class="data-sources-section">
            <h2 class="section-title">Data Sources Status</h2>
            <div class="sources-grid">
                {self.generate_modern_sources()}
            </div>
        </div>

        <div class="alerts-section">
            <h2 class="section-title">Critical Fraud Alerts</h2>
            {self.generate_modern_alerts(sorted_events)}
        </div>
    </div>

    <div class="loading-overlay" id="loadingOverlay">
        <div class="loading-content">
            <div class="spinner"></div>
            <h3>Analyzing Data...</h3>
            <p>Processing fraud detection algorithms</p>
        </div>
    </div>

    <div class="notification" id="notification">
        <i class="fas fa-check-circle"></i>
        <span id="notificationText">Operation completed</span>
    </div>

    <script>
        function showNotification(message, isError = false) {{
            const notification = document.getElementById('notification');
            const text = document.getElementById('notificationText');
            
            text.textContent = message;
            notification.className = 'notification' + (isError ? ' error' : '');
            notification.classList.add('show');
            
            setTimeout(() => {{
                notification.classList.remove('show');
            }}, 4000);
        }}

        function showLoading() {{
            document.getElementById('loadingOverlay').style.display = 'flex';
        }}

        function hideLoading() {{
            document.getElementById('loadingOverlay').style.display = 'none';
        }}

        function runOriginalAnalysis() {{
            showLoading();
            
            fetch('/api/analyze')
            .then(response => response.json())
            .then(data => {{
                hideLoading();
                if (data.success) {{
                    showNotification('✅ Analysis completed successfully!');
                    setTimeout(() => location.reload(), 2000);
                }} else {{
                    showNotification('❌ Analysis failed: ' + (data.error || 'Unknown error'), true);
                }}
            }})
            .catch(error => {{
                hideLoading();
                showNotification('❌ Error: ' + error.message, true);
            }});
        }}

        // Auto-refresh every 2 minutes
        setInterval(() => {{
            location.reload();
        }}, 120000);
    </script>
</body>
</html>
"""

    def generate_modern_sources(self):
        """Generate modern data source status"""
        sources = [
            ("inventory_snapshots.jsonl", "📦 Inventory", "Inventory tracking data"),
            ("pos_transactions.jsonl", "🛒 POS Systems", "Transaction records"),
            ("product_recognition.jsonl", "📱 Recognition", "AI confidence scores"),
            ("queue_monitoring.jsonl", "👥 Queue Data", "Customer behavior"),
            ("rfid_readings.jsonl", "📡 RFID Tags", "Security tracking")
        ]
        
        html = ""
        for filename, display_name, description in sources:
            # Check data sources
            original_path = f"data/input/{filename}"
            manual_path = f"data/manual/{filename}"
            
            if os.path.exists(manual_path):
                status_class = "status-uploaded"
                status_text = "Manual Data"
            elif os.path.exists(original_path):
                status_class = "status-active"
                status_text = "Dataset Active"
            else:
                status_class = "status-missing"
                status_text = "No Data"
            
            html += f"""
            <div class="source-card">
                <h4>{display_name}</h4>
                <p style="color: #a0a0a0; font-size: 0.9rem; margin: 0.5rem 0;">{description}</p>
                <div>
                    <span class="source-status {status_class}"></span>
                    <span style="font-size: 0.85rem; font-weight: 500;">{status_text}</span>
                </div>
            </div>
            """
        
        return html

    def generate_modern_alerts(self, events):
        """Generate modern fraud alerts"""
        if not events:
            return """
            <div class="alert-card" style="text-align: center; border-left-color: #56ab2f; background: rgba(86, 171, 47, 0.1);">
                <h4 style="color: #56ab2f;">No Critical Alerts</h4>
                <p style="color: #a0a0a0;">System monitoring - no fraud detected</p>
            </div>
            """
        
        html = ""
        for i, event in enumerate(events[:5], 1):
            html += f"""
            <div class="alert-card">
                <div class="alert-header">
                    <div class="alert-title">
                        <i class="fas fa-exclamation-triangle"></i>
                        Alert #{i}: {event.get('product', 'Unknown Product')}
                    </div>
                    <div class="severity-badge">{event.get('severity', 'MEDIUM')}</div>
                </div>
                <div class="alert-details">
                    <div>
                        <strong>Timestamp:</strong><br>
                        {event.get('timestamp', 'N/A')}
                    </div>
                    <div>
                        <strong>Loss Rate:</strong><br>
                        {event.get('decrease_percentage', 0):.1f}% decrease
                    </div>
                    <div>
                        <strong>Quantity Change:</strong><br>
                        {event.get('previous_qty', 0)} → {event.get('current_qty', 0)} items
                    </div>
                </div>
            </div>
            """
        
        return html

    def generate_manual_entry_page(self):
        """Generate modern manual data entry page"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manual Data Entry - Project Sentinel</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: #0a0a0a;
            color: #ffffff;
            min-height: 100vh;
        }
        
        .bg-pattern {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 40% 80%, rgba(120, 219, 226, 0.3) 0%, transparent 50%);
            z-index: -1;
        }
        
        .navbar {
            background: rgba(15, 15, 15, 0.9);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding: 1rem 0;
        }
        
        .nav-container {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 2rem;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 1rem;
            text-decoration: none;
            color: inherit;
        }
        
        .logo-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
        }
        
        .logo-text {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-family: inherit;
            font-size: 0.9rem;
        }
        
        .btn-secondary {
            background: rgba(255, 255, 255, 0.05);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-2px);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .page-header {
            text-align: center;
            margin: 2rem 0 4rem;
        }
        
        .page-title {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .page-subtitle {
            font-size: 1.25rem;
            color: #a0a0a0;
        }
        
        .entry-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .entry-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 2rem;
            backdrop-filter: blur(20px);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .card-icon {
            width: 50px;
            height: 50px;
            background: rgba(102, 126, 234, 0.1);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: #667eea;
        }
        
        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
        }
        
        .card-description {
            color: #a0a0a0;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }
        
        .data-textarea {
            width: 100%;
            min-height: 200px;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1rem;
            color: white;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            resize: vertical;
            outline: none;
            transition: border-color 0.3s ease;
        }
        
        .data-textarea:focus {
            border-color: #667eea;
        }
        
        .data-textarea::placeholder {
            color: #666;
        }
        
        .action-section {
            text-align: center;
            margin: 3rem 0;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            font-size: 1.1rem;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
            color: white;
            margin-left: 1rem;
        }
        
        .btn-success:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(86, 171, 47, 0.4);
        }
        
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 2000;
        }
        
        .loading-content {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 3rem;
            text-align: center;
            backdrop-filter: blur(20px);
        }
        
        .spinner {
            width: 60px;
            height: 60px;
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1.5rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .notification {
            position: fixed;
            top: 100px;
            right: 2rem;
            background: rgba(86, 171, 47, 0.9);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            backdrop-filter: blur(20px);
            transform: translateX(400px);
            transition: transform 0.3s ease;
            z-index: 1500;
        }
        
        .notification.show {
            transform: translateX(0);
        }
        
        .notification.error {
            background: rgba(245, 87, 108, 0.9);
        }
    </style>
</head>
<body>
    <div class="bg-pattern"></div>
    
    <nav class="navbar">
        <div class="nav-container">
            <a href="/" class="logo">
                <div class="logo-icon">🛡️</div>
                <div class="logo-text">PROJECT SENTINEL</div>
            </a>
            <div>
                <a href="/" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Back to Dashboard
                </a>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="page-header">
            <h1 class="page-title">Manual Data Entry</h1>
            <p class="page-subtitle">Enter your fraud detection data in JSONL format</p>
        </div>

        <div class="entry-grid">
            <div class="entry-card">
                <div class="card-header">
                    <div class="card-icon">📦</div>
                    <div>
                        <div class="card-title">Inventory Snapshots</div>
                        <div class="card-description">Inventory level data over time</div>
                    </div>
                </div>
                <textarea 
                    id="inventoryData" 
                    class="data-textarea" 
                    placeholder='{"timestamp": "2025-10-04T10:00:00", "data": {"PRD_F_01": 100, "PRD_F_02": 80, "PRD_F_03": 120}}'
                ></textarea>
            </div>

            <div class="entry-card">
                <div class="card-header">
                    <div class="card-icon">🛒</div>
                    <div>
                        <div class="card-title">POS Transactions</div>
                        <div class="card-description">Point-of-sale transaction records</div>
                    </div>
                </div>
                <textarea 
                    id="posData" 
                    class="data-textarea" 
                    placeholder='{"timestamp": "2025-10-04T10:05:00", "station_id": "SCC1", "data": {"customer_id": "C001", "sku": "PRD_F_01", "price": 540.0, "weight_g": 400.0}}'
                ></textarea>
            </div>

            <div class="entry-card">
                <div class="card-header">
                    <div class="card-icon">📱</div>
                    <div>
                        <div class="card-title">Product Recognition</div>
                        <div class="card-description">AI confidence scores for product identification</div>
                    </div>
                </div>
                <textarea 
                    id="recognitionData" 
                    class="data-textarea" 
                    placeholder='{"timestamp": "2025-10-04T10:05:00", "station_id": "SCC1", "data": {"predicted_product": "PRD_F_01", "accuracy": 0.89}}'
                ></textarea>
            </div>

            <div class="entry-card">
                <div class="card-header">
                    <div class="card-icon">👥</div>
                    <div>
                        <div class="card-title">Queue Monitoring</div>
                        <div class="card-description">Customer behavior and dwell time data</div>
                    </div>
                </div>
                <textarea 
                    id="queueData" 
                    class="data-textarea" 
                    placeholder='{"timestamp": "2025-10-04T10:00:00", "station_id": "SCC1", "data": {"customer_count": 3, "average_dwell_time": 120.5}}'
                ></textarea>
            </div>
        </div>

        <div class="action-section">
            <button onclick="saveData()" class="btn btn-primary">
                <i class="fas fa-save"></i> Save Data
            </button>
            <button onclick="analyzeManualData()" class="btn btn-success">
                <i class="fas fa-play"></i> Analyze Now
            </button>
        </div>
    </div>

    <div class="loading-overlay" id="loadingOverlay">
        <div class="loading-content">
            <div class="spinner"></div>
            <h3>Processing Data...</h3>
            <p>Analyzing fraud patterns in your data</p>
        </div>
    </div>

    <div class="notification" id="notification">
        <i class="fas fa-check-circle"></i>
        <span id="notificationText">Operation completed</span>
    </div>

    <script>
        function showNotification(message, isError = false) {
            const notification = document.getElementById('notification');
            const text = document.getElementById('notificationText');
            
            text.textContent = message;
            notification.className = 'notification' + (isError ? ' error' : '');
            notification.classList.add('show');
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 4000);
        }

        function showLoading() {
            document.getElementById('loadingOverlay').style.display = 'flex';
        }

        function hideLoading() {
            document.getElementById('loadingOverlay').style.display = 'none';
        }

        function saveData() {
            const data = {
                inventory_snapshots: document.getElementById('inventoryData').value.trim(),
                pos_transactions: document.getElementById('posData').value.trim(),
                product_recognition: document.getElementById('recognitionData').value.trim(),
                queue_monitoring: document.getElementById('queueData').value.trim()
            };

            if (!data.inventory_snapshots && !data.pos_transactions && !data.product_recognition && !data.queue_monitoring) {
                showNotification('⚠️ Please enter at least one type of data', true);
                return;
            }

            showLoading();

            fetch('/api/save-manual', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                hideLoading();
                if (data.success) {
                    showNotification('✅ Data saved successfully!');
                } else {
                    showNotification('❌ Failed to save data: ' + (data.error || 'Unknown error'), true);
                }
            })
            .catch(error => {
                hideLoading();
                showNotification('❌ Error: ' + error.message, true);
            });
        }

        function analyzeManualData() {
            showLoading();

            fetch('/api/manual-analyze')
            .then(response => response.json())
            .then(data => {
                hideLoading();
                if (data.success) {
                    showNotification('✅ Analysis completed! Redirecting to dashboard...');
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 2000);
                } else {
                    showNotification('❌ Analysis failed: ' + (data.error || 'Unknown error'), true);
                }
            })
            .catch(error => {
                hideLoading();
                showNotification('❌ Error: ' + error.message, true);
            });
        }
    </script>
</body>
</html>
"""

def start_modern_server():
    """Start the modern dashboard server"""
    server = HTTPServer(('localhost', 8080), ModernDashboardHandler)
    print("🚀 Starting Modern Project Sentinel Dashboard...")
    print("📊 Main Dashboard: http://localhost:8080")
    print("✏️  Manual Entry: http://localhost:8080/manual-entry")
    print("🎨 Modern dark theme with advanced features")
    print("⏹️  Press Ctrl+C to stop the server")
    
    # Open browser automatically
    threading.Timer(1.0, lambda: webbrowser.open('http://localhost:8080')).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()

if __name__ == "__main__":
    start_modern_server()
