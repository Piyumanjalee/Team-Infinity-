#!/usr/bin/env python3
"""
POS Transactions Analysis
=========================

This script analyzes Point of Sale transaction data to detect:
- Suspicious transaction patterns
- Weight discrepancies (actual vs expected weight)
- Barcode switching attempts
- Self-checkout fraud patterns
- Price manipulation attempts

Data Format: JSONL with transaction details including customer, product, price, weight
"""

import json
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple, Set
from collections import defaultdict

# @algorithm WeightDiscrepancyDetection | Detects suspicious weight differences in transactions
class WeightDiscrepancyDetector:
    def __init__(self, tolerance_percentage: float = 15.0):
        """
        Initialize weight discrepancy detector
        
        Args:
            tolerance_percentage: Acceptable weight variance percentage
        """
        self.tolerance = tolerance_percentage
        
    def detect_weight_discrepancies(self, transactions_df: pd.DataFrame) -> List[Dict]:
        """
        Detect transactions with suspicious weight discrepancies
        
        Returns:
            List of suspicious transactions
        """
        discrepancies = []
        
        # Group by SKU to establish expected weights
        sku_weights = transactions_df.groupby('sku')['expected_weight'].first().to_dict()
        
        for _, transaction in transactions_df.iterrows():
            if pd.isna(transaction['actual_weight']) or pd.isna(transaction['expected_weight']):
                continue
                
            expected = transaction['expected_weight']
            actual = transaction['actual_weight']
            
            if expected > 0:  # Avoid division by zero
                weight_diff_pct = abs((actual - expected) / expected) * 100
                
                if weight_diff_pct > self.tolerance:
                    discrepancies.append({
                        'timestamp': transaction['timestamp'],
                        'customer_id': transaction['customer_id'],
                        'station_id': transaction['station_id'],
                        'sku': transaction['sku'],
                        'product_name': transaction['product_name'],
                        'expected_weight': expected,
                        'actual_weight': actual,
                        'weight_difference_pct': weight_diff_pct,
                        'price': transaction['price'],
                        'severity': 'HIGH' if weight_diff_pct > 50 else 'MEDIUM'
                    })
        
        return discrepancies

# @algorithm BarcodeSwappingDetection | Identifies potential barcode switching fraud
class BarcodeSwappingDetector:
    def __init__(self):
        """Initialize barcode swapping detector"""
        pass
        
    def detect_barcode_swapping(self, transactions_df: pd.DataFrame) -> List[Dict]:
        """
        Detect potential barcode swapping by analyzing price-weight relationships
        
        Returns:
            List of suspicious transactions indicating possible barcode swapping
        """
        suspicious_transactions = []
        
        # Calculate price per gram for each product
        price_per_gram = {}
        for _, transaction in transactions_df.iterrows():
            sku = transaction['sku']
            if transaction['expected_weight'] > 0:
                ppg = transaction['price'] / transaction['expected_weight']
                if sku not in price_per_gram:
                    price_per_gram[sku] = []
                price_per_gram[sku].append(ppg)
        
        # Calculate average price per gram for each SKU
        avg_price_per_gram = {}
        for sku, prices in price_per_gram.items():
            avg_price_per_gram[sku] = np.mean(prices)
        
        # Sort SKUs by price per gram to identify cheap vs expensive items
        sorted_skus = sorted(avg_price_per_gram.items(), key=lambda x: x[1])
        
        # Look for high-weight items sold at low prices (potential swapping)
        for _, transaction in transactions_df.iterrows():
            sku = transaction['sku']
            actual_weight = transaction['actual_weight']
            
            if pd.isna(actual_weight) or actual_weight == 0:
                continue
                
            current_ppg = transaction['price'] / actual_weight
            expected_ppg = avg_price_per_gram.get(sku, current_ppg)
            
            # Flag if current price per gram is significantly lower than expected
            if expected_ppg > 0 and current_ppg < expected_ppg * 0.5:  # 50% or less
                suspicious_transactions.append({
                    'timestamp': transaction['timestamp'],
                    'customer_id': transaction['customer_id'],
                    'station_id': transaction['station_id'],
                    'sku': transaction['sku'],
                    'product_name': transaction['product_name'],
                    'price': transaction['price'],
                    'actual_weight': actual_weight,
                    'current_price_per_gram': current_ppg,
                    'expected_price_per_gram': expected_ppg,
                    'price_ratio': current_ppg / expected_ppg,
                    'suspicion_reason': 'LOW_PRICE_PER_WEIGHT'
                })
        
        return suspicious_transactions

# @algorithm CustomerBehaviorAnalysis | Analyzes customer purchasing patterns for anomalies
class CustomerBehaviorAnalyzer:
    def __init__(self):
        """Initialize customer behavior analyzer"""
        pass
        
    def analyze_customer_patterns(self, transactions_df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """
        Analyze customer behavior patterns to identify suspicious activity
        
        Returns:
            Dictionary with different types of suspicious customer behaviors
        """
        results = {
            'frequent_discrepancy_customers': [],
            'high_value_suspicious_transactions': [],
            'rapid_transaction_customers': []
        }
        
        # Group transactions by customer
        customer_groups = transactions_df.groupby('customer_id')
        
        for customer_id, customer_transactions in customer_groups:
            customer_transactions = customer_transactions.sort_values('timestamp')
            
            # Check for customers with frequent weight discrepancies
            discrepancy_count = 0
            total_transactions = len(customer_transactions)
            
            for _, transaction in customer_transactions.iterrows():
                if not pd.isna(transaction['actual_weight']) and not pd.isna(transaction['expected_weight']):
                    if transaction['expected_weight'] > 0:
                        weight_diff = abs((transaction['actual_weight'] - transaction['expected_weight']) / transaction['expected_weight']) * 100
                        if weight_diff > 15:  # 15% threshold
                            discrepancy_count += 1
            
            if total_transactions > 3 and discrepancy_count / total_transactions > 0.5:  # More than 50% discrepancies
                results['frequent_discrepancy_customers'].append({
                    'customer_id': customer_id,
                    'total_transactions': total_transactions,
                    'discrepancy_count': discrepancy_count,
                    'discrepancy_rate': discrepancy_count / total_transactions,
                    'total_value': customer_transactions['price'].sum()
                })
            
            # Check for high-value transactions with suspicions
            high_value_transactions = customer_transactions[customer_transactions['price'] > 500]
            for _, transaction in high_value_transactions.iterrows():
                if not pd.isna(transaction['actual_weight']) and not pd.isna(transaction['expected_weight']):
                    if transaction['expected_weight'] > 0:
                        weight_diff = abs((transaction['actual_weight'] - transaction['expected_weight']) / transaction['expected_weight']) * 100
                        if weight_diff > 25:  # High threshold for expensive items
                            results['high_value_suspicious_transactions'].append({
                                'customer_id': customer_id,
                                'timestamp': transaction['timestamp'],
                                'sku': transaction['sku'],
                                'product_name': transaction['product_name'],
                                'price': transaction['price'],
                                'weight_discrepancy_pct': weight_diff,
                                'station_id': transaction['station_id']
                            })
            
            # Check for rapid consecutive transactions (potential scanner avoidance)
            if len(customer_transactions) > 1:
                time_diffs = []
                timestamps = pd.to_datetime(customer_transactions['timestamp'])
                for i in range(1, len(timestamps)):
                    time_diff = (timestamps.iloc[i] - timestamps.iloc[i-1]).total_seconds()
                    time_diffs.append(time_diff)
                
                avg_time_between = np.mean(time_diffs) if time_diffs else 0
                if avg_time_between < 10 and len(customer_transactions) > 5:  # Less than 10 seconds between items, 5+ items
                    results['rapid_transaction_customers'].append({
                        'customer_id': customer_id,
                        'total_items': len(customer_transactions),
                        'avg_seconds_between_items': avg_time_between,
                        'total_value': customer_transactions['price'].sum(),
                        'session_start': customer_transactions['timestamp'].min(),
                        'session_end': customer_transactions['timestamp'].max()
                    })
        
        return results

def load_pos_transactions(file_path: str) -> pd.DataFrame:
    """Load POS transaction data from JSONL file"""
    transactions = []
    
    with open(file_path, 'r') as f:
        for line in f:
            record = json.loads(line.strip())
            
            # Flatten transaction data
            transaction = {
                'timestamp': record['timestamp'],
                'station_id': record['station_id'],
                'status': record['status'],
                'customer_id': record['data']['customer_id'],
                'sku': record['data']['sku'],
                'product_name': record['data']['product_name'],
                'barcode': record['data']['barcode'],
                'price': record['data']['price'],
                'expected_weight': record['data']['weight_g'],  # From product spec
                'actual_weight': record['data'].get('weight_g', record['data']['weight_g'])  # Actual scanned weight
            }
            
            # Handle cases where actual weight might differ (like the Coca-Cola example)
            # In real scenario, this would come from scale data
            if 'actual_weight_g' in record['data']:
                transaction['actual_weight'] = record['data']['actual_weight_g']
            
            transactions.append(transaction)
    
    df = pd.DataFrame(transactions)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df.sort_values('timestamp').reset_index(drop=True)

def analyze_transaction_patterns(df: pd.DataFrame) -> Dict:
    """Analyze overall transaction patterns and statistics"""
    analysis = {}
    
    # Basic statistics
    analysis['summary'] = {
        'total_transactions': len(df),
        'unique_customers': df['customer_id'].nunique(),
        'unique_products': df['sku'].nunique(),
        'unique_stations': df['station_id'].nunique(),
        'total_revenue': float(df['price'].sum()),
        'avg_transaction_value': float(df['price'].mean()),
        'time_range': {
            'start': df['timestamp'].min().isoformat(),
            'end': df['timestamp'].max().isoformat()
        }
    }
    
    # Customer analysis
    customer_stats = df.groupby('customer_id').agg({
        'price': ['sum', 'count', 'mean'],
        'timestamp': ['min', 'max']
    }).round(2)
    
    customer_stats.columns = ['total_spent', 'transaction_count', 'avg_transaction', 'first_transaction', 'last_transaction']
    
    analysis['top_customers'] = customer_stats.nlargest(10, 'total_spent').to_dict('index')
    
    # Product analysis
    product_stats = df.groupby(['sku', 'product_name']).agg({
        'price': ['sum', 'count', 'mean'],
        'customer_id': 'nunique'
    }).round(2)
    
    product_stats.columns = ['total_revenue', 'units_sold', 'avg_price', 'unique_customers']
    analysis['top_products'] = product_stats.nlargest(10, 'total_revenue').to_dict('index')
    
    # Station analysis
    station_stats = df.groupby('station_id').agg({
        'price': ['sum', 'count'],
        'customer_id': 'nunique'
    }).round(2)
    
    station_stats.columns = ['total_revenue', 'transaction_count', 'unique_customers']
    analysis['station_performance'] = station_stats.to_dict('index')
    
    return analysis

def generate_pos_analysis_report(file_path: str) -> Dict:
    """Generate comprehensive POS transaction analysis report"""
    print("Loading POS transaction data...")
    df = load_pos_transactions(file_path)
    
    print("Analyzing transaction patterns...")
    patterns = analyze_transaction_patterns(df)
    
    print("Detecting weight discrepancies...")
    weight_detector = WeightDiscrepancyDetector(tolerance_percentage=15.0)
    weight_discrepancies = weight_detector.detect_weight_discrepancies(df)
    
    print("Detecting barcode swapping...")
    barcode_detector = BarcodeSwappingDetector()
    barcode_suspicious = barcode_detector.detect_barcode_swapping(df)
    
    print("Analyzing customer behavior...")
    behavior_analyzer = CustomerBehaviorAnalyzer()
    customer_analysis = behavior_analyzer.analyze_customer_patterns(df)
    
    # Compile report
    report = {
        'analysis_timestamp': datetime.now().isoformat(),
        'data_source': file_path,
        'transaction_patterns': patterns,
        'weight_discrepancies': weight_discrepancies,
        'suspected_barcode_swapping': barcode_suspicious,
        'customer_behavior_analysis': customer_analysis,
        'summary': {
            'total_weight_discrepancies': len(weight_discrepancies),
            'high_severity_weight_issues': len([d for d in weight_discrepancies if d['severity'] == 'HIGH']),
            'suspected_barcode_swapping_count': len(barcode_suspicious),
            'frequent_discrepancy_customers': len(customer_analysis['frequent_discrepancy_customers']),
            'rapid_transaction_customers': len(customer_analysis['rapid_transaction_customers']),
            'high_value_suspicious_transactions': len(customer_analysis['high_value_suspicious_transactions'])
        }
    }
    
    return report

def visualize_pos_data(df: pd.DataFrame, output_dir: str = "plots"):
    """Generate visualization plots for POS transaction data"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Plot 1: Transaction volume over time
    plt.figure(figsize=(12, 6))
    hourly_transactions = df.set_index('timestamp').resample('H').size()
    hourly_transactions.plot(kind='line', linewidth=2)
    plt.title('Transaction Volume Over Time (Hourly)')
    plt.xlabel('Time')
    plt.ylabel('Number of Transactions')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/pos_transaction_volume.png")
    plt.close()
    
    # Plot 2: Revenue by customer
    plt.figure(figsize=(10, 6))
    customer_revenue = df.groupby('customer_id')['price'].sum().nlargest(15)
    customer_revenue.plot(kind='bar')
    plt.title('Top 15 Customers by Revenue')
    plt.xlabel('Customer ID')
    plt.ylabel('Total Revenue')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/pos_top_customers.png")
    plt.close()
    
    # Plot 3: Price distribution
    plt.figure(figsize=(10, 6))
    plt.hist(df['price'], bins=50, edgecolor='black', alpha=0.7)
    plt.title('Transaction Price Distribution')
    plt.xlabel('Price')
    plt.ylabel('Frequency')
    plt.axvline(df['price'].mean(), color='red', linestyle='--', label=f'Mean: ${df["price"].mean():.2f}')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/pos_price_distribution.png")
    plt.close()

if __name__ == "__main__":
    # File path to POS transactions
    pos_file = "data/input/pos_transactions.jsonl"
    
    try:
        report = generate_pos_analysis_report(pos_file)
        
        # Save report to JSON
        with open("pos_analysis_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*50)
        print("POS TRANSACTION ANALYSIS SUMMARY")
        print("="*50)
        print(f"Total Transactions: {report['transaction_patterns']['summary']['total_transactions']:,}")
        print(f"Unique Customers: {report['transaction_patterns']['summary']['unique_customers']}")
        print(f"Total Revenue: ${report['transaction_patterns']['summary']['total_revenue']:,.2f}")
        print(f"Average Transaction: ${report['transaction_patterns']['summary']['avg_transaction_value']:.2f}")
        
        print(f"\nFRAUD DETECTION RESULTS:")
        print(f"Weight Discrepancies: {report['summary']['total_weight_discrepancies']}")
        print(f"High Severity Weight Issues: {report['summary']['high_severity_weight_issues']}")
        print(f"Suspected Barcode Swapping: {report['summary']['suspected_barcode_swapping_count']}")
        print(f"Customers with Frequent Issues: {report['summary']['frequent_discrepancy_customers']}")
        print(f"Rapid Transaction Customers: {report['summary']['rapid_transaction_customers']}")
        
        # Show top suspicious activities
        if report['weight_discrepancies']:
            print(f"\nTOP WEIGHT DISCREPANCIES:")
            sorted_discrepancies = sorted(report['weight_discrepancies'], 
                                        key=lambda x: x['weight_difference_pct'], reverse=True)[:5]
            for i, disc in enumerate(sorted_discrepancies, 1):
                print(f"{i}. Customer {disc['customer_id']}: {disc['product_name']} "
                      f"({disc['weight_difference_pct']:.1f}% weight diff)")
        
        print(f"\nDetailed report saved to: pos_analysis_report.json")
        
        # Generate visualizations
        df = load_pos_transactions(pos_file)
        visualize_pos_data(df)
        print("Visualization plots saved to: plots/")
        
    except FileNotFoundError:
        print(f"Error: Could not find POS transactions file at {pos_file}")
        print("Please ensure the file path is correct.")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
