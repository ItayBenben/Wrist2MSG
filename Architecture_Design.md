# Wrist2Whats - Architecture Design

## Overview
The architecture consists of three layers:
1. **Garmin Watch App** (ConnectIQ)
2. **iPhone Companion App**
3. **Cloud Backend (Python on VPS)**

### Communication Flow
Garmin App → iPhone App → Cloud Server → Messaging Interface (WhatsApp | Telegram | Discord) → Recipient

### Technologies
- Garmin ConnectIQ SDK (Monkey C)
- Swift (iPhone companion app)
- Python (Flask/FastAPI backend with interface adapters for WhatsApp, Telegram Bot API, and Discord Webhooks)
- Docker container on VPS (Ubuntu)

## Deployment Diagram
```mermaid
graph TD
    A[Garmin Watch] -->|BLE/ConnectIQ| B[iPhone App]
    B -->|HTTPS| C[Python Backend VPS]
    C -->|WhatsApp Adapter| D[Recipient via WhatsApp]
    C -->|Telegram Adapter| E[Recipient via Telegram]
    C -->|Discord Adapter| F[Recipient via Discord]
```
