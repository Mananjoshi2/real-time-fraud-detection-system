from kafka import KafkaConsumer
import json
from feature_engineering import FeatureEngineer
import logging

class TransactionStreamProcessor:
    def __init__(self, config):
        self.config = config
        self.kafka_config = config['kafka']
        self.feature_engineer = FeatureEngineer(config)
        
        # Set up logging
        logging.basicConfig(
            level=config['logging']['level'],
            filename=config['logging']['file'],
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Initialize Kafka consumer
        self.consumer = KafkaConsumer(
            self.kafka_config['topic'],
            bootstrap_servers=self.kafka_config['bootstrap_servers'],
            group_id=self.kafka_config['group_id'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
    
    def validate_transaction(self, transaction):
        """Validate transaction data"""
        required_fields = [
            'id', 'user_id', 'merchant_id', 'amount',
            'timestamp', 'latitude', 'longitude', 'card_id'
        ]
        
        return all(field in transaction for field in required_fields)
    
    def process_stream(self):
        """Process incoming transaction stream"""
        for message in self.consumer:
            transaction = message.value
            
            try:
                if not self.validate_transaction(transaction):
                    logging.warning(f"Invalid transaction format: {transaction}")
                    continue
                
                # Engineer features
                features = self.feature_engineer.engineer_features(transaction)
                
                # Combine original transaction with features
                enriched_transaction = {**transaction, **features}
                
                yield enriched_transaction
                
            except Exception as e:
                logging.error(f"Error processing transaction: {str(e)}")
                continue
