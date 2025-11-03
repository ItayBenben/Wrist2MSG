# Wrist2Whats - Architecture Design

## Overview
The architecture consists of three layers:
1. **Garmin Watch App** (ConnectIQ)
2. **iPhone Companion App**
3. **Cloud Backend (Python on VPS)**

### Communication Flow
Garmin App → iPhone App → Cloud Server → Messaging Provider (WhatsApp | Telegram | Discord) → Recipient

### Technologies
- Garmin ConnectIQ SDK (Monkey C)
- Swift (iPhone companion app)
- Python (Flask/FastAPI backend with multi-channel messaging services)
- Docker container on VPS (Ubuntu)

## Deployment Diagram
```mermaid
graph TD
    A[Garmin Watch] -->|BLE/ConnectIQ| B[iPhone App]
    B -->|HTTPS| C[Python Backend VPS]
    C -->|WhatsApp Automation| D[Recipient via WhatsApp]
    C -->|Telegram Bot API| E[Recipient via Telegram]
    C -->|Discord Webhook| F[Recipient via Discord]
```
