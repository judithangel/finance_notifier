import streamlit as st
from pathlib import Path
import json
import os, subprocess
from dotenv import load_dotenv
import joblib
from src.app.ml_functions import load_hist_prices, engineer_features, train_model, predict_move, engineer_features_pred

CONFIG_PATH = Path("config.json")

# Load environment variables from .env file
load_dotenv()

@st.cache_data
def load_config():
    return json.loads(CONFIG_PATH.read_text())

def save_config(cfg: dict):
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))

def commit_and_push(token: str | None = None) -> bool:
    """Commit changes for configuration and push to GitHub repository"""
    token = token or os.getenv("GITHUB_TOKEN")
    if not token:
        st.error("GITHUB_TOKEN is not set. Cannot push to GitHub. Please enter the token or set as environment variable.")
        return False
    branch = "main"
    remote = f"https://{token}@github.com/judithangel/finance_notifier.git"
    try:
        # Ensure git has a user identity (necessary in ephemeral cloud runners)
        subprocess.run(["git", "config", "user.email", "streamlit@example.com"], check=True)
        subprocess.run(["git", "config", "user.name", "streamlit-bot"], check=True)
        # Disable GPG signing to avoid failures when gpg isn't available
        subprocess.run(["git", "config", "commit.gpgsign", "false"], check=True)

        subprocess.run(["git", "add", "config.json"], check=True)

        diff = subprocess.run(
            ["git", "diff", "--cached", "--quiet", "--", "config.json"]
        )
        if diff.returncode == 0:
            st.info("Keine Änderungen zum Commit.")
            return False

        subprocess.run(
            ["git", "commit", "--no-gpg-sign", "-m", "Update config via Streamlit"],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "push", remote, branch],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        error_msg = exc.stderr or exc.stdout or str(exc)
        st.error(f"Git push failed: {error_msg}")
        return False
    return True

st.set_page_config(
    page_title="Finance Notifier",
    page_icon="📈",
    layout="wide"
)
st.title("Finance Notifier")
st.write(
    "This app allows you to configure stock tickers and train a machine learning model to predict stock movements.")

# Load config file:
config_data = load_config()

# Tabs
tab1, tab2 = st.tabs(["Configuration", "Model Training"])
with tab1:
    st.header("Configuration Settings")
    # Set threshold for notification:
    threshold = st.number_input("Threshold percentage", min_value=0.0, value=3.0, step=0.1)
    # Set tickers:
    tickers = st.multiselect("Select tickers", options=["AAPL", "O", "QDVX.DE", "TUI1.DE"], default=["AAPL", "O"])
    custom_ticker = st.text_area("Enter custom ticker (separated by \",\")", value="")
    if custom_ticker:
        tickers.extend(custom_ticker.split(","))
    st.write(f"Selected tickers: {tickers}")
    # Set ntfy server:
    ntfy_server = st.text_input("ntfy server", value="https://ntfy.sh")
    # Set logging level:
    log_level = st.selectbox(
        "Log-Level",
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        index=["DEBUG","INFO","WARNING","ERROR","CRITICAL"].index(config_data["log"]["level"])
    )
    # Market hours:
    start_hour = st.number_input("Market start hour", min_value=0, max_value=22, value=8)
    end_hour = st.number_input("Market end hour", min_value=1, max_value=23, value=22)
    if end_hour <= start_hour:
        st.error("End hour must be greater than start hour")
    # GitHub token:
    github_token = st.text_input("GitHub token", type="password")

    # Commit and push to github
    if st.button("Save configuration and push to GitHub"):
        config_data["threshold_pct"] = threshold
        config_data["tickers"] = tickers
        config_data["ntfy"]["server"] = ntfy_server
        config_data["log"]["level"] = log_level
        config_data["market_hours"]["start"] = start_hour
        config_data["market_hours"]["end"] = end_hour
        save_config(config_data)
        if commit_and_push(github_token):
            st.success("Configuration saved and pushed to GitHub")

with tab2:
    st.header("Model Training")
    st.write("Train a machine learning model to predict stock movements.")
    ticker_for_training = st.selectbox("Select ticker for training", options=config_data["tickers"])
    if st.button("Train Model"):
        df_prices = load_hist_prices(ticker_for_training)
        df_features = engineer_features(df_prices)
        model = train_model(df_features)
        st.success("Model trained successfully.")
        # Save the trained model to a file
        joblib.dump(model, f"trained_model_{ticker_for_training}.pkl")
        if commit_and_push(github_token):
            st.session_state['model_trained'] = True
            st.success(f"Trained model saved as trained_model_{ticker_for_training}.pkl and pushed to GitHub")
    if st.button("Make Prediction for tomorrow"):
        try:
            if st.session_state.get('model_trained') is not True:
                model = joblib.load(f"trained_model_{ticker_for_training}.pkl")
            df_prices = load_hist_prices(ticker_for_training, period="1mo")
            df_features = engineer_features_pred(df_prices)
            prediction = predict_move(model, df_features)
            if prediction:
                st.success(f"The model predicts that the stock price of {ticker_for_training} will go UP tomorrow.")
            else:
                st.warning(f"The model predicts that the stock price of {ticker_for_training} will go DOWN tomorrow.")
        except Exception as e:
            st.error(f"Error making prediction: No model has been trained yet. Please train the model first. Error details: {e}")
    st.write("Used model: RandomForestClassifier")