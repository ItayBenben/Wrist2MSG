# Wrist2Whats - Low Level Design

## Garmin App (Monkey C)
- `MainView.mc` → Displays dropdown for contacts/messages.
- `CommHandler.mc` → Handles BLE connection to iPhone app.

## iPhone App (Swift)
- `BLEManager.swift` → Listens to Garmin data packets.
- `NetworkManager.swift` → Sends HTTPS POST to backend.
- `ConfigManager.swift` → Loads templates and contact lists.

## Python Backend
- `app.py` → REST API to receive message requests.
- `whatsapp_service.py` → Handles WhatsApp automation.
- `db_manager.py` → Manages message logs and configurations.
- `messaging_service.py` → Dispatches outbound messages to WhatsApp, Telegram, and Discord.

## Data Flow
```mermaid
flowchart LR
    Garmin --> iPhone --> Backend --> WhatsApp
    Backend --> Telegram
    Backend --> Discord
```
