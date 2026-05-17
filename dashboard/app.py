"""
NexusTrader Core - Streamlit Dashboard
Real-time monitoring, signal approval/rejection, trade journal and performance.
"""
import streamlit as st
import requests
import json
from datetime import datetime

# --- Config ---
ORCHESTRATOR_URL = "http://orchestrator:8000"

st.set_page_config(
    page_title="NexusTrader Core",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar ---
st.sidebar.title(" NexusTrader Core")
st.sidebar.markdown("---")

# Mode Switch
try:
    status = requests.get(f"{ORCHESTRATOR_URL}/status", timeout=3).json()
    current_mode = status.get("mode", "confirm")
    dry_run = status.get("dry_run", True)
    kill_switch = status.get("kill_switch", False)
except:
    current_mode = "unknown"
    dry_run = True
    kill_switch = False
    status = {}

st.sidebar.markdown(f"**Mode:** `{current_mode.upper()}`")
st.sidebar.markdown(f"**Dry Run:** {'YES - SAFE' if dry_run else ' LIVE TRADING'}")
st.sidebar.markdown(f"**Kill Switch:** {' ACTIVE' if kill_switch else ' Inactive'}")
st.sidebar.markdown("---")

if st.sidebar.button(" Switch to CONFIRM mode"):
    requests.post(f"{ORCHESTRATOR_URL}/mode", json={"mode": "confirm"})
    st.rerun()

if st.sidebar.button(" Switch to YOLO mode"):
    requests.post(f"{ORCHESTRATOR_URL}/mode", json={"mode": "yolo"})
    st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button(" ACTIVATE Kill Switch", type="primary"):
    requests.post(f"{ORCHESTRATOR_URL}/kill-switch?activate=true")
    st.rerun()

if st.sidebar.button("Deactivate Kill Switch"):
    requests.post(f"{ORCHESTRATOR_URL}/kill-switch?activate=false")
    st.rerun()

# --- Main Dashboard ---
st.title(" NexusTrader Core Dashboard")

# Status Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Trading Mode", current_mode.upper())
with col2:
    st.metric("Environment", "DRY RUN" if dry_run else "LIVE")
with col3:
    st.metric("Pending Signals", status.get("pending_signals", 0))
with col4:
    st.metric("Kill Switch", "ACTIVE" if kill_switch else "Off")

st.markdown("---")

# Risk Parameters
st.subheader(" Risk Parameters")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Max Daily Loss", f"{status.get('max_daily_loss_pct', 2.0)}%")
with col2:
    st.metric("Max Position Size", f"${status.get('max_position_size_usd', 500)}")
with col3:
    st.metric("Approved Signals", status.get("approved_signals", 0))

st.markdown("---")

# Pending Signals
st.subheader(" Pending Signals (Confirm Mode)")
try:
    pending = requests.get(f"{ORCHESTRATOR_URL}/signals/pending", timeout=3).json()
    if pending:
        for sig in pending:
            with st.expander(f" {sig['symbol']} {sig['side'].upper()} ${sig['size_usd']} - {sig['strategy']}"):
                st.write(f"**Timestamp:** {sig['timestamp']}")
                st.write(f"**Symbol:** {sig['symbol']}")
                st.write(f"**Side:** {sig['side'].upper()}")
                st.write(f"**Size:** ${sig['size_usd']}")
                st.write(f"**Strategy:** {sig['strategy']}")
                st.write(f"**Reason:** {sig.get('reason', 'N/A')}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f" APPROVE #{sig['id']}", key=f"approve_{sig['id']}", type="primary"):
                        requests.post(f"{ORCHESTRATOR_URL}/signal/{sig['id']}/approve")
                        st.success("Signal approved!")
                        st.rerun()
                with col2:
                    if st.button(f" REJECT #{sig['id']}", key=f"reject_{sig['id']}"):
                        requests.post(f"{ORCHESTRATOR_URL}/signal/{sig['id']}/reject")
                        st.warning("Signal rejected.")
                        st.rerun()
    else:
        st.info("No pending signals.")
except Exception as e:
    st.error(f"Cannot connect to orchestrator: {e}")

st.markdown("---")
st.caption("NexusTrader Core v1.0 | Auto-refreshes every 30s")

# Auto-refresh
st.markdown("""
    <script>
    setTimeout(function(){window.location.reload();}, 30000);
    </script>
""", unsafe_allow_html=True)
