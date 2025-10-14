# Wrist2Whats - Architecture Design

## Overview
The architecture consists of three layers:
1. **Garmin Watch App** (ConnectIQ, bridged by Garmin Connect Mobile)
2. **Cloud Backend** (Python/FastAPI on VPS)
3. **WhatsApp Business Cloud API** (official, compliant integration)

### Communication Flow
Garmin App → (ConnectIQ WebRequest via Garmin Connect Mobile) → Cloud Server → WhatsApp Business Cloud API → Recipient

WhatsApp Business Cloud API → Webhook → Cloud Server (delivery receipts)

### Technologies
- Garmin ConnectIQ SDK (Monkey C)
- Python (FastAPI backend)
- PostgreSQL (persistent storage)
- Redis + Celery/RQ (async message dispatch)
- Docker container on VPS (Ubuntu)
- WhatsApp Business Cloud API (Meta)

### Security & Compliance
- No web automation or unofficial endpoints; only WhatsApp Business Cloud API.
- Token-based auth on backend endpoints; verify Meta webhook signatures.
- Encrypt secrets at rest; restrict data retention (no plaintext message bodies in logs).

### Reliability
- Use queued, asynchronous dispatch to WhatsApp to avoid blocking the watch UI.
- Persist message status and surface delivery receipts from webhook callbacks.

## Deployment Diagram
```mermaid
graph TD
    A[Garmin Watch] -->|ConnectIQ WebRequest via GCM| B[Cloud Backend (FastAPI)]
    B -->|HTTPS (Meta API)| C[WhatsApp Business Cloud API]
    C -->|Deliver| D[Recipient]
    C -->|Webhook| B
```
