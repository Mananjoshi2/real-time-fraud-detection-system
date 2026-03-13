import os
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from collections import deque
import pandas as pd


class FraudDashboard:
    def __init__(self, config):
        self.config = config
        self.max_points = config['dashboard']['max_points']

        # Initialize data storage
        self.timestamps = deque(maxlen=self.max_points)
        self.fraud_probs = deque(maxlen=self.max_points)
        self.transaction_amounts = deque(maxlen=self.max_points)

        # Initialize Dash app
        self.app = dash.Dash(__name__)
        self.setup_layout()

    def setup_layout(self):
        """Set up the dashboard layout"""
        self.app.layout = html.Div([
            html.H1('Real-time Fraud Detection Dashboard'),

            html.Div([
                dcc.Graph(id='live-fraud-graph'),
                dcc.Graph(id='amount-distribution'),
                dcc.Interval(
                    id='interval-component',
                    interval=self.config['dashboard']['refresh_interval'] * 1000
                )
            ])
        ])

        self.setup_callbacks()

    def setup_callbacks(self):
        """Set up dashboard callbacks"""
        @self.app.callback(
            [Output('live-fraud-graph', 'figure'),
             Output('amount-distribution', 'figure')],
            Input('interval-component', 'n_intervals')
        )
        def update_graphs(_):
            fraud_fig = go.Figure(data=[go.Scatter(
                x=list(self.timestamps),
                y=list(self.fraud_probs),
                mode='lines+markers',
                name='Fraud Probability'
            )])

            fraud_fig.update_layout(
                title='Fraud Probability Over Time',
                xaxis_title='Time',
                yaxis_title='Fraud Probability'
            )

            amount_fig = go.Figure(data=[go.Histogram(
                x=list(self.transaction_amounts),
                nbinsx=30,
                name='Transaction Amounts'
            )])

            amount_fig.update_layout(
                title='Transaction Amount Distribution',
                xaxis_title='Amount',
                yaxis_title='Count'
            )

            return fraud_fig, amount_fig

    def update_data(self, prediction, transaction):
        """Update dashboard data with new prediction"""
        self.timestamps.append(pd.Timestamp(prediction['timestamp']))
        self.fraud_probs.append(prediction['fraud_probability'])
        self.transaction_amounts.append(transaction['amount'])

    def run(self):
        """Run the dashboard"""
        port = int(os.environ.get("PORT", self.config['dashboard']['port']))
        self.app.run(
            debug=False,
            host="0.0.0.0",
            port=port
        )