"""
Cycle-Aware WNBA: Predictive Modeling Pipeline

This module provides a pipeline for estimating the likelihood of menstruation-linked physiological impact on WNBA player performance.
- Data ingestion using wehoop and wearable APIs
- Feature engineering for cycle-aware features
- Hybrid modeling (Lasso Logistic Regression + LSTM)
- Evaluation metrics
- Daily predictions and dashboard overlays

Ethical Notice: This code is designed for responsible, privacy-aware research. Any use must comply with athlete consent, data protection laws, and non-exploitative practices.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegressionCV
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error, mean_absolute_error
import supabase
import torch
import torch.nn as nn

# ========== Data Ingestion ==========

def ingest_wehoop_data(schedule_path, stats_path, context_path):
    """Load game schedule, player stats, and context from wehoop CSVs."""
    schedule = pd.read_csv(schedule_path)
    stats = pd.read_csv(stats_path)
    context = pd.read_csv(context_path)
    return schedule, stats, context

def ingest_wearable_data(api_func, player_ids):
    """Ingest wearable data (BBT, HR, HRV, sleep, etc.) using API function for each player."""
    wearable_records = []
    for pid in player_ids:
        data = api_func(pid)
        wearable_records.append(data)
    return pd.DataFrame(wearable_records)

def merge_all(schedule, stats, context, wearable, cycle_tracking):
    """Merge all data sources into a unified DataFrame keyed by player and date."""
    df = stats.merge(schedule, on=["game_id"], how="left")
    df = df.merge(context, on=["game_id"], how="left")
    df = df.merge(wearable, on=["player_id", "date"], how="left")
    df = df.merge(cycle_tracking, on=["player_id", "date"], how="left")
    return df

# ========== Feature Engineering ==========

def engineer_features(df):
    """Generate cycle-aware and physiological features."""
    # Cycle day
    df["cycle_day"] = (df["date"] - pd.to_datetime(df["cycle_start"])).dt.days % df["menstruation_duration"]
    # Ovulation flag
    df["ovulation_flag"] = (df["cycle_day"] == df["ovulation_day"]).astype(int)
    # Symptom score
    symptom_cols = ["cramps", "mood", "discharge"]
    df["symptom_score"] = df[symptom_cols].sum(axis=1, skipna=True)
    # Lagged HRV
    df["lagged_hrv"] = df.groupby("player_id")["hrv"].shift(1)
    # Normalize features
    features_to_scale = ["bbt", "hr", "hrv", "sleep_quality", "sleep_duration",
                         "skin_temp", "breathing_rate", "flow_intensity",
                         "lh", "fsh", "estrogen", "progesterone", "symptom_score", "lagged_hrv"]
    scaler = StandardScaler()
    df[features_to_scale] = scaler.fit_transform(df[features_to_scale].fillna(0))
    # Handle missing
    imputer = SimpleImputer(strategy="mean")
    df[features_to_scale] = imputer.fit_transform(df[features_to_scale])
    return df

# ========== Modeling ==========

def train_lasso_logistic(X_train, y_train):
    """Train logistic regression with Lasso regularization."""
    clf = LogisticRegressionCV(
        Cs=10, cv=5, penalty="l1", solver="saga", scoring="neg_log_loss", max_iter=1000, n_jobs=-1
    )
    clf.fit(X_train, y_train)
    return clf

class PlayerLSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim=16, output_dim=1):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return torch.sigmoid(out)

def train_lstm(X_seq, y_seq, epochs=10, lr=1e-3):
    """Train LSTM on sequence data (optional)."""
    input_dim = X_seq.shape[-1]
    model = PlayerLSTM(input_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.BCELoss()
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        outputs = model(torch.tensor(X_seq, dtype=torch.float32))
        loss = criterion(outputs.squeeze(), torch.tensor(y_seq, dtype=torch.float32))
        loss.backward()
        optimizer.step()
    return model

# ========== Prediction & Output ==========

def predict_daily(model, X, threshold=0.5):
    """Predict daily impact probabilities and flag 'Likely'/'Unlikely'."""
    probs = model.predict_proba(X)[:, 1]
    flags = np.where(probs >= threshold, "Likely", "Unlikely")
    return pd.DataFrame({"probability": probs, "flag": flags})

def store_results(df, supabase_url=None, supabase_key=None, csv_path=None):
    """Store results in Supabase or CSV."""
    if supabase_url and supabase_key:
        client = supabase.create_client(supabase_url, supabase_key)
        client.table("wnba_cycle_predictions").upsert(df.to_dict("records")).execute()
    if csv_path:
        df.to_csv(csv_path, index=False)

# ========== Evaluation Metrics ==========

def evaluate(y_true, y_pred, y_prob):
    """Compute metrics: RMSE, MAE, MAPE, Bias, RMSSE, Congruence."""
    rmse = mean_squared_error(y_true, y_pred, squared=False)
    mae = mean_absolute_error(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    bias = np.mean(y_pred - y_true)
    rmsse = np.sqrt(np.mean((y_pred - y_true) ** 2) / np.mean((y_true - np.mean(y_true)) ** 2))
    congruence = np.corrcoef(y_true, y_prob)[0, 1]
    return {"RMSE": rmse, "MAE": mae, "MAPE": mape, "Bias": bias, "RMSSE": rmsse, "Congruence": congruence}

# ========== Dashboard Overlay & Ethical Disclaimer ==========

def render_dashboard(preds_df, metrics, explainability_df):
    """Render dashboard with predictions, metrics, explainability overlays, and ethical disclaimer."""
    import streamlit as st
    st.title("Cycle-Aware WNBA Dashboard")
    st.markdown("""
    **Ethical Disclaimer:**  
    This dashboard is for research and health-supportive purposes only.  
    All predictions are probabilistic and should never be used for exploitative or discriminatory decision-making.  
    Athlete privacy and consent are strictly required.  
    """)
    st.write("Daily Player Predictions")
    st.dataframe(preds_df)
    st.write("Model Evaluation Metrics")
    st.json(metrics)
    st.write("Explainability Overlay")
    st.dataframe(explainability_df)

# ========== Explainability Overlays ==========

def explainability_overlay(model, X, feature_names):
    """Return feature importances or SHAP-like explanations for predictions."""
    importances = np.abs(model.coef_[0])
    return pd.DataFrame({"feature": feature_names, "importance": importances}).sort_values("importance", ascending=False)