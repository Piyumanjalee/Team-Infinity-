#!/usr/bin/env python3
"""
Inventory Snapshots Analysis
============================

This script analyzes inventory snapshot data to detect:
- Inventory shrinkage patterns
- Unusual product depletion rates  
- Potential theft or misplacement events
- Stock level anomalies

Data Format: JSONL with timestamp and product quantities
"""

import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple

# @algorithm InventoryShrinkageDetection | Detects abnormal inventory decreases indicating potential theft
class InventoryShrinkageDetector:
    def __init__(self, threshold_percentage: float = 5.0):
        """
        Initialize shrinkage detector
        
        Args:
            threshold_percentage: Minimum percentage decrease to flag as suspicious
        """
        self.threshold = threshold_percentage
        
    def detect_shrinkage_events(self, inventory_data: pd.DataFrame) -> List[Dict]:
        """
        Detect inventory shrinkage events
        
        Returns:
            List of shrinkage events with timestamp, product, and severity
        """
        events = []
        
        for product in inventory_data.columns:
            if product == 'timestamp':
                continue
                
            product_data = inventory_data[product].values
            for i in range(1, len(product_data)):
                if product_data[i-1] > 0:  # Avoid division by zero
                    decrease_pct = ((product_data[i-1] - product_data[i]) / product_data[i-1]) * 100
                    
                    if decrease_pct > self.threshold:
                        events.append({
                            'timestamp': inventory_data.iloc[i]['timestamp'].strftime('%Y-%m-%dT%H:%M:%S'),
                            'product': product,
                            'previous_qty': int(product_data[i-1]),
                            'current_qty': int(product_data[i]),
                            'decrease_percentage': float(decrease_pct),
                            'severity': 'HIGH' if decrease_pct > 10 else 'MEDIUM'
                        })
        
        return events

# @algorithm AnomalyDetection | Identifies statistical outliers in inventory patterns
class InventoryAnomalyDetector:
    def __init__(self, z_score_threshold: float = 2.0):
        """
        Initialize anomaly detector using Z-score method
        
        Args:
            z_score_threshold: Standard deviations from mean to consider anomalous
        """
        self.z_threshold = z_score_threshold
        
    def detect_anomalies(self, inventory_data: pd.DataFrame) -> List[Dict]:
        """
        Detect statistical anomalies in inventory levels
        
        Returns:
            List of anomaly events
        """
        anomalies = []
        
        for product in inventory_data.columns:
            if product == 'timestamp':
                continue
                
            product_values = inventory_data[product].values
            mean_val = np.mean(product_values)
            std_val = np.std(product_values)
            
            if std_val > 0:  # Avoid division by zero
                z_scores = np.abs((product_values - mean_val) / std_val)
                
                for i, z_score in enumerate(z_scores):
                    if z_score > self.z_threshold:
                        anomalies.append({
                            'timestamp': inventory_data.iloc[i]['timestamp'].strftime('%Y-%m-%dT%H:%M:%S'),
                            'product': product,
                            'quantity': int(product_values[i]),
                            'z_score': float(z_score),
                            'mean_quantity': float(mean_val),
                            'anomaly_type': 'LOW' if product_values[i] < mean_val else 'HIGH'
                        })
        
        return anomalies

def load_inventory_data(file_path: str) -> pd.DataFrame:
    """Load inventory snapshots from JSONL file"""
    data = []
    
    with open(file_path, 'r') as f:
        for line in f:
            record = json.loads(line.strip())
            # Flatten the data structure
            flat_record = {'timestamp': record['timestamp']}
            flat_record.update(record['data'])
            data.append(flat_record)
    
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df.sort_values('timestamp').reset_index(drop=True)

def analyze_inventory_trends(df: pd.DataFrame) -> Dict:
    """Analyze overall inventory trends"""
    analysis = {}
    
    # Calculate total inventory over time
    product_columns = [col for col in df.columns if col != 'timestamp']
    df['total_inventory'] = df[product_columns].sum(axis=1)
    
    # Trend analysis
    analysis['total_products'] = len(product_columns)
    analysis['time_range'] = {
        'start': df['timestamp'].min().strftime('%Y-%m-%dT%H:%M:%S'),
        'end': df['timestamp'].max().strftime('%Y-%m-%dT%H:%M:%S'),
        'duration_hours': (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600
    }
    
    analysis['inventory_summary'] = {
        'initial_total': int(df['total_inventory'].iloc[0]),
        'final_total': int(df['total_inventory'].iloc[-1]),
        'net_change': int(df['total_inventory'].iloc[-1] - df['total_inventory'].iloc[0]),
        'max_total': int(df['total_inventory'].max()),
        'min_total': int(df['total_inventory'].min())
    }
    
    # Product-level statistics
    analysis['product_statistics'] = {}
    for product in product_columns:
        product_data = df[product]
        analysis['product_statistics'][product] = {
            'initial_qty': int(product_data.iloc[0]),
            'final_qty': int(product_data.iloc[-1]),
            'net_change': int(product_data.iloc[-1] - product_data.iloc[0]),
            'max_qty': int(product_data.max()),
            'min_qty': int(product_data.min()),
            'avg_qty': float(product_data.mean()),
            'std_dev': float(product_data.std())
        }
    
    return analysis

def generate_inventory_report(file_path: str) -> Dict:
    """Generate comprehensive inventory analysis report"""
    print("Loading inventory data...")
    df = load_inventory_data(file_path)
    
    print("Analyzing inventory trends...")
    trends = analyze_inventory_trends(df)
    
    print("Detecting shrinkage events...")
    shrinkage_detector = InventoryShrinkageDetector(threshold_percentage=3.0)
    shrinkage_events = shrinkage_detector.detect_shrinkage_events(df)
    
    print("Detecting anomalies...")
    anomaly_detector = InventoryAnomalyDetector(z_score_threshold=2.0)
    anomaly_events = anomaly_detector.detect_anomalies(df)
    
    # Compile report
    report = {
        'analysis_timestamp': datetime.now().isoformat(),
        'data_source': file_path,
        'trends': trends,
        'shrinkage_events': shrinkage_events,
        'anomaly_events': anomaly_events,
        'summary': {
            'total_shrinkage_events': len(shrinkage_events),
            'total_anomaly_events': len(anomaly_events),
            'high_severity_shrinkage': len([e for e in shrinkage_events if e['severity'] == 'HIGH']),
            'products_with_issues': len(set([e['product'] for e in shrinkage_events + anomaly_events]))
        }
    }
    
    return report

def visualize_inventory_data(df: pd.DataFrame, output_dir: str = "plots"):
    """Generate visualization plots for inventory data"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Plot 1: Total inventory over time
    plt.figure(figsize=(12, 6))
    product_columns = [col for col in df.columns if col != 'timestamp']
    df['total_inventory'] = df[product_columns].sum(axis=1)
    plt.plot(df['timestamp'], df['total_inventory'], linewidth=2)
    plt.title('Total Inventory Over Time')
    plt.xlabel('Time')
    plt.ylabel('Total Quantity')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/total_inventory_trend.png")
    plt.close()
    
    # Plot 2: Top products with highest variance
    variances = {}
    for product in product_columns:
        variances[product] = df[product].var()
    
    top_variance = sorted(variances.items(), key=lambda x: x[1], reverse=True)[:10]
    
    plt.figure(figsize=(14, 8))
    for i, (product, _) in enumerate(top_variance):
        plt.subplot(2, 5, i + 1)
        plt.plot(df['timestamp'], df[product], linewidth=1)
        plt.title(f'{product}', fontsize=10)
        plt.xticks(rotation=45, fontsize=8)
        plt.yticks(fontsize=8)
    
    plt.suptitle('Top 10 Products by Inventory Variance')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/high_variance_products.png", dpi=150)
    plt.close()

if __name__ == "__main__":
    # File path to inventory snapshots
    inventory_file = "data/input/inventory_snapshots.jsonl"
    
    # Generate analysis report
    try:
        report = generate_inventory_report(inventory_file)
        
        # Save report to JSON
        with open("inventory_analysis_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*50)
        print("INVENTORY ANALYSIS SUMMARY")
        print("="*50)
        print(f"Analysis Period: {report['trends']['time_range']['start']} to {report['trends']['time_range']['end']}")
        print(f"Total Products: {report['trends']['total_products']}")
        print(f"Initial Inventory: {report['trends']['inventory_summary']['initial_total']:,}")
        print(f"Final Inventory: {report['trends']['inventory_summary']['final_total']:,}")
        print(f"Net Change: {report['trends']['inventory_summary']['net_change']:,}")
        print(f"\nShrinkage Events Detected: {report['summary']['total_shrinkage_events']}")
        print(f"High Severity Events: {report['summary']['high_severity_shrinkage']}")
        print(f"Anomaly Events: {report['summary']['total_anomaly_events']}")
        print(f"Products with Issues: {report['summary']['products_with_issues']}")
        
        # Show top shrinkage events
        if report['shrinkage_events']:
            print(f"\nTOP 5 SHRINKAGE EVENTS:")
            sorted_events = sorted(report['shrinkage_events'], 
                                 key=lambda x: x['decrease_percentage'], reverse=True)[:5]
            for i, event in enumerate(sorted_events, 1):
                print(f"{i}. {event['product']} at {event['timestamp']}: "
                      f"{event['decrease_percentage']:.1f}% decrease "
                      f"({event['previous_qty']} → {event['current_qty']})")
        
        print(f"\nDetailed report saved to: inventory_analysis_report.json")
        
        # Generate visualizations if data loaded successfully
        df = load_inventory_data(inventory_file)
        visualize_inventory_data(df)
        print("Visualization plots saved to: plots/")
        
    except FileNotFoundError:
        print(f"Error: Could not find inventory file at {inventory_file}")
        print("Please ensure the file path is correct.")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
