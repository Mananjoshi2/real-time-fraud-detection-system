import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import pickle
import yaml
import logging
from pathlib import Path

class ModelTrainer:
    def __init__(self, config_path):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Set up logging
        logging.basicConfig(
            level=self.config['logging']['level'],
            filename=self.config['logging']['file'],
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        self.feature_columns = [
            'amount', 'hour', 'day_of_week', 'is_weekend', 'is_night',
            'avg_amount', 'transaction_frequency', 'amount_deviation',
            'distance_from_last', 'speed_from_last'
        ]
        
        self.scaler = StandardScaler()
    
    def prepare_data(self, data_path):
        """Load and prepare training data"""
        try:
            # Load data
            df = pd.read_csv(data_path)
            
            # Ensure required columns exist
            required_columns = self.feature_columns + ['is_fraud']
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Split features and target
            X = df[self.feature_columns]
            y = df['is_fraud']
            
            # Split into train and test sets
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            logging.info("Data preparation completed successfully")
            return X_train_scaled, X_test_scaled, y_train, y_test
            
        except Exception as e:
            logging.error(f"Error preparing data: {str(e)}")
            raise
    
    def train(self, X_train, y_train, X_test, y_test):
        """Train the XGBoost model"""
        try:
            # Calculate class weights
            n_neg = np.sum(y_train == 0)
            n_pos = np.sum(y_train == 1)
            scale_pos_weight = n_neg / n_pos
            
            # Set up model parameters (no early stopping here to avoid
            # version-specific keyword issues in different XGBoost builds)
            params = {
                **self.config['model']['params'],
                'scale_pos_weight': scale_pos_weight,
            }
            
            # Create and train model
            model = xgb.XGBClassifier(**params)
            model.fit(X_train, y_train)
            
            # Save model and scaler
            self.save_model(model)
            self.save_scaler()
            
            logging.info("Model training completed successfully")
            return model
            
        except Exception as e:
            logging.error(f"Error training model: {str(e)}")
            raise
    
    def save_model(self, model):
        """Save the trained model"""
        model_path = self.config['model']['model_path']
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        logging.info(f"Model saved to {model_path}")
    
    def save_scaler(self):
        """Save the fitted scaler"""
        scaler_path = Path(self.config['model']['model_path']).parent / 'scaler.pkl'
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        logging.info(f"Scaler saved to {scaler_path}")

def main():
    # Initialize trainer
    trainer = ModelTrainer('config/config.yaml')
    
    try:
        # Prepare data
        logging.info("Starting data preparation...")
        X_train, X_test, y_train, y_test = trainer.prepare_data('data/training_data.csv')
        
        # Train model
        logging.info("Starting model training...")
        model = trainer.train(X_train, y_train, X_test, y_test)
        
        logging.info("Model training pipeline completed successfully")
        
    except Exception as e:
        logging.error(f"Training pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 