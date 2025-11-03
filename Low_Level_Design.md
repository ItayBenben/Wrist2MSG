# Wrist2Whats - Low Level Design

## Garmin App (Monkey C)
- `MainView.mc` → Displays dropdown for contacts/messages.
- `CommHandler.mc` → Handles BLE connection to iPhone app.

## iPhone App (Swift)
- `BLEManager.swift` → Listens to Garmin data packets.
- `NetworkManager.swift` → Sends HTTPS POST to backend.
- `ConfigManager.swift` → Loads templates and contact lists.

## Python Backend
- `backend_app.py` → REST API to receive message requests and dispatch to providers.
- `messaging_services.py` → Handles WhatsApp, Telegram, and Discord integrations.
- `db_manager.py` → Manages message logs and configurations.

## Data Flow
```mermaid
flowchart LR
    Garmin --> iPhone --> Backend --> WhatsApp
    Backend --> Telegram
    Backend --> Discord
```
