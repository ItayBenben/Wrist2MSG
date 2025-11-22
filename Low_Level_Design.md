# Wrist2Whats - Low Level Design

## Garmin App (Monkey C)
- `MainView.mc` → Displays dropdown for contacts/messages.
- `CommHandler.mc` → Handles BLE connection to iPhone app for the fallback path.
- `RelayClient.mc` → Background data service that brings up Wi-Fi/LTE, signs payloads, and POSTs to the `/watch/send` endpoint. Maintains a local queue (max 20) and promotes messages to BLE fallback when direct delivery fails for >5 minutes.

## iPhone App (Swift)
- `BLEManager.swift` → Listens to Garmin data packets.
- `NetworkManager.swift` → Sends HTTPS POST to backend.
- `ConfigManager.swift` → Loads templates and contact lists.

## Python Backend
- `backend_app.py`
  - `/send` route → legacy companion app ingress.
  - `/watch/send` route → mutual-auth device relay that validates `X-Device-ID` + bearer tokens from `WATCH_DEVICE_TOKENS`, enriches metadata with device context, and emits 202 responses when queued.
- `whatsapp_service.py` → Handles WhatsApp automation.
- `db_manager.py` → Manages message logs and configurations.
- `messaging_service.py` → Dispatches outbound messages to WhatsApp, Telegram, and Discord.

## Data Flow
```mermaid
flowchart TD
    subgraph Watch
        G1[RelayClient\n(Wi-Fi/LTE)]
        G2[CommHandler\n(BLE)]
    end
    subgraph Mobile
        I[iPhone App]
    end
    subgraph Cloud
        B1[Device Relay API\n/watch/send]
        B2[Messaging Backend]
    end

    G1 -->|HTTPS| B1
    B1 --> B2
    G2 -->|BLE| I
    I -->|HTTPS| B2
    B2 --> WhatsApp
    B2 --> Telegram
    B2 --> Discord
```
