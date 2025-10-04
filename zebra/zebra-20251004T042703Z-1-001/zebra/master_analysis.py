#!/usr/bin/env python3
"""
Master Analysis Runner for Project Sentinel
===========================================

This script runs all individual data analysis modules and generates:
- Combined event detection results
- Cross-correlation analysis between data sources
- Final events.jsonl output for submission
- Comprehensive fraud detection report

Usage: python master_analysis.py
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List

# Import all analysis modules
try:
    from analysis_inventory_snapshots import generate_inventory_analysis_report
    from analysis_pos_transactions import generate_pos_analysis_report
    from analysis_product_recognition import generate_recognition_analysis_report
    from analysis_queue_monitoring import generate_queue_analysis_report
    from analysis_rfid_readings import generate_rfid_analysis_report
except ImportError as e:
    print(f"Warning: Could not import analysis module: {e}")
    print("Make sure all analysis files are in the same directory.")

# @algorithm CrossCorrelationAnalysis | Correlates events across different data sources
class CrossCorrelationAnalyzer:
    def __init__(self, time_window_seconds: int = 300):
        """
        Initialize cross-correlation analyzer
        
        Args:
            time_window_seconds: Time window for correlating events (default 5 minutes)
        """
        self.time_window = time_window_seconds
        
    def correlate_events(self, all_reports: Dict) -> List[Dict]:
        """
        Correlate suspicious events across different data sources
        
        Args:
            all_reports: Dictionary containing all analysis reports
            
        Returns:
            List of correlated suspicious events
        """
        correlated_events = []
        
        # Extract events from all reports
        inventory_events = all_reports.get('inventory', {}).get('shrinkage_events', [])
        pos_events = all_reports.get('pos', {}).get('weight_discrepancies', [])
        recognition_events = all_reports.get('recognition', {}).get('low_confidence_events', [])
        queue_events = all_reports.get('queue', {}).get('dwell_time_anomalies', [])
        
        # Cross-correlate POS discrepancies with recognition issues
        for pos_event in pos_events:
            pos_time = datetime.fromisoformat(pos_event['timestamp'])
            pos_station = pos_event['station_id']
            
            # Look for recognition issues around the same time/station
            for recog_event in recognition_events:
                recog_time = datetime.fromisoformat(recog_event['timestamp'])
                recog_station = recog_event['station_id']
                
                time_diff = abs((pos_time - recog_time).total_seconds())
                
                if (pos_station == recog_station and time_diff <= self.time_window):
                    correlated_events.append({
                        'event_type': 'CORRELATED_FRAUD_ATTEMPT',
                        'timestamp': pos_event['timestamp'],
                        'station_id': pos_station,
                        'confidence': 'HIGH',
                        'description': f"Weight discrepancy combined with low recognition confidence",
                        'evidence': {
                            'pos_issue': {
                                'product': pos_event['product_name'],
                                'weight_discrepancy_pct': pos_event['weight_difference_pct'],
                                'customer_id': pos_event['customer_id']
                            },
                            'recognition_issue': {
                                'predicted_product': recog_event['predicted_product'],
                                'confidence': recog_event['confidence']
                            }
                        },
                        'fraud_indicators': ['weight_manipulation', 'barcode_switching', 'product_substitution']
                    })
        
        # Cross-correlate queue anomalies with other events
        for queue_event in queue_events:
            if queue_event['anomaly_type'] == 'HIGH_DWELL_TIME':
                queue_time = datetime.fromisoformat(queue_event['timestamp'])
                queue_station = queue_event['station_id']
                
                # Look for related POS or recognition issues
                related_issues = []
                
                for pos_event in pos_events:
                    pos_time = datetime.fromisoformat(pos_event['timestamp'])
                    if (pos_event['station_id'] == queue_station and 
                        abs((queue_time - pos_time).total_seconds()) <= self.time_window):
                        related_issues.append(('pos_discrepancy', pos_event))
                
                for recog_event in recognition_events:
                    recog_time = datetime.fromisoformat(recog_event['timestamp'])
                    if (recog_event['station_id'] == queue_station and 
                        abs((queue_time - recog_time).total_seconds()) <= self.time_window):
                        related_issues.append(('recognition_issue', recog_event))
                
                if related_issues:
                    correlated_events.append({
                        'event_type': 'CUSTOMER_DIFFICULTY_WITH_FRAUD',
                        'timestamp': queue_event['timestamp'],
                        'station_id': queue_station,
                        'confidence': 'MEDIUM',
                        'description': f"Extended dwell time ({queue_event['dwell_time']:.1f}s) with technical issues",
                        'evidence': {
                            'dwell_time': queue_event['dwell_time'],
                            'customer_count': queue_event['customer_count'],
                            'related_issues': related_issues
                        },
                        'fraud_indicators': ['checkout_difficulty', 'potential_fraud_complexity']
                    })
        
        return correlated_events

# @algorithm FraudSeverityScoring | Assigns severity scores to detected events
class FraudSeverityScorer:
    def __init__(self):
        """Initialize fraud severity scorer"""
        self.severity_weights = {
            'weight_discrepancy': 0.3,
            'recognition_confidence': 0.25,
            'dwell_time': 0.2,
            'inventory_shrinkage': 0.15,
            'cross_correlation': 0.1
        }
        
    def calculate_severity_score(self, event: Dict) -> float:
        """
        Calculate a severity score for a fraud event (0.0 to 1.0)
        
        Args:
            event: Event dictionary with fraud indicators
            
        Returns:
            Severity score between 0.0 and 1.0
        """
        score = 0.0
        
        # Weight discrepancy scoring
        if 'weight_difference_pct' in event.get('evidence', {}):
            weight_pct = event['evidence']['weight_difference_pct']
            weight_score = min(weight_pct / 100, 1.0)  # Normalize to 0-1
            score += weight_score * self.severity_weights['weight_discrepancy']
        
        # Recognition confidence scoring (inverse - lower confidence = higher severity)
        if 'confidence' in event.get('evidence', {}):
            confidence = event['evidence']['confidence']
            confidence_score = 1.0 - confidence  # Invert so low confidence = high score
            score += confidence_score * self.severity_weights['recognition_confidence']
        
        # Cross-correlation bonus
        if event.get('event_type') in ['CORRELATED_FRAUD_ATTEMPT', 'CUSTOMER_DIFFICULTY_WITH_FRAUD']:
            score += self.severity_weights['cross_correlation']
        
        # Ensure score doesn't exceed 1.0
        return min(score, 1.0)

def generate_events_jsonl(all_reports: Dict, correlator: CrossCorrelationAnalyzer, scorer: FraudSeverityScorer) -> List[Dict]:
    """
    Generate final events in the format expected for submission
    
    Args:
        all_reports: All analysis reports
        correlator: Cross-correlation analyzer
        scorer: Fraud severity scorer
        
    Returns:
        List of events for events.jsonl output
    """
    events = []
    
    # Process inventory shrinkage events
    if 'inventory' in all_reports:
        for shrinkage in all_reports['inventory'].get('shrinkage_events', []):
            event = {
                'timestamp': shrinkage['timestamp'],
                'event_type': 'INVENTORY_SHRINKAGE',
                'location': 'STORE_FLOOR',  # Inventory is store-wide
                'severity': shrinkage['severity'].lower(),
                'confidence': 0.8,
                'description': f"Inventory decrease of {shrinkage['decrease_percentage']:.1f}% for {shrinkage['product']}",
                'metadata': {
                    'product_sku': shrinkage['product'],
                    'quantity_change': shrinkage['current_qty'] - shrinkage['previous_qty'],
                    'percentage_decrease': shrinkage['decrease_percentage']
                }
            }
            events.append(event)
    
    # Process POS transaction anomalies
    if 'pos' in all_reports:
        for weight_disc in all_reports['pos'].get('weight_discrepancies', []):
            event = {
                'timestamp': weight_disc['timestamp'],
                'event_type': 'WEIGHT_DISCREPANCY',
                'location': weight_disc['station_id'],
                'severity': weight_disc['severity'].lower(),
                'confidence': 0.85,
                'description': f"Weight discrepancy of {weight_disc['weight_difference_pct']:.1f}% for {weight_disc['product_name']}",
                'metadata': {
                    'customer_id': weight_disc['customer_id'],
                    'product_sku': weight_disc['sku'],
                    'expected_weight': weight_disc['expected_weight'],
                    'actual_weight': weight_disc['actual_weight'],
                    'price': weight_disc['price']
                }
            }
            events.append(event)
        
        for barcode_event in all_reports['pos'].get('suspected_barcode_swapping', []):
            event = {
                'timestamp': barcode_event['timestamp'],
                'event_type': 'BARCODE_SWITCHING',
                'location': barcode_event['station_id'],
                'severity': 'high',
                'confidence': 0.75,
                'description': f"Suspected barcode switching - unusually low price per weight",
                'metadata': {
                    'customer_id': barcode_event['customer_id'],
                    'product_sku': barcode_event['sku'],
                    'price_ratio': barcode_event['price_ratio']
                }
            }
            events.append(event)
    
    # Process recognition anomalies
    if 'recognition' in all_reports:
        for low_conf in all_reports['recognition'].get('low_confidence_events', []):
            if low_conf['severity'] == 'HIGH':  # Only high severity recognition issues
                event = {
                    'timestamp': low_conf['timestamp'],
                    'event_type': 'SCANNER_AVOIDANCE',
                    'location': low_conf['station_id'],
                    'severity': 'medium',
                    'confidence': 0.6,
                    'description': f"Very low product recognition confidence ({low_conf['confidence']:.2f})",
                    'metadata': {
                        'predicted_product': low_conf['predicted_product'],
                        'recognition_confidence': low_conf['confidence']
                    }
                }
                events.append(event)
    
    # Process queue monitoring anomalies
    if 'queue' in all_reports:
        for dwell_anomaly in all_reports['queue'].get('dwell_time_anomalies', []):
            if dwell_anomaly['severity'] == 'HIGH':  # Only high severity dwell issues
                event = {
                    'timestamp': dwell_anomaly['timestamp'],
                    'event_type': 'CHECKOUT_DIFFICULTY',
                    'location': dwell_anomaly['station_id'],
                    'severity': 'medium',
                    'confidence': 0.5,
                    'description': f"Unusually {dwell_anomaly['anomaly_type'].lower().replace('_', ' ')}: {dwell_anomaly['dwell_time']:.1f}s",
                    'metadata': {
                        'dwell_time': dwell_anomaly['dwell_time'],
                        'customer_count': dwell_anomaly['customer_count'],
                        'anomaly_type': dwell_anomaly['anomaly_type']
                    }
                }
                events.append(event)
    
    # Add correlated events
    correlated_events = correlator.correlate_events(all_reports)
    for corr_event in correlated_events:
        severity_score = scorer.calculate_severity_score(corr_event)
        
        event = {
            'timestamp': corr_event['timestamp'],
            'event_type': corr_event['event_type'],
            'location': corr_event['station_id'],
            'severity': 'high' if severity_score > 0.7 else 'medium',
            'confidence': 0.9 if corr_event['confidence'] == 'HIGH' else 0.7,
            'description': corr_event['description'],
            'metadata': corr_event['evidence']
        }
        events.append(event)
    
    # Sort events by timestamp
    events.sort(key=lambda x: x['timestamp'])
    
    return events

def run_all_analyses() -> Dict:
    """Run all individual analysis modules and collect results"""
    reports = {}
    base_path = "data/input"
    
    print("="*60)
    print("RUNNING PROJECT SENTINEL ANALYSIS")
    print("="*60)
    
    # Run inventory analysis
    try:
        print("\n1. Running Inventory Analysis...")
        inventory_report = generate_inventory_analysis_report(f"{base_path}/inventory_snapshots.jsonl")
        reports['inventory'] = inventory_report
        print(f"   ✓ Found {len(inventory_report.get('shrinkage_events', []))} shrinkage events")
    except Exception as e:
        print(f"   ✗ Inventory analysis failed: {e}")
    
    # Run POS analysis
    try:
        print("\n2. Running POS Transaction Analysis...")
        pos_report = generate_pos_analysis_report(f"{base_path}/pos_transactions.jsonl")
        reports['pos'] = pos_report
        print(f"   ✓ Found {len(pos_report.get('weight_discrepancies', []))} weight discrepancies")
        print(f"   ✓ Found {len(pos_report.get('suspected_barcode_swapping', []))} suspected barcode swapping incidents")
    except Exception as e:
        print(f"   ✗ POS analysis failed: {e}")
    
    # Run recognition analysis
    try:
        print("\n3. Running Product Recognition Analysis...")
        recognition_report = generate_recognition_analysis_report(f"{base_path}/product_recognition.jsonl")
        reports['recognition'] = recognition_report
        print(f"   ✓ Found {len(recognition_report.get('low_confidence_events', []))} low confidence events")
    except Exception as e:
        print(f"   ✗ Recognition analysis failed: {e}")
    
    # Run queue analysis
    try:
        print("\n4. Running Queue Monitoring Analysis...")
        queue_report = generate_queue_analysis_report(f"{base_path}/queue_monitoring.jsonl")
        reports['queue'] = queue_report
        print(f"   ✓ Found {len(queue_report.get('dwell_time_anomalies', []))} dwell time anomalies")
    except Exception as e:
        print(f"   ✗ Queue analysis failed: {e}")
    
    # Run RFID analysis
    try:
        print("\n5. Running RFID Analysis...")
        rfid_report = generate_rfid_analysis_report(f"{base_path}/rfid_readings.jsonl")
        reports['rfid'] = rfid_report
        print(f"   ✓ RFID detection rate: {rfid_report['summary']['rfid_detection_rate']:.1%}")
        print(f"   ✓ Found {rfid_report['summary']['security_incidents']} security incidents")
    except Exception as e:
        print(f"   ✗ RFID analysis failed: {e}")
    
    return reports

def main():
    """Main execution function"""
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # Run all analyses
    all_reports = run_all_analyses()
    
    # Cross-correlation analysis
    print("\n6. Running Cross-Correlation Analysis...")
    correlator = CrossCorrelationAnalyzer(time_window_seconds=300)  # 5 minute window
    scorer = FraudSeverityScorer()
    
    # Generate final events
    print("\n7. Generating Final Events...")
    events = generate_events_jsonl(all_reports, correlator, scorer)
    
    # Save events.jsonl for submission
    with open("output/events.jsonl", "w") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")
    
    # Generate master report
    master_report = {
        'analysis_timestamp': datetime.now().isoformat(),
        'project': 'Project Sentinel - Retail Fraud Detection',
        'individual_reports': all_reports,
        'final_events': events,
        'summary': {
            'total_events_detected': len(events),
            'high_severity_events': len([e for e in events if e['severity'] == 'high']),
            'event_types': list(set(e['event_type'] for e in events)),
            'locations_affected': list(set(e['location'] for e in events if e['location'] != 'STORE_FLOOR')),
            'analysis_modules_run': list(all_reports.keys())
        }
    }
    
    # Save master report
    with open("reports/master_analysis_report.json", "w") as f:
        json.dump(master_report, f, indent=2)
    
    # Print final summary
    print("\n" + "="*60)
    print("PROJECT SENTINEL ANALYSIS COMPLETE")
    print("="*60)
    print(f"Total Events Detected: {len(events)}")
    print(f"High Severity Events: {len([e for e in events if e['severity'] == 'high'])}")
    print(f"Medium Severity Events: {len([e for e in events if e['severity'] == 'medium'])}")
    
    print(f"\nEvent Types Detected:")
    event_type_counts = {}
    for event in events:
        event_type_counts[event['event_type']] = event_type_counts.get(event['event_type'], 0) + 1
    
    for event_type, count in sorted(event_type_counts.items()):
        print(f"  - {event_type}: {count}")
    
    print(f"\nFiles Generated:")
    print(f"  - output/events.jsonl (for submission)")
    print(f"  - reports/master_analysis_report.json (detailed analysis)")
    
    for module in all_reports.keys():
        print(f"  - {module}_analysis_report.json (individual module)")
    
    print(f"\n✓ Analysis complete! Check the output/ directory for submission files.")

if __name__ == "__main__":
    main()
