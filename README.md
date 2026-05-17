# NexusTrader Core — KI-gestütztes Automatisches Handelssystem

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=flat-square&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?style=flat-square&logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?style=flat-square&logo=docker)
![Lizenz](https://img.shields.io/badge/Lizenz-MIT-brightgreen?style=flat-square)
![Freqtrade](https://img.shields.io/badge/Freqtrade-FreqAI-orange?style=flat-square)

> **Autonomes Handelssystem der naechsten Generation**
> Powered by Freqtrade/FreqAI, FastAPI, Stable-Baselines3 & LLM-Integration

_Erstellt von Francis Klein / StockPro-AI · Mai 2026 · Mit Unterstuetzung von Perplexity Pro_

---

## Ueber NexusTrader Core

NexusTrader Core ist das **autonome Execution-Backend** des NexusTrader-Oekosystems. Es kombiniert klassisches algorithmisches Trading (Freqtrade) mit modernen KI-Methoden (FreqAI, DRL, LLM-Agenten) und bietet zwei Betriebsmodi:

- **CONFIRM Mode** — Jedes Signal wird im Dashboard angezeigt und muss manuell bestaetigt werden (Human-in-the-Loop)
- **YOLO Mode** — Vollautonomes Trading ohne Bestaetigung, direkte Ausfuehrung auf Hyperliquid

Das System ist modular aufgebaut, Docker-basiert und ueber MCP (Model Context Protocol) erweiterbar.

---

## Funktionsuebersicht

| Feature | Beschreibung |
|---|---|
| **Zwei Trading-Modi** | CONFIRM (manuell) und YOLO (autonom) |
| **FreqAI / DRL** | Machine Learning & Deep Reinforcement Learning fuer Strategieentwicklung |
| **LLM-Integration** | OpenAI, Anthropic, Google Gemini fuer Signalbegruendung |
| **Hyperliquid** | Native Perpetuals-Unterstuetzung via API |
| **FastAPI Orchestrator** | REST API fuer Signalverwaltung, Modus-Umschaltung, Status |
| **Streamlit Dashboard** | Echtzeit-Uebersicht, Signalbestaetigung, Portfolio-Monitoring |
| **Redis Queue** | Asynchrone Signalverarbeitung und Caching |
| **MCP-Erweiterbar** | Skills und Tools koennen per MCP hinzugefuegt werden |
| **Docker-Ready** | Ein-Klick-Start per start.bat / docker-compose |
| **Risikomanagement** | Positions-Sizing, Stop-Loss, Max-Drawdown-Kontrolle |

---

## Systemarchitektur

```
+----------------------------------+
|       Streamlit Dashboard        |
|  (Port 8501 - Signale / Status)  |
+----------------------------------+
            |
            v REST API
+----------------------------------+
|      FastAPI Orchestrator        |
|  (Port 8000 - Signal Router)     |
|  - CONFIRM / YOLO Mode Switch    |
|  - Signal Queue Management       |
|  - Risk Management               |
+----------------------------------+
       |              |
       v              v
+----------+    +------------------+
|  Redis   |    |  FreqAI / DRL    |
|  Queue   |    |  Strategy Engine |
+----------+    +------------------+
                       |
                       v
            +--------------------+
            |   Hyperliquid API  |
            |  (Live / Paper)    |
            +--------------------+
```

---

## Tech-Stack

### Backend (Orchestrator)
| Komponente | Technologie |
|---|---|
| Web Framework | FastAPI + Uvicorn |
| ML / DRL | scikit-learn, PyTorch, Stable-Baselines3 |
| Trading Engine | Freqtrade + FreqAI |
| LLM Router | OpenAI, Anthropic, Google Gemini |
| Queue / Cache | Redis + Celery |
| Scheduling | APScheduler |
| Datenbank | SQLAlchemy + SQLite/PostgreSQL |
| Config | Pydantic Settings + python-dotenv |
| Logging | Loguru |

### Frontend (Dashboard)
| Komponente | Technologie |
|---|---|
| Dashboard | Streamlit 1.35 |
| Charts | Plotly |
| HTTP Client | Requests |
| Daten | Pandas + NumPy |

### Infrastruktur
| Komponente | Technologie |
|---|---|
| Containerisierung | Docker + Docker Compose |
| Nachrichten-Queue | Redis |
| Windows-Scripts | start.bat / stop.bat / reset.bat |

---

## Schnellstart

### Voraussetzungen

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac/Linux)
- [Git](https://git-scm.com/)
- Hyperliquid API Key (fuer Live-Trading)
- Optional: OpenAI / Anthropic / Gemini API Key (fuer LLM-Features)

### Windows One-Click-Start

```bash
# 1. Repository klonen
git clone https://github.com/StockPro-AI/nexustrader-core.git
cd nexustrader-core

# 2. Umgebung konfigurieren
copy .env.example .env
# .env mit deinen API-Keys befuellen

# 3. System starten
start.bat
```

### Manuelle Installation (Docker)

```bash
git clone https://github.com/StockPro-AI/nexustrader-core.git
cd nexustrader-core
cp .env.example .env
# .env bearbeiten
docker-compose up -d
```

### Dienste nach dem Start

| Dienst | URL | Beschreibung |
|---|---|---|
| Dashboard | http://localhost:8501 | Streamlit UI |
| Orchestrator API | http://localhost:8000 | FastAPI REST |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Redis | localhost:6379 | Queue / Cache |

---

## Konfiguration

Alle Einstellungen werden ueber die `.env`-Datei gesteuert:

```env
# Trading Modus
TRADING_MODE=confirm          # 'confirm' oder 'yolo'

# Hyperliquid
HYPERLIQUID_API_KEY=dein_key
HYPERLIQUID_SECRET=dein_secret
HYPERLIQUID_TESTNET=true      # false fuer Live-Trading

# LLM (optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_KEY=...

# Risikomanagement
MAX_POSITION_SIZE_USD=1000
MAX_DRAWDOWN_PCT=10
STOP_LOSS_PCT=2

# Redis
REDIS_URL=redis://redis:6379/0
```

### Empfohlene Einstellungen fuer den Start

```env
TRADING_MODE=confirm
HYPERLIQUID_TESTNET=true
MAX_POSITION_SIZE_USD=100
```

---

## API-Endpunkte

### System

| Methode | Endpoint | Beschreibung |
|---|---|---|
| GET | `/` | Health Check & Status |
| GET | `/status` | System-Status (Modus, Queue, PnL) |
| POST | `/mode/confirm` | CONFIRM Mode aktivieren |
| POST | `/mode/yolo` | YOLO Mode aktivieren |

### Signale

| Methode | Endpoint | Beschreibung |
|---|---|---|
| GET | `/signals/pending` | Ausstehende Signale abrufen |
| POST | `/signal/{id}/approve` | Signal bestaetigen (CONFIRM Mode) |
| POST | `/signal/{id}/reject` | Signal ablehnen |
| POST | `/signal/submit` | Neues Signal einreichen |

### Portfolio

| Methode | Endpoint | Beschreibung |
|---|---|---|
| GET | `/portfolio` | Aktuelle Positionen |
| GET | `/trades/history` | Trade-Historie |
| GET | `/performance` | Performance-Metriken |

---

## Trading-Modi im Detail

### CONFIRM Mode (Standard)

```
Strategie generiert Signal
        |
        v
Signal landet in Queue
        |
        v
Dashboard zeigt Signal an
        |
   [Trader entscheidet]
    /          \
APPROVE      REJECT
   |              |
Order auf    Signal wird
Hyperliquid  verworfen
```

### YOLO Mode (Autonom)

```
Strategie generiert Signal
        |
        v
Risiko-Check (Stop-Loss, Max-Size)
        |
        v
Direkte Order auf Hyperliquid
        |
        v
Notifikation im Dashboard
```

---

## Projektstruktur

```
nexustrader-core/
|-- dashboard/
|   |-- app.py              # Streamlit Dashboard
|   +-- requirements.txt    # Dashboard Dependencies
|-- orchestrator/
|   |-- main.py             # FastAPI Orchestrator
|   +-- requirements.txt    # Orchestrator Dependencies
|-- .env.example            # Umgebungsvariablen Template
|-- .gitignore
|-- README.md
|-- docker-compose.yml      # Multi-Container Setup
|-- reset.bat               # Reset Script (Windows)
|-- start.bat               # Start Script (Windows)
+-- stop.bat                # Stop Script (Windows)
```

---

## Erweiterbarkeit (MCP)

NexusTrader Core ist fuer die Integration von MCP-Servern (Model Context Protocol) ausgelegt. Neue Skills koennen als separate Services hinzugefuegt werden:

```yaml
# docker-compose.yml Erweiterung
services:
  mcp-server:
    build: ./mcp-skills/dein-skill
    environment:
      - ORCHESTRATOR_URL=http://orchestrator:8000
```

Beispiel-Skills:
- **Sentiment Analyzer** — Reddit/News Sentiment via LLM
- **On-Chain Monitor** — Blockchain-Daten fuer Hyperliquid
- **Backtester** — Automatisches Backtesting neuer Strategien
- **Risk Guardian** — Erweitertes Risikomanagement

---

## Mitwirken

1. Fork erstellen
2. Feature-Branch anlegen (`git checkout -b feature/mein-feature`)
3. Aenderungen committen (`git commit -m 'Add: mein Feature'`)
4. Branch pushen (`git push origin feature/mein-feature`)
5. Pull Request erstellen

---

## Lizenz

Dieses Projekt steht unter der [MIT-Lizenz](LICENSE).

---

## Haftungsausschluss

> **WICHTIG:** NexusTrader Core ist ein experimentelles System fuer Bildungs- und Forschungszwecke. Der Einsatz im Live-Trading geschieht auf eigene Gefahr. Kryptowaerungs-Trading birgt erhebliche finanzielle Risiken. Die Entwickler uebernehmen keine Haftung fuer finanzielle Verluste.

---

## Credits

- **Entwickler:** Francis Klein / StockPro-AI
- **Trading Engine:** [Freqtrade](https://www.freqtrade.io/) & FreqAI
- **Exchange:** [Hyperliquid](https://hyperliquid.xyz/)
- **KI-Unterstuetzung:** Perplexity Pro
