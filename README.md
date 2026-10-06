## Real-Time Fraud Detection System

**Live demo:** [real-time-fraud-detection-system.onrender.com](https://real-time-fraud-detection-system.onrender.com/) *(hosted on Render's free tier — may take a few seconds to spin up on first load)*

A machine learning system for detecting fraudulent credit card transactions in real time. It combines a Kafka-based streaming pipeline, engineered transaction features, and an XGBoost classifier to score transactions as they arrive, with a live Plotly/Dash dashboard for monitoring fraud probability and transaction activity.

The system is built around a production-style streaming architecture (Kafka consumer → feature engineering → model inference → dashboard) and includes a self-contained simulation mode that runs the full pipeline end-to-end without requiring a Kafka cluster — useful for local development, testing, and deployment in environments where standing up streaming infrastructure isn't practical.

### Architecture

- **Data & Features**: Transaction data in `data/training_data.csv` with engineered features such as time-of-day, weekend/night flags, spending patterns, and location-style signals.
- **Model Training**: `src/train_model.py` trains an `XGBoost` classifier on these features, scales inputs with `StandardScaler`, and saves both the model (`models/fraud_detector.pkl`) and scaler (`models/scaler.pkl`).
- **Inference & Scoring**: `src/fraud_detector.py` loads the trained model and scaler and scores each incoming transaction, returning a fraud probability and a fraud flag.
- **Streaming Pipeline (Kafka)**: `src/stream_processor.py` consumes transactions from Kafka and uses `src/feature_engineering.py` to compute real-time features (time-based, historical, and location-based), orchestrated by `src/main.py`.
- **Dashboard**: `src/dashboard.py` runs a Dash application that visualizes:
  - Fraud probability over time
  - Transaction amount distribution
- **Simulation Mode**: `demo.py` runs the same detector and dashboard against a continuous feed of generated transactions, so the full pipeline can be exercised without a Kafka deployment.

### Features

- Supervised fraud detection with XGBoost
- Config-driven (`config/config.yaml`) model, dashboard, and logging settings
- Real-time monitoring dashboard with Plotly/Dash
- Synthetic transaction generator for training and testing without production data
- Two execution modes:
  - Kafka-backed streaming pipeline for production-style deployment
  - Standalone simulation mode with no external infrastructure dependencies

### Local Setup

1. **Clone and create a virtual environment** (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# .\venv\Scripts\activate  # Windows
```

2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

3. **Generate training data** (if you don't already have `data/training_data.csv`):

```bash
python src/generate_sample_data.py
```

### Training the Model

1. Make sure training data exists:

```bash
python src/generate_sample_data.py
```

2. Train the model and save both model and scaler:

```bash
python src/train_model.py
```

On success you should see:

- `models/fraud_detector.pkl` – trained XGBoost model
- `models/scaler.pkl` – fitted `StandardScaler`

### Kafka Streaming Mode

This is the primary, production-style execution path.

1. Have a Kafka cluster and topic available, matching `config/config.yaml` (`bootstrap_servers`, `topic`, `group_id`).
2. Ensure the model and scaler exist (`models/fraud_detector.pkl`, `models/scaler.pkl`).
3. Run the pipeline:

```bash
python src/main.py
```

This wires the Kafka consumer (`src/stream_processor.py`) through real-time feature engineering (`src/feature_engineering.py`) into the fraud detector and dashboard.

### Standalone Simulation Mode (No Kafka Required)

For local development, testing, or environments without a Kafka deployment, `demo.py` runs the same detection and dashboard logic against a generated transaction feed.

1. Ensure you have:
   - `data/training_data.csv` (from `src/generate_sample_data.py`)
   - `models/fraud_detector.pkl` and `models/scaler.pkl` (from `src/train_model.py`)

2. Run it from the project root:

```bash
python demo.py
```

3. Open the dashboard in your browser:

- By default: `http://localhost:8050`

This mode continuously feeds transactions through the trained model and updates the dashboard in near real time, exercising the same scoring and visualization code paths as the Kafka pipeline.

### Deployment Notes (Render)

**Service type**: Python web service

- **Build command**:

```bash
pip install -r requirements.txt
```

- **Start command**:

```bash
python demo.py
```

- **Environment**:
  - Render sets a `$PORT` environment variable; `dashboard.py` reads this automatically and binds the Dash app to `0.0.0.0:$PORT`.
  - This start command runs the standalone simulation mode, so no Kafka cluster is required for the hosted deployment.
