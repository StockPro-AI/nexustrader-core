"""
NexusTrader Core - Orchestrator
FastAPI-based risk management, signal routing, and confirm/yolo mode switching.
"""
import os
import sqlite3
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

app = FastAPI(
    title="NexusTrader Orchestrator",
    description="Risk management & signal routing for NexusTrader Core",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Config from env ---
TRADING_MODE = os.getenv("TRADING_MODE", "confirm")  # confirm or yolo
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
MAX_DAILY_LOSS_PCT = float(os.getenv("MAX_DAILY_LOSS_PCT", "2.0"))
MAX_OPEN_POSITIONS = int(os.getenv("MAX_OPEN_POSITIONS", "5"))
MAX_POSITION_SIZE_USD = float(os.getenv("MAX_POSITION_SIZE_USD", "500"))
KILL_SWITCH = os.getenv("KILL_SWITCH", "false").lower() == "true"
DB_PATH = os.getenv("DB_PATH", "/app/data/nexustrader.db")

# --- DB Setup ---
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            symbol TEXT,
            side TEXT,
            size_usd REAL,
            strategy TEXT,
            status TEXT DEFAULT 'pending',
            reason TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            symbol TEXT,
            side TEXT,
            size_usd REAL,
            entry_price REAL,
            stop_loss REAL,
            take_profit REAL,
            strategy TEXT,
            pnl REAL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- Models ---
class Signal(BaseModel):
    symbol: str
    side: str  # long or short
    size_usd: float
    strategy: str
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    reason: Optional[str] = None

class ModeSwitch(BaseModel):
    mode: str  # confirm or yolo

# --- Risk Gates ---
def check_risk_gates(signal: Signal) -> tuple[bool, str]:
    if KILL_SWITCH:
        return False, "Kill switch is active"
    if signal.size_usd > MAX_POSITION_SIZE_USD:
        return False, f"Position size {signal.size_usd} exceeds max {MAX_POSITION_SIZE_USD}"
    if signal.side not in ["long", "short"]:
        return False, f"Invalid side: {signal.side}"
    return True, "OK"

# --- Endpoints ---
@app.get("/")
def root():
    return {
        "service": "NexusTrader Orchestrator",
        "version": "1.0.0",
        "mode": TRADING_MODE,
        "dry_run": DRY_RUN,
        "kill_switch": KILL_SWITCH
    }

@app.get("/status")
def status():
    conn = sqlite3.connect(DB_PATH)
    pending = conn.execute("SELECT COUNT(*) FROM signals WHERE status='pending'").fetchone()[0]
    approved = conn.execute("SELECT COUNT(*) FROM signals WHERE status='approved'").fetchone()[0]
    rejected = conn.execute("SELECT COUNT(*) FROM signals WHERE status='rejected'").fetchone()[0]
    conn.close()
    return {
        "mode": TRADING_MODE,
        "dry_run": DRY_RUN,
        "kill_switch": KILL_SWITCH,
        "max_daily_loss_pct": MAX_DAILY_LOSS_PCT,
        "max_position_size_usd": MAX_POSITION_SIZE_USD,
        "pending_signals": pending,
        "approved_signals": approved,
        "rejected_signals": rejected
    }

@app.post("/signal")
def submit_signal(signal: Signal):
    """Submit a new trading signal for processing"""
    passed, reason = check_risk_gates(signal)
    if not passed:
        raise HTTPException(status_code=400, detail=f"Risk gate failed: {reason}")

    status = "pending" if TRADING_MODE == "confirm" else "approved"
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO signals (timestamp, symbol, side, size_usd, strategy, status, reason) VALUES (?,?,?,?,?,?,?)",
        (datetime.utcnow().isoformat(), signal.symbol, signal.side, signal.size_usd, signal.strategy, status, signal.reason)
    )
    conn.commit()
    conn.close()

    if TRADING_MODE == "yolo" and not DRY_RUN:
        # TODO: Execute via Hyperliquid MCP server
        pass

    return {"status": status, "message": f"Signal {'queued for approval' if status == 'pending' else 'auto-approved (yolo mode)'}"}

@app.get("/signals/pending")
def get_pending_signals():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT * FROM signals WHERE status='pending' ORDER BY timestamp DESC").fetchall()
    conn.close()
    return [{"id": r[0], "timestamp": r[1], "symbol": r[2], "side": r[3], "size_usd": r[4], "strategy": r[5], "reason": r[7]} for r in rows]

@app.post("/signal/{signal_id}/approve")
def approve_signal(signal_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE signals SET status='approved' WHERE id=?", (signal_id,))
    conn.commit()
    conn.close()
    # TODO: Execute via Hyperliquid MCP server
    return {"status": "approved", "signal_id": signal_id}

@app.post("/signal/{signal_id}/reject")
def reject_signal(signal_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE signals SET status='rejected' WHERE id=?", (signal_id,))
    conn.commit()
    conn.close()
    return {"status": "rejected", "signal_id": signal_id}

@app.post("/mode")
def switch_mode(mode: ModeSwitch):
    global TRADING_MODE
    if mode.mode not in ["confirm", "yolo"]:
        raise HTTPException(status_code=400, detail="Mode must be 'confirm' or 'yolo'")
    TRADING_MODE = mode.mode
    return {"mode": TRADING_MODE, "message": f"Switched to {TRADING_MODE} mode"}

@app.post("/kill-switch")
def toggle_kill_switch(activate: bool = True):
    global KILL_SWITCH
    KILL_SWITCH = activate
    return {"kill_switch": KILL_SWITCH}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("ORCHESTRATOR_PORT", 8000)))
