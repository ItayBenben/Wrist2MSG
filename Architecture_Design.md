# Wrist2Whats - Architecture Design

## Overview
The architecture consists of three layers:
1. **Garmin Watch App** (ConnectIQ)
2. **iPhone Companion App**
3. **Cloud Backend (Python on VPS)**

### Communication Flow
Garmin App → iPhone App → Cloud Server → Messaging Interface → Recipient

### Technologies
- Garmin ConnectIQ SDK (Monkey C)
- Swift (iPhone companion app)
- Python (Flask/FastAPI backend)
- Telegram Bot API integration
- Discord Webhook integration
- Docker container on VPS (Ubuntu)

## Deployment Diagram
```mermaid
graph TD
    A[Garmin Watch] -->|BLE/ConnectIQ| B[iPhone App]
    B -->|HTTPS (TLS 1.2+)| C[Python Backend VPS]
    C -->|WhatsApp Automation| D[Recipient via WhatsApp]
    C -->|Telegram Bot API| E[Recipient via Telegram]
    C -->|Discord Webhook| F[Recipient via Discord]
```

## Security Additions
- **SSL Termination:** The iPhone app only talks to the backend over HTTPS with a Let’s Encrypt (or similar) certificate terminated on the VPS reverse proxy (e.g., Nginx). All internal services also use HTTPS to keep transport encrypted end to end.
- **Lightweight Client Authentication:** Each Garmin/iPhone pair stores a static API key issued during onboarding; the companion app sends it as an `Authorization: Bearer <token>` header on every request. The proxy passes the header to the Python backend, which rejects unknown keys before executing any business logic.
- **Service-to-Service Authentication:** Outbound calls from the backend to Telegram/Discord/WhatsApp continue using their respective bot tokens/webhooks, stored in environment variables. No secret material is baked into binaries.

## Contact Management Implementation
- **Storage:** Contacts live in the same relational datastore as message templates/logs (e.g., PostgreSQL or SQLite on the VPS). Each contact row includes `contact_id`, `user_id`, `display_name`, `channel_type`, `channel_identifier`, plus optional metadata like `priority` or `enabled`.
- **Backend Logic:** The FastAPI/Flask service (`backend_app.py`) exposes CRUD endpoints under `/contacts`. Persistence is handled through the existing ORM/repository layer, while `messaging_service.py` resolves the target channel by calling `contact_repo.get(contact_id)`.
- **Interface Layers:** The Swift companion app surfaces contact management inside its configuration screens (e.g., `ConfigManager`-backed views) and syncs changes via the new endpoints. The Garmin watch continues to read the synced contact list—no additional UI beyond refreshing its dropdown payload is required.
