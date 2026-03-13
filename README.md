## Credit Card Fraud Detection Demo

An AI-powered credit card fraud detection system that started as a Kafka‑streaming project and is now equipped with a **demo mode** for easy portfolio deployment. The demo simulates a real-time fraud monitoring dashboard using synthetic transactions and a trained XGBoost model.

### Architecture

- **Data & Features**: Synthetic transactions generated into `data/training_data.csv` with engineered features such as time-of-day, weekend/night flags, spending patterns, and location‑style signals.
- **Model Training**: `src/train_model.py` trains an `XGBoost` classifier on these features, scales inputs with `StandardScaler`, and saves both the model (`models/fraud_detector.pkl`) and scaler (`models/scaler.pkl`).
- **Inference & Scoring**: `src/fraud_detector.py` loads the trained model and scaler and scores each incoming transaction, returning fraud probability and a fraud flag.
- **Dashboard**: `src/dashboard.py` exposes a Dash app that shows:
  - Fraud probability over time
  - Transaction amount distribution
- **Original Streaming Path (Kafka)**: `src/stream_processor.py` consumes from Kafka and uses `src/feature_engineering.py` to compute real-time features, orchestrated by `src/main.py`.
- **Demo Mode (No Kafka)**: `demo.py` reuses the same detector and dashboard, but feeds them a loop of synthetic transactions instead of Kafka messages.

### Features

- Supervised fraud detection with XGBoost
- Config‑driven (`config/config.yaml`) model, dashboard, and logging settings
- Real-time style dashboard with Plotly/Dash
- Synthetic data generation for safe experimentation
- Pluggable streaming backends:
  - Kafka production path (kept intact)
  - Demo mode using synthetic transactions (no infrastructure required)

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

3. **Generate synthetic training data** (if you don't already have `data/training_data.csv`):

```bash
python src/generate_sample_data.py
```

### Training the Model

1. Make sure synthetic data exists:

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

### Running Demo Mode (No Kafka)

Demo mode simulates a streaming system by feeding the model and dashboard a sequence of synthetic transactions.

1. Ensure you have:
   - `data/training_data.csv` (from `src/generate_sample_data.py`)
   - `models/fraud_detector.pkl` and `models/scaler.pkl` (from `src/train_model.py`)

2. Start demo mode from the project root:

```bash
python demo.py
```

3. Open the dashboard in your browser:

- By default: `http://localhost:8050`

The dashboard will:

- Continuously ingest synthetic transactions from `data/training_data.csv`
- Run fraud prediction on each one
- Update plots in near‑real time

### Original Kafka Streaming Mode (Optional)

The original streaming architecture is preserved for reference:

- `src/stream_processor.py`: Kafka consumer + real-time feature engineering.
- `src/feature_engineering.py`: time, historical, and location‑based features.
- `src/main.py`: wires Kafka stream → `FraudDetector` → `FraudDashboard`.

To run this mode you would need a Kafka cluster and topic configured as in `config/config.yaml`. For portfolio/demo purposes you can stick with `demo.py`.

### Deployment Notes for Render

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
  - Render will set a `$PORT` environment variable; `dashboard.py` reads this automatically and binds the Dash app to `0.0.0.0:$PORT`.
  - No Kafka is required for the demo service.

**Recommended steps**:

1. Push this project to GitHub.
2. Create a new **Web Service** in Render and point it at the repo.
3. Set the build and start commands as shown above.
4. Deploy; once live, open the Render URL to see the real‑time fraud detection dashboard driven by synthetic data.

