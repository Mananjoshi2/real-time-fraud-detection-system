import pandas as pd
import numpy as np
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

class FeatureEngineer:
    def __init__(self, config):
        self.config = config
        self.user_history = {}
        
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points on Earth"""
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    
    def create_time_features(self, timestamp):
        """Create time-based features from timestamp"""
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return {
            'hour': dt.hour,
            'day_of_week': dt.weekday(),
            'is_weekend': 1 if dt.weekday() >= 5 else 0,
            'is_night': 1 if (dt.hour >= 22 or dt.hour <= 5) else 0
        }
    
    def update_user_history(self, transaction):
        """Update user transaction history"""
        user_id = transaction['user_id']
        if user_id not in self.user_history:
            self.user_history[user_id] = []
        self.user_history[user_id].append(transaction)
        
        # Keep only recent history
        cutoff = pd.Timestamp.now() - pd.Timedelta(hours=self.config['features']['time_window'])
        self.user_history[user_id] = [
            t for t in self.user_history[user_id]
            if pd.Timestamp(t['timestamp']) > cutoff
        ]
    
    def create_historical_features(self, transaction):
        """Create features based on user history"""
        user_id = transaction['user_id']
        history = self.user_history.get(user_id, [])
        
        if not history:
            return {
                'avg_amount': 0,
                'transaction_frequency': 0,
                'amount_deviation': 0
            }
        
        amounts = [t['amount'] for t in history]
        avg_amount = np.mean(amounts)
        
        return {
            'avg_amount': avg_amount,
            'transaction_frequency': len(history) / 24,  # transactions per hour
            'amount_deviation': abs(transaction['amount'] - avg_amount) / (avg_amount + 1e-10)
        }
    
    def create_location_features(self, transaction):
        """Create location-based features"""
        user_id = transaction['user_id']
        history = self.user_history.get(user_id, [])
        
        if not history:
            return {
                'distance_from_last': 0,
                'speed_from_last': 0
            }
        
        last_transaction = history[-1]
        distance = self.haversine_distance(
            transaction['latitude'], transaction['longitude'],
            last_transaction['latitude'], last_transaction['longitude']
        )
        
        time_diff = (pd.Timestamp(transaction['timestamp']) - 
                    pd.Timestamp(last_transaction['timestamp'])).total_seconds() / 3600  # hours
        
        speed = distance / (time_diff + 1e-10)  # km/h
        
        return {
            'distance_from_last': distance,
            'speed_from_last': speed
        }
    
    def engineer_features(self, transaction):
        """Create all features for a transaction"""
        self.update_user_history(transaction)
        
        features = {}
        features.update(self.create_time_features(transaction['timestamp']))
        features.update(self.create_historical_features(transaction))
        features.update(self.create_location_features(transaction))
        
        return features
