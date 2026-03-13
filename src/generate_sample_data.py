import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(n_samples=1000):
    np.random.seed(42)
    
    # Generate timestamps
    base_time = datetime.now()
    timestamps = [base_time + timedelta(hours=i) for i in range(n_samples)]
    
    # Generate data
    data = {
        'amount': np.random.lognormal(4, 1, n_samples),  # Transaction amounts
        'hour': [t.hour for t in timestamps],
        'day_of_week': [t.weekday() for t in timestamps],
        'is_weekend': [1 if t.weekday() >= 5 else 0 for t in timestamps],
        'is_night': [1 if (t.hour >= 22 or t.hour <= 5) else 0 for t in timestamps],
        'avg_amount': np.random.lognormal(4, 0.5, n_samples),
        'transaction_frequency': np.random.uniform(0, 5, n_samples),
        'amount_deviation': np.random.uniform(0, 2, n_samples),
        'distance_from_last': np.random.uniform(0, 200, n_samples),
        'speed_from_last': np.random.uniform(0, 100, n_samples)
    }
    
    # Generate fraud labels (about 1% fraud rate)
    data['is_fraud'] = np.random.choice(
        [0, 1], 
        size=n_samples, 
        p=[0.99, 0.01]
    )
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    return df

if __name__ == "__main__":
    # Generate sample data
    df = generate_sample_data(10000)
    
    # Create data directory if it doesn't exist
    import os
    os.makedirs('data', exist_ok=True)
    
    # Save to CSV
    df.to_csv('data/training_data.csv', index=False)
    print("Sample data generated and saved to data/training_data.csv") 