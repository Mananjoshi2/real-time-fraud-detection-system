import yaml
from stream_processor import TransactionStreamProcessor
from fraud_detector import FraudDetector
from dashboard import FraudDashboard
import logging

def load_config():
    with open('config/config.yaml', 'r') as f:
        return yaml.safe_load(f)

def main():
    # Load configuration
    config = load_config()
    
    # Set up logging
    logging.basicConfig(
        level=config['logging']['level'],
        filename=config['logging']['file'],
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Initialize components
    stream_processor = TransactionStreamProcessor(config)
    fraud_detector = FraudDetector(config)
    dashboard = FraudDashboard(config)
    
    # Start dashboard in a separate thread
    import threading
    dashboard_thread = threading.Thread(target=dashboard.run)
    dashboard_thread.start()
    
    # Process transactions
    try:
        for transaction in stream_processor.process_stream():
            # Make prediction
            prediction = fraud_detector.predict(transaction)
            
            if prediction:
                # Update dashboard
                dashboard.update_data(prediction, transaction)
                
                # Log suspicious transactions
                if prediction['is_fraud']:
                    logging.warning(f"Suspicious transaction detected: {transaction['id']}")
    
    except KeyboardInterrupt:
        logging.info("Shutting down fraud detection system")
    
    except Exception as e:
        logging.error(f"System error: {str(e)}")

if __name__ == "__main__":
    main() 