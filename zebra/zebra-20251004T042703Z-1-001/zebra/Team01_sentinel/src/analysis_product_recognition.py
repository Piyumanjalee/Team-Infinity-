#!/usr/bin/env python3
"""
Product Recognition Analysis
============================

This script analyzes product recognition data to detect:
- Low confidence product predictions
- Misrecognition patterns that could indicate fraud
- Scanner avoidance (products not being scanned)
- Recognition accuracy trends over time
- Products frequently misidentified

Data Format: JSONL with product predictions and confidence scores
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Set
from collections import defaultdict, Counter
import statistics

# @algorithm LowConfidenceDetection | Identifies product recognitions with suspiciously low confidence
class LowConfidenceDetector:
    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize low confidence detector
        
        Args:
            confidence_threshold: Minimum acceptable confidence score (0.0 to 1.0)
        """
        self.threshold = confidence_threshold
        
    def detect_low_confidence_predictions(self, recognition_data: List[Dict]) -> List[Dict]:
        """
        Detect product recognition events with low confidence scores
        
        Returns:
            List of low confidence recognition events
        """
        low_confidence_events = []
        
        for record in recognition_data:
            if record['accuracy'] < self.threshold:
                low_confidence_events.append({
                    'timestamp': record['timestamp'],
                    'station_id': record['station_id'],
                    'predicted_product': record['predicted_product'],
                    'confidence': record['accuracy'],
                    'severity': 'HIGH' if record['accuracy'] < 0.5 else 'MEDIUM'
                })
        
        return low_confidence_events

# @algorithm ScannerAvoidanceDetection | Detects potential scanner avoidance patterns
class ScannerAvoidanceDetector:
    def __init__(self, time_gap_threshold: int = 60):
        """
        Initialize scanner avoidance detector
        
        Args:
            time_gap_threshold: Minimum seconds gap to consider suspicious
        """
        self.time_gap_threshold = time_gap_threshold
        
    def detect_scanner_avoidance(self, recognition_data: List[Dict], pos_data: List[Dict] = None) -> List[Dict]:
        """
        Detect potential scanner avoidance by analyzing recognition gaps
        
        Args:
            recognition_data: Product recognition events
            pos_data: POS transaction data (optional, for correlation)
            
        Returns:
            List of potential scanner avoidance events
        """
        avoidance_events = []
        
        # Group by station
        station_data = defaultdict(list)
        for record in recognition_data:
            station_data[record['station_id']].append(record)
        
        for station_id, records in station_data.items():
            # Sort by timestamp
            records.sort(key=lambda x: datetime.fromisoformat(x['timestamp']))
            
            for i in range(1, len(records)):
                prev_time = datetime.fromisoformat(records[i-1]['timestamp'])
                curr_time = datetime.fromisoformat(records[i]['timestamp'])
                time_gap = (curr_time - prev_time).total_seconds()
                
                # Check for suspicious gaps in recognition
                if time_gap > self.time_gap_threshold:
                    # Check if there were multiple low-confidence predictions before gap
                    recent_low_confidence = 0
                    look_back = max(0, i-5)  # Look at last 5 records
                    
                    for j in range(look_back, i):
                        if records[j]['accuracy'] < 0.6:
                            recent_low_confidence += 1
                    
                    if recent_low_confidence >= 2:  # 2 or more low confidence in recent history
                        avoidance_events.append({
                            'timestamp': records[i]['timestamp'],
                            'station_id': station_id,
                            'time_gap_seconds': time_gap,
                            'previous_low_confidence_count': recent_low_confidence,
                            'suspected_reason': 'SCANNER_AVOIDANCE_AFTER_LOW_CONFIDENCE'
                        })
        
        return avoidance_events

# @algorithm ProductMisrecognitionAnalysis | Analyzes patterns in product misrecognition
class ProductMisrecognitionAnalyzer:
    def __init__(self):
        """Initialize product misrecognition analyzer"""
        pass
        
    def analyze_misrecognition_patterns(self, recognition_data: List[Dict]) -> Dict:
        """
        Analyze patterns in product misrecognition
        
        Returns:
            Dictionary with misrecognition analysis results
        """
        analysis = {
            'confidence_statistics': {},
            'product_confidence_patterns': {},
            'temporal_patterns': {},
            'problematic_products': []
        }
        
        # Calculate overall confidence statistics
        confidences = [record['accuracy'] for record in recognition_data]
        analysis['confidence_statistics'] = {
            'mean_confidence': statistics.mean(confidences),
            'median_confidence': statistics.median(confidences),
            'min_confidence': min(confidences),
            'max_confidence': max(confidences),
            'std_dev': statistics.stdev(confidences) if len(confidences) > 1 else 0
        }
        
        # Analyze confidence by product
        product_confidences = defaultdict(list)
        for record in recognition_data:
            product_confidences[record['predicted_product']].append(record['accuracy'])
        
        for product, conf_list in product_confidences.items():
            analysis['product_confidence_patterns'][product] = {
                'count': len(conf_list),
                'avg_confidence': statistics.mean(conf_list),
                'min_confidence': min(conf_list),
                'low_confidence_count': len([c for c in conf_list if c < 0.7]),
                'very_low_confidence_count': len([c for c in conf_list if c < 0.5])
            }
        
        # Identify problematic products (consistently low confidence)
        for product, stats in analysis['product_confidence_patterns'].items():
            if stats['count'] >= 5:  # At least 5 recognitions
                low_conf_rate = stats['low_confidence_count'] / stats['count']
                if low_conf_rate > 0.4 or stats['avg_confidence'] < 0.65:  # 40% low confidence or avg < 65%
                    analysis['problematic_products'].append({
                        'product': product,
                        'avg_confidence': stats['avg_confidence'],
                        'low_confidence_rate': low_conf_rate,
                        'total_recognitions': stats['count']
                    })
        
        # Temporal pattern analysis (confidence trends over time)
        hourly_confidence = defaultdict(list)
        for record in recognition_data:
            timestamp = datetime.fromisoformat(record['timestamp'])
            hour = timestamp.hour
            hourly_confidence[hour].append(record['accuracy'])
        
        for hour, conf_list in hourly_confidence.items():
            analysis['temporal_patterns'][f'hour_{hour}'] = {
                'avg_confidence': statistics.mean(conf_list),
                'count': len(conf_list),
                'low_confidence_count': len([c for c in conf_list if c < 0.7])
            }
        
        return analysis

def load_product_recognition_data(file_path: str) -> List[Dict]:
    """Load product recognition data from JSONL file"""
    recognition_data = []
    
    with open(file_path, 'r') as f:
        for line in f:
            record = json.loads(line.strip())
            
            # Flatten recognition data
            recognition_event = {
                'timestamp': record['timestamp'],
                'station_id': record['station_id'],
                'status': record['status'],
                'predicted_product': record['data']['predicted_product'],
                'accuracy': record['data']['accuracy']
            }
            
            recognition_data.append(recognition_event)
    
    return recognition_data

def analyze_recognition_performance(recognition_data: List[Dict]) -> Dict:
    """Analyze overall recognition system performance"""
    analysis = {}
    
    # Basic statistics
    total_events = len(recognition_data)
    stations = set(record['station_id'] for record in recognition_data)
    products = set(record['predicted_product'] for record in recognition_data)
    
    # Confidence level distribution
    confidence_levels = {
        'very_high': len([r for r in recognition_data if r['accuracy'] >= 0.9]),
        'high': len([r for r in recognition_data if 0.8 <= r['accuracy'] < 0.9]),
        'medium': len([r for r in recognition_data if 0.7 <= r['accuracy'] < 0.8]),
        'low': len([r for r in recognition_data if 0.5 <= r['accuracy'] < 0.7]),
        'very_low': len([r for r in recognition_data if r['accuracy'] < 0.5])
    }
    
    analysis['summary'] = {
        'total_recognition_events': total_events,
        'unique_stations': len(stations),
        'unique_products_recognized': len(products),
        'avg_confidence': statistics.mean([r['accuracy'] for r in recognition_data]),
        'confidence_distribution': confidence_levels,
        'time_range': {
            'start': min(r['timestamp'] for r in recognition_data),
            'end': max(r['timestamp'] for r in recognition_data)
        }
    }
    
    # Station performance
    station_performance = {}
    for station in stations:
        station_records = [r for r in recognition_data if r['station_id'] == station]
        station_performance[station] = {
            'total_recognitions': len(station_records),
            'avg_confidence': statistics.mean([r['accuracy'] for r in station_records]),
            'low_confidence_count': len([r for r in station_records if r['accuracy'] < 0.7]),
            'low_confidence_rate': len([r for r in station_records if r['accuracy'] < 0.7]) / len(station_records)
        }
    
    analysis['station_performance'] = station_performance
    
    # Product recognition frequency
    product_counts = Counter(record['predicted_product'] for record in recognition_data)
    analysis['top_recognized_products'] = dict(product_counts.most_common(10))
    
    return analysis

def generate_recognition_analysis_report(file_path: str) -> Dict:
    """Generate comprehensive product recognition analysis report"""
    print("Loading product recognition data...")
    recognition_data = load_product_recognition_data(file_path)
    
    print("Analyzing recognition performance...")
    performance = analyze_recognition_performance(recognition_data)
    
    print("Detecting low confidence predictions...")
    low_conf_detector = LowConfidenceDetector(confidence_threshold=0.7)
    low_confidence_events = low_conf_detector.detect_low_confidence_predictions(recognition_data)
    
    print("Detecting scanner avoidance patterns...")
    avoidance_detector = ScannerAvoidanceDetector(time_gap_threshold=60)
    avoidance_events = avoidance_detector.detect_scanner_avoidance(recognition_data)
    
    print("Analyzing misrecognition patterns...")
    misrecognition_analyzer = ProductMisrecognitionAnalyzer()
    misrecognition_analysis = misrecognition_analyzer.analyze_misrecognition_patterns(recognition_data)
    
    # Compile report
    report = {
        'analysis_timestamp': datetime.now().isoformat(),
        'data_source': file_path,
        'recognition_performance': performance,
        'low_confidence_events': low_confidence_events,
        'scanner_avoidance_events': avoidance_events,
        'misrecognition_analysis': misrecognition_analysis,
        'summary': {
            'total_recognition_events': len(recognition_data),
            'low_confidence_events_count': len(low_confidence_events),
            'scanner_avoidance_events_count': len(avoidance_events),
            'problematic_products_count': len(misrecognition_analysis['problematic_products']),
            'avg_system_confidence': misrecognition_analysis['confidence_statistics']['mean_confidence'],
            'high_severity_low_confidence': len([e for e in low_confidence_events if e['severity'] == 'HIGH'])
        }
    }
    
    return report

def visualize_recognition_data(recognition_data: List[Dict], output_dir: str = "plots"):
    """Generate simple visualization data for recognition analysis (text-based)"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate text-based analysis files since matplotlib might not be available
    
    # Confidence distribution analysis
    confidence_ranges = {
        '0.9-1.0': 0, '0.8-0.9': 0, '0.7-0.8': 0, 
        '0.6-0.7': 0, '0.5-0.6': 0, '0.0-0.5': 0
    }
    
    for record in recognition_data:
        conf = record['accuracy']
        if conf >= 0.9:
            confidence_ranges['0.9-1.0'] += 1
        elif conf >= 0.8:
            confidence_ranges['0.8-0.9'] += 1
        elif conf >= 0.7:
            confidence_ranges['0.7-0.8'] += 1
        elif conf >= 0.6:
            confidence_ranges['0.6-0.7'] += 1
        elif conf >= 0.5:
            confidence_ranges['0.5-0.6'] += 1
        else:
            confidence_ranges['0.0-0.5'] += 1
    
    with open(f"{output_dir}/confidence_distribution.txt", "w") as f:
        f.write("Product Recognition Confidence Distribution\n")
        f.write("=" * 45 + "\n\n")
        for range_name, count in confidence_ranges.items():
            percentage = (count / len(recognition_data)) * 100
            bar = "█" * int(percentage / 2)  # Simple text bar chart
            f.write(f"{range_name:8} | {count:4} ({percentage:5.1f}%) {bar}\n")
    
    # Hourly confidence trends
    hourly_data = defaultdict(list)
    for record in recognition_data:
        timestamp = datetime.fromisoformat(record['timestamp'])
        hour = timestamp.hour
        hourly_data[hour].append(record['accuracy'])
    
    with open(f"{output_dir}/hourly_confidence_trends.txt", "w") as f:
        f.write("Hourly Confidence Trends\n")
        f.write("=" * 25 + "\n\n")
        f.write("Hour | Count | Avg Conf | Low Conf Count\n")
        f.write("-" * 40 + "\n")
        
        for hour in sorted(hourly_data.keys()):
            conf_list = hourly_data[hour]
            avg_conf = statistics.mean(conf_list)
            low_count = len([c for c in conf_list if c < 0.7])
            f.write(f"{hour:4} | {len(conf_list):5} | {avg_conf:8.3f} | {low_count:12}\n")

if __name__ == "__main__":
    # File path to product recognition data
    recognition_file = "data/input/product_recognition.jsonl"
    
    try:
        report = generate_recognition_analysis_report(recognition_file)
        
        # Save report to JSON
        with open("product_recognition_analysis_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*50)
        print("PRODUCT RECOGNITION ANALYSIS SUMMARY")
        print("="*50)
        print(f"Total Recognition Events: {report['summary']['total_recognition_events']:,}")
        print(f"Average System Confidence: {report['summary']['avg_system_confidence']:.3f}")
        print(f"Low Confidence Events: {report['summary']['low_confidence_events_count']}")
        print(f"High Severity Low Confidence: {report['summary']['high_severity_low_confidence']}")
        print(f"Scanner Avoidance Events: {report['summary']['scanner_avoidance_events_count']}")
        print(f"Problematic Products: {report['summary']['problematic_products_count']}")
        
        # Show confidence distribution
        conf_dist = report['recognition_performance']['summary']['confidence_distribution']
        print(f"\nCONFIDENCE DISTRIBUTION:")
        print(f"Very High (≥0.9): {conf_dist['very_high']:,}")
        print(f"High (0.8-0.9): {conf_dist['high']:,}")
        print(f"Medium (0.7-0.8): {conf_dist['medium']:,}")
        print(f"Low (0.5-0.7): {conf_dist['low']:,}")
        print(f"Very Low (<0.5): {conf_dist['very_low']:,}")
        
        # Show problematic products
        if report['misrecognition_analysis']['problematic_products']:
            print(f"\nPROBLEMATIC PRODUCTS (Low Recognition Accuracy):")
            for i, product in enumerate(report['misrecognition_analysis']['problematic_products'][:5], 1):
                print(f"{i}. {product['product']}: {product['avg_confidence']:.3f} avg confidence "
                      f"({product['low_confidence_rate']:.1%} low confidence rate)")
        
        print(f"\nDetailed report saved to: product_recognition_analysis_report.json")
        
        # Generate text-based visualizations
        recognition_data = load_product_recognition_data(recognition_file)
        visualize_recognition_data(recognition_data)
        print("Analysis charts saved to: plots/")
        
    except FileNotFoundError:
        print(f"Error: Could not find product recognition file at {recognition_file}")
        print("Please ensure the file path is correct.")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
