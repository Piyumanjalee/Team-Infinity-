#!/usr/bin/env python3
"""
Queue Monitoring Analysis
=========================

This script analyzes queue monitoring data to detect:
- Unusual customer dwell times (potential fraud or confusion)
- Queue congestion patterns
- Station utilization issues
- Customer experience problems
- Peak usage times and bottlenecks

Data Format: JSONL with customer counts and dwell times per station
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Set
from collections import defaultdict
import statistics

# @algorithm DwellTimeAnomalyDetection | Detects unusual customer dwell times indicating potential issues
class DwellTimeAnomalyDetector:
    def __init__(self, high_dwell_threshold: float = 300.0, low_dwell_threshold: float = 10.0):
        """
        Initialize dwell time anomaly detector
        
        Args:
            high_dwell_threshold: Seconds above which dwell time is considered suspicious
            low_dwell_threshold: Seconds below which dwell time might indicate avoidance
        """
        self.high_threshold = high_dwell_threshold
        self.low_threshold = low_dwell_threshold
        
    def detect_dwell_anomalies(self, queue_data: List[Dict]) -> List[Dict]:
        """
        Detect anomalous dwell times that might indicate fraud or operational issues
        
        Returns:
            List of anomalous dwell time events
        """
        anomalies = []
        
        for record in queue_data:
            dwell_time = record['average_dwell_time']
            customer_count = record['customer_count']
            
            # Skip empty stations
            if customer_count == 0:
                continue
            
            # Detect unusually high dwell times
            if dwell_time > self.high_threshold:
                anomalies.append({
                    'timestamp': record['timestamp'],
                    'station_id': record['station_id'],
                    'customer_count': customer_count,
                    'dwell_time': dwell_time,
                    'anomaly_type': 'HIGH_DWELL_TIME',
                    'severity': 'HIGH' if dwell_time > 600 else 'MEDIUM',  # 10+ minutes is high severity
                    'potential_causes': ['checkout_difficulty', 'scanner_issues', 'suspicious_activity']
                })
            
            # Detect unusually low dwell times (potential scanner avoidance)
            elif dwell_time < self.low_threshold and customer_count > 0:
                anomalies.append({
                    'timestamp': record['timestamp'],
                    'station_id': record['station_id'],
                    'customer_count': customer_count,
                    'dwell_time': dwell_time,
                    'anomaly_type': 'LOW_DWELL_TIME',
                    'severity': 'MEDIUM',
                    'potential_causes': ['scanner_avoidance', 'quick_pass_through', 'system_error']
                })
        
        return anomalies

# @algorithm CongestionAnalysis | Analyzes queue congestion patterns and bottlenecks
class CongestionAnalyzer:
    def __init__(self, congestion_threshold: int = 3):
        """
        Initialize congestion analyzer
        
        Args:
            congestion_threshold: Customer count above which station is considered congested
        """
        self.congestion_threshold = congestion_threshold
        
    def analyze_congestion_patterns(self, queue_data: List[Dict]) -> Dict:
        """
        Analyze queue congestion patterns across stations and time
        
        Returns:
            Dictionary with congestion analysis results
        """
        analysis = {
            'congestion_events': [],
            'station_congestion_stats': {},
            'peak_hours': {},
            'bottleneck_periods': []
        }
        
        # Group data by station
        station_data = defaultdict(list)
        for record in queue_data:
            station_data[record['station_id']].append(record)
        
        # Analyze each station
        for station_id, records in station_data.items():
            records.sort(key=lambda x: datetime.fromisoformat(x['timestamp']))
            
            congested_periods = []
            current_congestion = None
            
            for record in records:
                customer_count = record['customer_count']
                timestamp = datetime.fromisoformat(record['timestamp'])
                
                if customer_count > self.congestion_threshold:
                    # Start or continue congestion period
                    if current_congestion is None:
                        current_congestion = {
                            'start_time': record['timestamp'],
                            'peak_customers': customer_count,
                            'total_observations': 1
                        }
                    else:
                        current_congestion['peak_customers'] = max(
                            current_congestion['peak_customers'], 
                            customer_count
                        )
                        current_congestion['total_observations'] += 1
                        current_congestion['end_time'] = record['timestamp']
                    
                    # Record individual congestion event
                    analysis['congestion_events'].append({
                        'timestamp': record['timestamp'],
                        'station_id': station_id,
                        'customer_count': customer_count,
                        'dwell_time': record['average_dwell_time']
                    })
                    
                else:
                    # End congestion period if it was ongoing
                    if current_congestion is not None:
                        current_congestion['end_time'] = records[records.index(record)-1]['timestamp'] if records.index(record) > 0 else current_congestion['start_time']
                        congested_periods.append(current_congestion)
                        current_congestion = None
            
            # Close any ongoing congestion period
            if current_congestion is not None:
                current_congestion['end_time'] = records[-1]['timestamp']
                congested_periods.append(current_congestion)
            
            # Station statistics
            customer_counts = [r['customer_count'] for r in records]
            dwell_times = [r['average_dwell_time'] for r in records if r['customer_count'] > 0]
            
            analysis['station_congestion_stats'][station_id] = {
                'total_observations': len(records),
                'congested_observations': len([r for r in records if r['customer_count'] > self.congestion_threshold]),
                'congestion_rate': len([r for r in records if r['customer_count'] > self.congestion_threshold]) / len(records),
                'avg_customers': statistics.mean(customer_counts),
                'max_customers': max(customer_counts),
                'avg_dwell_time': statistics.mean(dwell_times) if dwell_times else 0,
                'congested_periods': congested_periods
            }
        
        # Analyze peak hours across all stations
        hourly_congestion = defaultdict(int)
        for record in queue_data:
            if record['customer_count'] > self.congestion_threshold:
                timestamp = datetime.fromisoformat(record['timestamp'])
                hour = timestamp.hour
                hourly_congestion[hour] += 1
        
        analysis['peak_hours'] = dict(hourly_congestion)
        
        return analysis

# @algorithm OperationalEfficiencyAnalysis | Measures operational efficiency metrics
class OperationalEfficiencyAnalyzer:
    def __init__(self):
        """Initialize operational efficiency analyzer"""
        pass
        
    def analyze_efficiency_metrics(self, queue_data: List[Dict]) -> Dict:
        """
        Analyze operational efficiency metrics
        
        Returns:
            Dictionary with efficiency analysis results
        """
        analysis = {
            'station_efficiency': {},
            'time_based_efficiency': {},
            'overall_metrics': {}
        }
        
        # Group data by station
        station_data = defaultdict(list)
        for record in queue_data:
            station_data[record['station_id']].append(record)
        
        # Calculate station-level efficiency metrics
        for station_id, records in station_data.items():
            active_records = [r for r in records if r['customer_count'] > 0]
            
            if active_records:
                dwell_times = [r['average_dwell_time'] for r in active_records]
                customer_counts = [r['customer_count'] for r in active_records]
                
                # Calculate efficiency metrics
                avg_dwell = statistics.mean(dwell_times)
                avg_customers = statistics.mean(customer_counts)
                
                # Efficiency score: lower dwell time with more customers is better
                efficiency_score = (1 / avg_dwell) * avg_customers if avg_dwell > 0 else 0
                
                analysis['station_efficiency'][station_id] = {
                    'avg_dwell_time': avg_dwell,
                    'avg_customer_count': avg_customers,
                    'efficiency_score': efficiency_score,
                    'utilization_rate': len(active_records) / len(records),
                    'total_customer_minutes': sum(r['customer_count'] * r['average_dwell_time'] / 60 for r in active_records),
                    'problem_periods': len([r for r in active_records if r['average_dwell_time'] > 300])  # 5+ minute average
                }
            else:
                analysis['station_efficiency'][station_id] = {
                    'avg_dwell_time': 0,
                    'avg_customer_count': 0,
                    'efficiency_score': 0,
                    'utilization_rate': 0,
                    'total_customer_minutes': 0,
                    'problem_periods': 0
                }
        
        # Time-based efficiency analysis (hourly)
        hourly_data = defaultdict(list)
        for record in queue_data:
            timestamp = datetime.fromisoformat(record['timestamp'])
            hour = timestamp.hour
            hourly_data[hour].append(record)
        
        for hour, records in hourly_data.items():
            active_records = [r for r in records if r['customer_count'] > 0]
            
            if active_records:
                avg_dwell = statistics.mean([r['average_dwell_time'] for r in active_records])
                total_customers = sum(r['customer_count'] for r in active_records)
                
                analysis['time_based_efficiency'][f'hour_{hour}'] = {
                    'total_observations': len(records),
                    'active_observations': len(active_records),
                    'avg_dwell_time': avg_dwell,
                    'total_customers_served': total_customers,
                    'efficiency_indicator': total_customers / avg_dwell if avg_dwell > 0 else 0
                }
        
        # Overall system metrics
        all_active_records = [r for r in queue_data if r['customer_count'] > 0]
        if all_active_records:
            analysis['overall_metrics'] = {
                'total_active_periods': len(all_active_records),
                'system_avg_dwell_time': statistics.mean([r['average_dwell_time'] for r in all_active_records]),
                'system_utilization': len(all_active_records) / len(queue_data),
                'peak_concurrent_customers': max(r['customer_count'] for r in all_active_records),
                'total_customer_sessions': sum(r['customer_count'] for r in all_active_records)
            }
        
        return analysis

def load_queue_monitoring_data(file_path: str) -> List[Dict]:
    """Load queue monitoring data from JSONL file"""
    queue_data = []
    
    with open(file_path, 'r') as f:
        for line in f:
            record = json.loads(line.strip())
            
            # Flatten queue monitoring data
            queue_event = {
                'timestamp': record['timestamp'],
                'station_id': record['station_id'],
                'status': record['status'],
                'customer_count': record['data']['customer_count'],
                'average_dwell_time': record['data']['average_dwell_time']
            }
            
            queue_data.append(queue_event)
    
    return queue_data

def analyze_queue_patterns(queue_data: List[Dict]) -> Dict:
    """Analyze overall queue patterns and usage statistics"""
    analysis = {}
    
    # Basic statistics
    total_observations = len(queue_data)
    active_observations = len([r for r in queue_data if r['customer_count'] > 0])
    stations = set(record['station_id'] for record in queue_data)
    
    analysis['summary'] = {
        'total_observations': total_observations,
        'active_observations': active_observations,
        'system_utilization_rate': active_observations / total_observations if total_observations > 0 else 0,
        'unique_stations': len(stations),
        'time_range': {
            'start': min(r['timestamp'] for r in queue_data),
            'end': max(r['timestamp'] for r in queue_data)
        }
    }
    
    # Station-level statistics
    station_stats = {}
    for station in stations:
        station_records = [r for r in queue_data if r['station_id'] == station]
        active_station_records = [r for r in station_records if r['customer_count'] > 0]
        
        if active_station_records:
            station_stats[station] = {
                'total_observations': len(station_records),
                'active_observations': len(active_station_records),
                'utilization_rate': len(active_station_records) / len(station_records),
                'avg_customers': statistics.mean([r['customer_count'] for r in active_station_records]),
                'max_customers': max(r['customer_count'] for r in active_station_records),
                'avg_dwell_time': statistics.mean([r['average_dwell_time'] for r in active_station_records]),
                'max_dwell_time': max(r['average_dwell_time'] for r in active_station_records)
            }
        else:
            station_stats[station] = {
                'total_observations': len(station_records),
                'active_observations': 0,
                'utilization_rate': 0,
                'avg_customers': 0,
                'max_customers': 0,
                'avg_dwell_time': 0,
                'max_dwell_time': 0
            }
    
    analysis['station_statistics'] = station_stats
    
    return analysis

def generate_queue_analysis_report(file_path: str) -> Dict:
    """Generate comprehensive queue monitoring analysis report"""
    print("Loading queue monitoring data...")
    queue_data = load_queue_monitoring_data(file_path)
    
    print("Analyzing queue patterns...")
    patterns = analyze_queue_patterns(queue_data)
    
    print("Detecting dwell time anomalies...")
    dwell_detector = DwellTimeAnomalyDetector(high_dwell_threshold=300.0, low_dwell_threshold=10.0)
    dwell_anomalies = dwell_detector.detect_dwell_anomalies(queue_data)
    
    print("Analyzing congestion patterns...")
    congestion_analyzer = CongestionAnalyzer(congestion_threshold=2)  # 3+ customers = congested
    congestion_analysis = congestion_analyzer.analyze_congestion_patterns(queue_data)
    
    print("Analyzing operational efficiency...")
    efficiency_analyzer = OperationalEfficiencyAnalyzer()
    efficiency_analysis = efficiency_analyzer.analyze_efficiency_metrics(queue_data)
    
    # Compile report
    report = {
        'analysis_timestamp': datetime.now().isoformat(),
        'data_source': file_path,
        'queue_patterns': patterns,
        'dwell_time_anomalies': dwell_anomalies,
        'congestion_analysis': congestion_analysis,
        'efficiency_analysis': efficiency_analysis,
        'summary': {
            'total_queue_observations': len(queue_data),
            'dwell_time_anomalies_count': len(dwell_anomalies),
            'high_severity_dwell_anomalies': len([a for a in dwell_anomalies if a['severity'] == 'HIGH']),
            'congestion_events_count': len(congestion_analysis['congestion_events']),
            'stations_with_efficiency_issues': len([s for s, stats in efficiency_analysis['station_efficiency'].items() 
                                                   if stats['problem_periods'] > 5]),
            'overall_system_utilization': patterns['summary']['system_utilization_rate']
        }
    }
    
    return report

def visualize_queue_data(queue_data: List[Dict], output_dir: str = "plots"):
    """Generate text-based visualization data for queue analysis"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Station utilization summary
    station_data = defaultdict(list)
    for record in queue_data:
        station_data[record['station_id']].append(record)
    
    with open(f"{output_dir}/station_utilization.txt", "w") as f:
        f.write("Station Utilization Analysis\n")
        f.write("=" * 30 + "\n\n")
        f.write("Station | Total | Active | Util% | Avg Customers | Avg Dwell\n")
        f.write("-" * 60 + "\n")
        
        for station_id, records in station_data.items():
            active_records = [r for r in records if r['customer_count'] > 0]
            utilization = (len(active_records) / len(records)) * 100 if records else 0
            avg_customers = statistics.mean([r['customer_count'] for r in active_records]) if active_records else 0
            avg_dwell = statistics.mean([r['average_dwell_time'] for r in active_records]) if active_records else 0
            
            f.write(f"{station_id:7} | {len(records):5} | {len(active_records):6} | {utilization:4.1f}% | {avg_customers:12.1f} | {avg_dwell:8.1f}s\n")
    
    # Hourly activity pattern
    hourly_activity = defaultdict(int)
    hourly_dwell = defaultdict(list)
    
    for record in queue_data:
        if record['customer_count'] > 0:
            timestamp = datetime.fromisoformat(record['timestamp'])
            hour = timestamp.hour
            hourly_activity[hour] += record['customer_count']
            hourly_dwell[hour].append(record['average_dwell_time'])
    
    with open(f"{output_dir}/hourly_patterns.txt", "w") as f:
        f.write("Hourly Activity Patterns\n")
        f.write("=" * 25 + "\n\n")
        f.write("Hour | Customers | Avg Dwell | Activity Bar\n")
        f.write("-" * 45 + "\n")
        
        max_activity = max(hourly_activity.values()) if hourly_activity else 1
        
        for hour in range(24):
            customers = hourly_activity.get(hour, 0)
            avg_dwell = statistics.mean(hourly_dwell[hour]) if hourly_dwell.get(hour) else 0
            bar_length = int((customers / max_activity) * 20)
            activity_bar = "█" * bar_length
            
            f.write(f"{hour:4} | {customers:9} | {avg_dwell:8.1f}s | {activity_bar}\n")

if __name__ == "__main__":
    # File path to queue monitoring data
    queue_file = "data/input/queue_monitoring.jsonl"
    
    try:
        report = generate_queue_analysis_report(queue_file)
        
        # Save report to JSON
        with open("queue_monitoring_analysis_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*50)
        print("QUEUE MONITORING ANALYSIS SUMMARY")
        print("="*50)
        print(f"Total Observations: {report['summary']['total_queue_observations']:,}")
        print(f"System Utilization: {report['summary']['overall_system_utilization']:.1%}")
        print(f"Dwell Time Anomalies: {report['summary']['dwell_time_anomalies_count']}")
        print(f"High Severity Anomalies: {report['summary']['high_severity_dwell_anomalies']}")
        print(f"Congestion Events: {report['summary']['congestion_events_count']}")
        print(f"Stations with Issues: {report['summary']['stations_with_efficiency_issues']}")
        
        # Show station performance
        print(f"\nSTATION PERFORMANCE:")
        for station, stats in report['queue_patterns']['station_statistics'].items():
            print(f"{station}: {stats['utilization_rate']:.1%} utilization, "
                  f"{stats['avg_dwell_time']:.1f}s avg dwell time")
        
        # Show top dwell time anomalies
        if report['dwell_time_anomalies']:
            print(f"\nTOP DWELL TIME ANOMALIES:")
            sorted_anomalies = sorted(report['dwell_time_anomalies'], 
                                    key=lambda x: x['dwell_time'], reverse=True)[:5]
            for i, anomaly in enumerate(sorted_anomalies, 1):
                print(f"{i}. {anomaly['station_id']} at {anomaly['timestamp']}: "
                      f"{anomaly['dwell_time']:.1f}s dwell time "
                      f"({anomaly['anomaly_type']}, {anomaly['severity']} severity)")
        
        print(f"\nDetailed report saved to: queue_monitoring_analysis_report.json")
        
        # Generate text-based visualizations
        queue_data = load_queue_monitoring_data(queue_file)
        visualize_queue_data(queue_data)
        print("Analysis charts saved to: plots/")
        
    except FileNotFoundError:
        print(f"Error: Could not find queue monitoring file at {queue_file}")
        print("Please ensure the file path is correct.")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
