import streamlit as st
from src.app.config import load_config, deep_merge
import json

st.set_page_config(
    page_title="Finance Notifier",
    page_icon="📈",
    layout="wide"
)
st.title("Finance Notifier")
st.write("Please enter your configuration settings:")
threshold = st.number_input("Threshold percentage", min_value=0.0, value=3.0, step=0.1)
tickers = st.multiselect("Select tickers", options=["AAPL", "O", "QDVX.DE", "TUI1.DE"], default=["AAPL", "O"])
custom_ticker = st.text_area("Enter custom ticker (separated by \",\")", value="")
if custom_ticker:
    tickers.extend(custom_ticker.split(","))
st.write(f"Selected tickers: {tickers}")
ntfy_server = st.text_input("ntfy server", value="https://ntfy.sh")

config_data = load_config()
config_data["threshold_pct"] = threshold
config_data["tickers"] = tickers
config_data["ntfy"]["server"] = ntfy_server
if st.button("Save configuration"):
    with open("config.json", "w") as f:
        json.dump(config_data, f, indent=2)
    st.success("Configuration saved to config.json")