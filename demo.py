import os
import sys
import time
import logging
from pathlib import Path

import pandas as pd
import yaml


# Ensure the src/ directory is on the import path so we can
# reuse the existing modules without changing their imports.
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fraud_detector import FraudDetector  # noqa: E402
from dashboard import FraudDashboard  # noqa: E402


def load_config():
    with open(PROJECT_ROOT / "config" / "config.yaml", "r") as f:
        return yaml.safe_load(f)


def load_demo_data():
    """
    Load synthetic transactions for demo mode.

    We reuse the saved training data as a source of realistic-looking
    feature rows and turn each row into a "streamed" transaction.
    """
    data_path = PROJECT_ROOT / "data" / "training_data.csv"
    if not data_path.exists():
        raise FileNotFoundError(
            f"Expected demo data at {data_path}, but it was not found. "
            f"Generate it first with: python src/generate_sample_data.py"
        )

    return pd.read_csv(data_path)


def build_transaction_stream(df: pd.DataFrame):
    """
    Turn a static DataFrame of feature rows into an iterator of
    transaction dictionaries compatible with FraudDetector.
    """
    # We just assign synthetic IDs and timestamps in order.
    base_timestamp = pd.Timestamp.utcnow()

    for idx, row in df.iterrows():
        timestamp = base_timestamp + pd.Timedelta(seconds=idx)
        transaction = {
            "id": int(idx),
            "timestamp": timestamp.isoformat(),
            "amount": float(row["amount"]),
            "hour": int(row["hour"]),
            "day_of_week": int(row["day_of_week"]),
            "is_weekend": int(row["is_weekend"]),
            "is_night": int(row["is_night"]),
            "avg_amount": float(row["avg_amount"]),
            "transaction_frequency": float(row["transaction_frequency"]),
            "amount_deviation": float(row["amount_deviation"]),
            "distance_from_last": float(row["distance_from_last"]),
            "speed_from_last": float(row["speed_from_last"]),
        }
        yield transaction


def main():
    config = load_config()

    # Set up logging for demo mode
    log_file = config["logging"]["file"]
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=config["logging"]["level"],
        filename=log_file,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    logging.info("Starting fraud detection demo mode")

    # Load model + scaler and dashboard
    fraud_detector = FraudDetector(config)
    dashboard = FraudDashboard(config)

    # Start the Dash app in a separate thread so we can feed it data
    import threading

    dashboard_thread = threading.Thread(target=dashboard.run, daemon=True)
    dashboard_thread.start()

    # Load synthetic data and stream it to the model/dashboard
    df = load_demo_data()
    delay_seconds = float(config["dashboard"].get("refresh_interval", 1))

    try:
        for transaction in build_transaction_stream(df):
            prediction = fraud_detector.predict(transaction)
            if prediction is not None:
                dashboard.update_data(prediction, transaction)

                if prediction["is_fraud"]:
                    logging.warning(
                        f"Suspicious transaction detected in demo mode: {transaction['id']}"
                    )

            # Small delay to simulate real-time streaming
            time.sleep(delay_seconds)

        # Keep the app running after the last transaction so the dashboard
        # stays visible in demo mode.
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("Shutting down demo mode")


if __name__ == "__main__":
    main()

