#!/usr/bin/env python3
"""
RFID Readings Analysis
======================

This script analyzes RFID reading data to detect:
- Missing RFID tags (products without tags)
- RFID tag movement patterns
- Potential tag cloning or manipulation
- Products leaving without RFID detection
- RFID system performance issues

Data Format: JSONL with RFID tag readings including EPC, location, and SKU
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict, Counter

# @algorithm RFIDCoverageAnalysis | Analyzes RFID tag coverage and missing tags
class RFIDCoverageAnalyzer:
    def __init__(self):
        """Initialize RFID coverage analyzer"""
        pass
        
    def analyze_rfid_coverage(self, rfid_data: List[Dict], pos_data: List[Dict] = None) -> Dict:
        """
        Analyze RFID tag coverage by comparing RFID readings with expected products
        
        Args:
            rfid_data: RFID reading events
            pos_data: POS transaction data for comparison (optional)
            
        Returns:
            Dictionary with coverage analysis results
        """
        analysis = {
            'coverage_statistics': {},
            'missing_tag_events': [],
            'tag_performance': {},
            'station_coverage': {}
        }
        
        # Count null vs valid RFID readings
        total_readings = len(rfid_data)
        null_readings = len([r for r in rfid_data if r['epc'] is None])
        valid_readings = total_readings - null_readings
        
        analysis['coverage_statistics'] = {
            'total_rfid_readings': total_readings,
            'valid_tag_readings': valid_readings,
            'null_readings': null_readings,
            'coverage_rate': valid_readings / total_readings if total_readings > 0 else 0,
            'missing_tag_rate': null_readings / total_readings if total_readings > 0 else 0
        }
        
        # Analyze by station
        station_data = defaultdict(lambda: {'total': 0, 'valid': 0, 'null': 0})
        
        for record in rfid_data:
            station = record['station_id']
            station_data[station]['total'] += 1
            
            if record['epc'] is None:
                station_data[station]['null'] += 1
            else:
                station_data[station]['valid'] += 1
        
        for station, stats in station_data.items():
            analysis['station_coverage'][station] = {
                'total_readings': stats['total'],
                'valid_readings': stats['valid'],
                'null_readings': stats['null'],
                'coverage_rate': stats['valid'] / stats['total'] if stats['total'] > 0 else 0
            }
        
        # Identify periods of missing RFID coverage
        current_null_streak = None
        
        for record in sorted(rfid_data, key=lambda x: x['timestamp']):
            if record['epc'] is None:
                if current_null_streak is None:
                    current_null_streak = {
                        'start_time': record['timestamp'],
                        'station_id': record['station_id'],
                        'count': 1
                    }
                else:
                    current_null_streak['count'] += 1
                    current_null_streak['end_time'] = record['timestamp']
            else:
                if current_null_streak is not None and current_null_streak['count'] >= 10:  # 10+ consecutive null readings
                    analysis['missing_tag_events'].append(current_null_streak)
                current_null_streak = None
        
        # Close any ongoing null streak
        if current_null_streak is not None and current_null_streak['count'] >= 10:
            analysis['missing_tag_events'].append(current_null_streak)
        
        return analysis

# @algorithm RFIDMovementTracking | Tracks RFID tag movement patterns
class RFIDMovementTracker:
    def __init__(self):
        """Initialize RFID movement tracker"""
        pass
        
    def track_tag_movements(self, rfid_data: List[Dict]) -> Dict:
        """
        Track movement patterns of RFID tags
        
        Returns:
            Dictionary with tag movement analysis
        """
        analysis = {
            'tag_journeys': {},
            'suspicious_movements': [],
            'location_transitions': defaultdict(int),
            'tag_statistics': {}
        }
        
        # Group readings by EPC tag
        tag_readings = defaultdict(list)
        
        for record in rfid_data:
            if record['epc'] is not None:
                tag_readings[record['epc']].append(record)
        
        # Analyze each tag's journey
        for epc, readings in tag_readings.items():
            readings.sort(key=lambda x: datetime.fromisoformat(x['timestamp']))
            
            journey = {
                'epc': epc,
                'sku': readings[0]['sku'] if readings[0]['sku'] else 'UNKNOWN',
                'first_seen': readings[0]['timestamp'],
                'last_seen': readings[-1]['timestamp'],
                'total_readings': len(readings),
                'locations_visited': list(set(r['location'] for r in readings if r['location'])),
                'stations_visited': list(set(r['station_id'] for r in readings)),
                'movement_pattern': []
            }
            
            # Track location transitions
            prev_location = None
            for reading in readings:
                current_location = reading['location']
                if current_location and current_location != prev_location:
                    if prev_location:
                        transition = f"{prev_location} -> {current_location}"
                        analysis['location_transitions'][transition] += 1
                        journey['movement_pattern'].append({
                            'timestamp': reading['timestamp'],
                            'from_location': prev_location,
                            'to_location': current_location
                        })
                    prev_location = current_location
            
            analysis['tag_journeys'][epc] = journey
            
            # Detect suspicious movement patterns
            if len(journey['locations_visited']) > 5:  # Tag visited many locations
                analysis['suspicious_movements'].append({
                    'epc': epc,
                    'sku': journey['sku'],
                    'reason': 'EXCESSIVE_MOVEMENT',
                    'locations_count': len(journey['locations_visited']),
                    'locations': journey['locations_visited']
                })
            
            # Check for rapid back-and-forth movement
            if len(journey['movement_pattern']) > 3:
                locations_sequence = [m['to_location'] for m in journey['movement_pattern']]
                for i in range(len(locations_sequence) - 2):
                    if (locations_sequence[i] == locations_sequence[i+2] and 
                        locations_sequence[i] != locations_sequence[i+1]):
                        analysis['suspicious_movements'].append({
                            'epc': epc,
                            'sku': journey['sku'],
                            'reason': 'RAPID_BACK_AND_FORTH',
                            'pattern': locations_sequence[i:i+3],
                            'timestamp': journey['movement_pattern'][i+1]['timestamp']
                        })
                        break
        
        # Overall tag statistics
        if tag_readings:
            reading_counts = [len(readings) for readings in tag_readings.values()]
            location_counts = [len(set(r['location'] for r in readings if r['location'])) 
                             for readings in tag_readings.values()]
            
            analysis['tag_statistics'] = {
                'unique_tags_detected': len(tag_readings),
                'avg_readings_per_tag': statistics.mean(reading_counts),
                'max_readings_per_tag': max(reading_counts),
                'avg_locations_per_tag': statistics.mean(location_counts) if location_counts else 0,
                'tags_with_multiple_locations': len([c for c in location_counts if c > 1])
            }
        
        return analysis

# @algorithm RFIDSecurityAnalysis | Detects potential RFID security issues
class RFIDSecurityAnalyzer:
    def __init__(self):
        """Initialize RFID security analyzer"""
        pass
        
    def detect_security_issues(self, rfid_data: List[Dict]) -> Dict:
        """
        Detect potential RFID security issues like tag cloning or manipulation
        
        Returns:
            Dictionary with security analysis results
        """
        analysis = {
            'duplicate_epc_events': [],
            'tag_sku_mismatches': [],
            'temporal_anomalies': [],
            'security_summary': {}
        }
        
        # Group by EPC and timestamp to find duplicates
        epc_timestamp_map = defaultdict(list)
        
        for record in rfid_data:
            if record['epc'] is not None:
                timestamp_key = record['timestamp'][:16]  # Group by minute
                epc_timestamp_map[(record['epc'], timestamp_key)].append(record)
        
        # Detect simultaneous readings of same tag (potential cloning)
        for (epc, timestamp_key), readings in epc_timestamp_map.items():
            if len(readings) > 1:
                # Check if readings are at different locations simultaneously
                locations = set(r['location'] for r in readings if r['location'])
                stations = set(r['station_id'] for r in readings)
                
                if len(locations) > 1 or len(stations) > 1:
                    analysis['duplicate_epc_events'].append({
                        'epc': epc,
                        'timestamp_window': timestamp_key,
                        'simultaneous_readings': len(readings),
                        'locations': list(locations),
                        'stations': list(stations),
                        'suspicion_level': 'HIGH' if len(locations) > 1 else 'MEDIUM'
                    })
        
        # Detect tag-SKU mismatches (same tag associated with different SKUs)
        tag_sku_map = defaultdict(set)
        
        for record in rfid_data:
            if record['epc'] is not None and record['sku'] is not None:
                tag_sku_map[record['epc']].add(record['sku'])
        
        for epc, skus in tag_sku_map.items():
            if len(skus) > 1:
                analysis['tag_sku_mismatches'].append({
                    'epc': epc,
                    'associated_skus': list(skus),
                    'sku_count': len(skus),
                    'suspicion_level': 'HIGH'  # Same tag for different products is highly suspicious
                })
        
        # Detect temporal anomalies (tags appearing after long absence)
        tag_timeline = defaultdict(list)
        
        for record in rfid_data:
            if record['epc'] is not None:
                tag_timeline[record['epc']].append(datetime.fromisoformat(record['timestamp']))
        
        for epc, timestamps in tag_timeline.items():
            timestamps.sort()
            
            for i in range(1, len(timestamps)):
                time_gap = (timestamps[i] - timestamps[i-1]).total_seconds()
                
                # Flag gaps longer than 1 hour as potentially suspicious
                if time_gap > 3600:  # 1 hour
                    analysis['temporal_anomalies'].append({
                        'epc': epc,
                        'gap_start': timestamps[i-1].isoformat(),
                        'gap_end': timestamps[i].isoformat(),
                        'gap_duration_hours': time_gap / 3600,
                        'suspicion_level': 'HIGH' if time_gap > 7200 else 'MEDIUM'  # 2+ hours = high
                    })
        
        # Security summary
        analysis['security_summary'] = {
            'duplicate_epc_incidents': len(analysis['duplicate_epc_events']),
            'high_risk_duplicates': len([e for e in analysis['duplicate_epc_events'] if e['suspicion_level'] == 'HIGH']),
            'tag_sku_mismatches': len(analysis['tag_sku_mismatches']),
            'temporal_anomalies': len(analysis['temporal_anomalies']),
            'high_risk_temporal_anomalies': len([a for a in analysis['temporal_anomalies'] if a['suspicion_level'] == 'HIGH'])
        }
        
        return analysis

def load_rfid_readings_data(file_path: str) -> List[Dict]:
    """Load RFID readings data from JSONL file"""
    rfid_data = []
    
    with open(file_path, 'r') as f:
        for line in f:
            record = json.loads(line.strip())
            
            # Flatten RFID data
            rfid_reading = {
                'timestamp': record['timestamp'],
                'station_id': record['station_id'],
                'status': record['status'],
                'epc': record['data']['epc'],
                'location': record['data']['location'],
                'sku': record['data']['sku']
            }
            
            rfid_data.append(rfid_reading)
    
    return rfid_data

def analyze_rfid_system_performance(rfid_data: List[Dict]) -> Dict:
    """Analyze overall RFID system performance"""
    analysis = {}
    
    # Basic statistics
    total_readings = len(rfid_data)
    valid_readings = len([r for r in rfid_data if r['epc'] is not None])
    unique_tags = len(set(r['epc'] for r in rfid_data if r['epc'] is not None))
    stations = set(r['station_id'] for r in rfid_data)
    
    analysis['summary'] = {
        'total_rfid_readings': total_readings,
        'valid_tag_readings': valid_readings,
        'null_readings': total_readings - valid_readings,
        'unique_tags_detected': unique_tags,
        'unique_stations': len(stations),
        'overall_detection_rate': valid_readings / total_readings if total_readings > 0 else 0,
        'time_range': {
            'start': min(r['timestamp'] for r in rfid_data),
            'end': max(r['timestamp'] for r in rfid_data)
        }
    }
    
    # Station-level performance
    station_performance = {}
    
    for station in stations:
        station_readings = [r for r in rfid_data if r['station_id'] == station]
        station_valid = len([r for r in station_readings if r['epc'] is not None])
        
        station_performance[station] = {
            'total_readings': len(station_readings),
            'valid_readings': station_valid,
            'detection_rate': station_valid / len(station_readings) if station_readings else 0,
            'unique_tags': len(set(r['epc'] for r in station_readings if r['epc'] is not None))
        }
    
    analysis['station_performance'] = station_performance
    
    # Temporal analysis (hourly detection rates)
    hourly_stats = defaultdict(lambda: {'total': 0, 'valid': 0})
    
    for record in rfid_data:
        timestamp = datetime.fromisoformat(record['timestamp'])
        hour = timestamp.hour
        hourly_stats[hour]['total'] += 1
        if record['epc'] is not None:
            hourly_stats[hour]['valid'] += 1
    
    hourly_detection_rates = {}
    for hour, stats in hourly_stats.items():
        hourly_detection_rates[f'hour_{hour}'] = {
            'total_readings': stats['total'],
            'valid_readings': stats['valid'],
            'detection_rate': stats['valid'] / stats['total'] if stats['total'] > 0 else 0
        }
    
    analysis['hourly_performance'] = hourly_detection_rates
    
    return analysis

def generate_rfid_analysis_report(file_path: str) -> Dict:
    """Generate comprehensive RFID readings analysis report"""
    print("Loading RFID readings data...")
    rfid_data = load_rfid_readings_data(file_path)
    
    print("Analyzing RFID system performance...")
    performance = analyze_rfid_system_performance(rfid_data)
    
    print("Analyzing RFID coverage...")
    coverage_analyzer = RFIDCoverageAnalyzer()
    coverage_analysis = coverage_analyzer.analyze_rfid_coverage(rfid_data)
    
    print("Tracking RFID tag movements...")
    movement_tracker = RFIDMovementTracker()
    movement_analysis = movement_tracker.track_tag_movements(rfid_data)
    
    print("Detecting RFID security issues...")
    security_analyzer = RFIDSecurityAnalyzer()
    security_analysis = security_analyzer.detect_security_issues(rfid_data)
    
    # Compile report
    report = {
        'analysis_timestamp': datetime.now().isoformat(),
        'data_source': file_path,
        'system_performance': performance,
        'coverage_analysis': coverage_analysis,
        'movement_analysis': movement_analysis,
        'security_analysis': security_analysis,
        'summary': {
            'total_rfid_readings': len(rfid_data),
            'rfid_detection_rate': performance['summary']['overall_detection_rate'],
            'unique_tags_tracked': movement_analysis['tag_statistics'].get('unique_tags_detected', 0),
            'coverage_issues': len(coverage_analysis['missing_tag_events']),
            'security_incidents': (security_analysis['security_summary']['duplicate_epc_incidents'] + 
                                 security_analysis['security_summary']['tag_sku_mismatches']),
            'suspicious_movements': len(movement_analysis['suspicious_movements'])
        }
    }
    
    return report

def visualize_rfid_data(rfid_data: List[Dict], output_dir: str = "plots"):
    """Generate text-based visualization data for RFID analysis"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # RFID detection rate by hour
    hourly_stats = defaultdict(lambda: {'total': 0, 'valid': 0})
    
    for record in rfid_data:
        timestamp = datetime.fromisoformat(record['timestamp'])
        hour = timestamp.hour
        hourly_stats[hour]['total'] += 1
        if record['epc'] is not None:
            hourly_stats[hour]['valid'] += 1
    
    with open(f"{output_dir}/rfid_detection_rates.txt", "w") as f:
        f.write("RFID Detection Rates by Hour\n")
        f.write("=" * 30 + "\n\n")
        f.write("Hour | Total | Valid | Rate | Detection Bar\n")
        f.write("-" * 45 + "\n")
        
        for hour in range(24):
            stats = hourly_stats.get(hour, {'total': 0, 'valid': 0})
            rate = (stats['valid'] / stats['total']) * 100 if stats['total'] > 0 else 0
            bar_length = int(rate / 5)  # Scale to 20 chars max
            detection_bar = "█" * bar_length
            
            f.write(f"{hour:4} | {stats['total']:5} | {stats['valid']:5} | {rate:4.1f}% | {detection_bar}\n")
    
    # Station performance comparison
    station_stats = defaultdict(lambda: {'total': 0, 'valid': 0})
    
    for record in rfid_data:
        station = record['station_id']
        station_stats[station]['total'] += 1
        if record['epc'] is not None:
            station_stats[station]['valid'] += 1
    
    with open(f"{output_dir}/station_rfid_performance.txt", "w") as f:
        f.write("RFID Performance by Station\n")
        f.write("=" * 30 + "\n\n")
        f.write("Station | Total | Valid | Detection Rate | Performance Bar\n")
        f.write("-" * 55 + "\n")
        
        for station, stats in station_stats.items():
            rate = (stats['valid'] / stats['total']) * 100 if stats['total'] > 0 else 0
            bar_length = int(rate / 5)  # Scale to 20 chars max
            performance_bar = "█" * bar_length
            
            f.write(f"{station:7} | {stats['total']:5} | {stats['valid']:5} | {rate:12.1f}% | {performance_bar}\n")

if __name__ == "__main__":
    # File path to RFID readings
    rfid_file = "data/input/rfid_readings.jsonl"
    
    try:
        report = generate_rfid_analysis_report(rfid_file)
        
        # Save report to JSON
        with open("rfid_analysis_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*50)
        print("RFID READINGS ANALYSIS SUMMARY")
        print("="*50)
        print(f"Total RFID Readings: {report['summary']['total_rfid_readings']:,}")
        print(f"RFID Detection Rate: {report['summary']['rfid_detection_rate']:.1%}")
        print(f"Unique Tags Tracked: {report['summary']['unique_tags_tracked']}")
        print(f"Coverage Issues: {report['summary']['coverage_issues']}")
        print(f"Security Incidents: {report['summary']['security_incidents']}")
        print(f"Suspicious Movements: {report['summary']['suspicious_movements']}")
        
        # Show station performance
        print(f"\nSTATION RFID PERFORMANCE:")
        for station, perf in report['system_performance']['station_performance'].items():
            print(f"{station}: {perf['detection_rate']:.1%} detection rate "
                  f"({perf['valid_readings']}/{perf['total_readings']} readings)")
        
        # Show security issues if any
        if report['security_analysis']['security_summary']['duplicate_epc_incidents'] > 0:
            print(f"\nSECURITY ALERTS:")
            print(f"Duplicate EPC Incidents: {report['security_analysis']['security_summary']['duplicate_epc_incidents']}")
            print(f"Tag-SKU Mismatches: {report['security_analysis']['security_summary']['tag_sku_mismatches']}")
        
        # Show top suspicious movements
        if report['movement_analysis']['suspicious_movements']:
            print(f"\nSUSPICIOUS TAG MOVEMENTS:")
            for i, movement in enumerate(report['movement_analysis']['suspicious_movements'][:3], 1):
                print(f"{i}. Tag {movement['epc']} ({movement['sku']}): {movement['reason']}")
        
        print(f"\nDetailed report saved to: rfid_analysis_report.json")
        
        # Generate text-based visualizations
        rfid_data = load_rfid_readings_data(rfid_file)
        visualize_rfid_data(rfid_data)
        print("Analysis charts saved to: plots/")
        
    except FileNotFoundError:
        print(f"Error: Could not find RFID readings file at {rfid_file}")
        print("Please ensure the file path is correct.")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

# Import statistics module if available
try:
    import statistics
except ImportError:
    # Fallback implementations for basic statistics
    class statistics:
        @staticmethod
        def mean(data):
            return sum(data) / len(data) if data else 0
        
        @staticmethod
        def median(data):
            sorted_data = sorted(data)
            n = len(sorted_data)
            if n == 0:
                return 0
            elif n % 2 == 0:
                return (sorted_data[n//2-1] + sorted_data[n//2]) / 2
            else:
                return sorted_data[n//2]
        
        @staticmethod
        def stdev(data):
            if len(data) < 2:
                return 0
            mean_val = statistics.mean(data)
            variance = sum((x - mean_val) ** 2 for x in data) / (len(data) - 1)
            return variance ** 0.5
