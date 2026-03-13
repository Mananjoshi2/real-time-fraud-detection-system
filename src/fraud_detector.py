import pickle
import logging
from pathlib import Path

import pandas as pd


class FraudDetector:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.scaler = None
        self.feature_columns = [
            'amount', 'hour', 'day_of_week', 'is_weekend', 'is_night',
            'avg_amount', 'transaction_frequency', 'amount_deviation',
            'distance_from_last', 'speed_from_last'
        ]

        self.load_model()
        self.load_scaler()

    def load_model(self):
        """Load the trained model"""
        try:
            with open(self.config['model']['model_path'], 'rb') as f:
                self.model = pickle.load(f)
            logging.info("Model loaded successfully")
        except Exception as e:
            logging.error(f"Error loading model: {str(e)}")
            raise

    def load_scaler(self):
        """Load the fitted scaler saved during training"""
        try:
            scaler_path = Path(self.config['model']['model_path']).parent / 'scaler.pkl'
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            logging.info(f"Scaler loaded successfully from {scaler_path}")
        except Exception as e:
            logging.error(f"Error loading scaler: {str(e)}")
            raise

    def prepare_features(self, transaction):
        """Prepare features for prediction"""
        features = pd.DataFrame(
            [[transaction[col] for col in self.feature_columns]],
            columns=self.feature_columns
        )
        return features

    def predict(self, transaction):
        """Make fraud prediction for a transaction"""
        try:
            features = self.prepare_features(transaction)
            features_scaled = self.scaler.transform(features)

            fraud_probability = self.model.predict_proba(features_scaled)[0][1]

            prediction = {
                'transaction_id': transaction['id'],
                'fraud_probability': float(fraud_probability),
                'is_fraud': fraud_probability > 0.5,
                'timestamp': transaction['timestamp']
            }

            return prediction

        except Exception as e:
            logging.error(f"Error making prediction: {str(e)}")
            return None
