# Wrist2Whats - Architecture Design

## Overview
The architecture now exposes two delivery paths so the watch can send messages without the user touching their iPhone:

1. **Garmin Watch App** (ConnectIQ) with Wi-Fi/LTE-capable background service
2. **Direct Cloud Relay** (HTTPS ingress tailored for devices)
3. **iPhone Companion App** (kept as a fallback/bridge)
4. **Cloud Backend (Python on VPS)**

The watch attempts the direct relay first. If it cannot reach the internet (e.g., model without Wi-Fi, airplane mode), it falls back to the legacy BLE → iPhone path automatically. Both flows converge on the same backend logic, so feature behavior stays identical while availability improves.

### Communication Flow
1. **Preferred path:** Garmin App (Wi-Fi/LTE) → Direct Cloud Relay (`/watch/send`) → Cloud Server → Messaging Interface → Recipient  
2. **Fallback path:** Garmin App → iPhone App → Cloud Server → Messaging Interface → Recipient

### Technologies
- Garmin ConnectIQ SDK (Monkey C)
- Swift (iPhone companion app)
- Python (Flask/FastAPI backend)
- Telegram Bot API integration
- Discord Webhook integration
- Docker container on VPS (Ubuntu)

## Deployment Diagram
```mermaid
flowchart TD
    subgraph Edge
        A1[Garmin Watch\n(Direct Relay Agent)]
        A2[Garmin Watch\nBLE Bridge]
    end

    subgraph Mobile
        B[iPhone Companion App]
    end

    subgraph Cloud
        C1[Device Relay API\n(/watch/send)]
        C2[Python Backend]
    end

    A1 -->|HTTPS over Wi-Fi/LTE + mTLS| C1
    C1 -->|internal gRPC| C2
    A2 -->|BLE/ConnectIQ| B
    B -->|HTTPS (TLS 1.2+)| C2
    C2 -->|WhatsApp Automation| D[Recipient via WhatsApp]
    C2 -->|Telegram Bot API| E[Recipient via Telegram]
    C2 -->|Discord Webhook| F[Recipient via Discord]
```

### Direct Cloud Relay
- **Device Agent:** A background Monkey C module (`RelayClient`) wakes on user input, brings up Wi-Fi/LTE, and POSTs payloads directly to `/watch/send`. Requests include device ID, firmware version, signed nonce, and message body.
- **mTLS + Short-Lived Tokens:** During onboarding the watch downloads a per-device client certificate and receives a refreshable OAuth client credential. The relay requires mutual TLS and a proof-of-possession token so that lost certificates can be revoked without touching the phone.
- **Retry & Store-and-Forward:** Messages are stored in the watch’s local queue (max 20 pending). The direct agent retries with backoff for 5 minutes before asking the BLE bridge to take over.
- **Convergence Logic:** The Device Relay API pushes valid payloads onto the same message bus as the iPhone flow, so downstream services remain unchanged.

## Security Additions
- **SSL Termination:** The iPhone app only talks to the backend over HTTPS with a Let’s Encrypt (or similar) certificate terminated on the VPS reverse proxy (e.g., Nginx). All internal services also use HTTPS to keep transport encrypted end to end.
- **Lightweight Client Authentication:** Each Garmin/iPhone pair stores a static API key issued during onboarding; the companion app sends it as an `Authorization: Bearer <token>` header on every request. The proxy passes the header to the Python backend, which rejects unknown keys before executing any business logic.
- **Service-to-Service Authentication:** Outbound calls from the backend to Telegram/Discord/WhatsApp continue using their respective bot tokens/webhooks, stored in environment variables. No secret material is baked into binaries.
- **Device Certificates:** Direct relay traffic uses mutual TLS with rotating certificates managed by the provisioning backend. The certificate fingerprint is bound to the Garmin device ID, preventing replay from other hardware.
- **Signed Payloads:** Each direct message includes a SHA256 HMAC over the body + monotonic counter, catching tampering and detecting out-of-order delivery before it can mutate logs or trigger duplicate sends.

## Contact Management Implementation
- **Storage:** Contacts live in the same relational datastore as message templates/logs (e.g., PostgreSQL or SQLite on the VPS). Each contact row includes `contact_id`, `user_id`, `display_name`, `channel_type`, `channel_identifier`, plus optional metadata like `priority` or `enabled`.
- **Backend Logic:** The FastAPI/Flask service (`backend_app.py`) exposes CRUD endpoints under `/contacts`. Persistence is handled through the existing ORM/repository layer, while `messaging_service.py` resolves the target channel by calling `contact_repo.get(contact_id)`.
- **Interface Layers:** The Swift companion app surfaces contact management inside its configuration screens (e.g., `ConfigManager`-backed views) and syncs changes via the new endpoints. The Garmin watch continues to read the synced contact list—no additional UI beyond refreshing its dropdown payload is required.

## Direct Relay Request/Response
- **Endpoint:** `POST /watch/send`
- **Headers:** `Authorization: Bearer <short-lived PoP token>`, `X-Device-ID`, `X-Device-Nonce`, plus the mutual TLS certificate.
- **Body:** `{"message_id": "...", "template_id": "...", "contact_id": "...", "channel": "whatsapp", "payload": {...}}`
- **Responses:** 202 Accepted (queued) or concrete error codes describing whether the device should retry immediately, fall back to iPhone, or prompt re-provisioning.
- **Monitoring:** Relay requests emit structured logs with device ID, firmware, and result code so operations can spot models that frequently drop to fallback mode.
