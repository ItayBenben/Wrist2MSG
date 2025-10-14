# Wrist2Whats - Architecture Design

## Overview
The architecture consists of three layers:
1. **Garmin Watch App** (ConnectIQ)
2. **iPhone Companion App**
3. **Cloud Backend (Python on VPS)**

### Communication Flow
Garmin App → iPhone App → Cloud Server → Channel Provider (WhatsApp/Telegram/Discord) → Recipient

### Technologies
- Garmin ConnectIQ SDK (Monkey C)
- Swift (iPhone companion app)
- Python (Flask/FastAPI backend)
- Docker container on VPS (Ubuntu)
- Messaging providers: WhatsApp API/automation, Telegram Bot API, Discord Bot API/Webhooks

## Deployment Diagram
```mermaid
graph TD
    A[Garmin Watch] -->|BLE/ConnectIQ| B[iPhone App]
    B -->|HTTPS| C[Python Backend VPS]
    subgraph Channels
      D1[WhatsApp]
      D2[Telegram]
      D3[Discord]
    end
    C -->|Provider Adapter| D1
    C -->|Provider Adapter| D2
    C -->|Provider Adapter| D3
```

## Channel Abstraction
The backend exposes a single message API and delegates delivery to a provider adapter
based on a `platform` parameter. Supported values: `whatsapp`, `telegram`, `discord`.
This design enables adding future channels with minimal changes.
