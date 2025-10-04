#!/usr/bin/env python3
"""
Simple Inventory Analysis (No Dependencies)
==========================================

This script analyzes inventory data without external dependencies.
"""

import json
import statistics
from datetime import datetime

def load_inventory_data(file_path):
    """Load inventory data from JSONL file"""
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            record = json.loads(line.strip())
            data.append(record)
    return data

def detect_shrinkage_events(data, threshold=3.0):
    """Detect inventory shrinkage events"""
    events = []
    
    if len(data) < 2:
        return events
    
    # Get all product keys from first record
    products = list(data[0]['data'].keys())
    
    for i in range(1, len(data)):
        prev_data = data[i-1]['data']
        curr_data = data[i]['data']
        
        for product in products:
            prev_qty = prev_data.get(product, 0)
            curr_qty = curr_data.get(product, 0)
            
            if prev_qty > 0:
                decrease_pct = ((prev_qty - curr_qty) / prev_qty) * 100
                
                if decrease_pct > threshold:
                    events.append({
                        'timestamp': data[i]['timestamp'],
                        'product': product,
                        'previous_qty': prev_qty,
                        'current_qty': curr_qty,
                        'decrease_percentage': decrease_pct,
                        'severity': 'HIGH' if decrease_pct > 10 else 'MEDIUM'
                    })
    
    return events

def analyze_inventory(file_path):
    """Main analysis function"""
    print("Loading inventory data...")
    data = load_inventory_data(file_path)
    
    print("Detecting shrinkage events...")
    shrinkage_events = detect_shrinkage_events(data, threshold=3.0)
    
    # Calculate basic statistics
    if data:
        products = list(data[0]['data'].keys())
        total_products = len(products)
        
        initial_inventory = sum(data[0]['data'].values())
        final_inventory = sum(data[-1]['data'].values())
        net_change = final_inventory - initial_inventory
        
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'data_source': file_path,
            'shrinkage_events': shrinkage_events,
            'summary': {
                'total_products': total_products,
                'initial_inventory': initial_inventory,
                'final_inventory': final_inventory,
                'net_change': net_change,
                'shrinkage_events_count': len(shrinkage_events),
                'high_severity_events': len([e for e in shrinkage_events if e['severity'] == 'HIGH'])
            }
        }
        
        return report
    
    return {'shrinkage_events': [], 'summary': {}}

if __name__ == "__main__":
    try:
        report = analyze_inventory("data/input/inventory_snapshots.jsonl")
        
        # Save report
        with open("inventory_simple_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print("\n" + "="*50)
        print("INVENTORY ANALYSIS SUMMARY")
        print("="*50)
        print(f"Initial Inventory: {report['summary'].get('initial_inventory', 0):,}")
        print(f"Final Inventory: {report['summary'].get('final_inventory', 0):,}")
        print(f"Net Change: {report['summary'].get('net_change', 0):,}")
        print(f"Shrinkage Events: {report['summary'].get('shrinkage_events_count', 0)}")
        print(f"High Severity Events: {report['summary'].get('high_severity_events', 0)}")
        
        if report['shrinkage_events']:
            print(f"\nTOP SHRINKAGE EVENTS:")
            sorted_events = sorted(report['shrinkage_events'], 
                                 key=lambda x: x['decrease_percentage'], reverse=True)[:5]
            for i, event in enumerate(sorted_events, 1):
                print(f"{i}. {event['product']} at {event['timestamp']}: "
                      f"{event['decrease_percentage']:.1f}% decrease")
        
        print("Report saved to: inventory_simple_report.json")
        
    except Exception as e:
        print(f"Error: {e}")
