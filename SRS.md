# Wrist2Whats - Software Requirements Specification (SRS)

## 1. Introduction
Wrist2Whats is a smartwatch application for Garmin (Vivoactive 5) that allows the user to send predefined WhatsApp messages from the watch, without needing to access their iPhone.

## 2. Purpose
Enable one-tap emergency or quick communication via WhatsApp through a Garmin wearable.

## 3. System Overview
- Garmin app sends a message trigger using ConnectIQ `Communications.makeWebRequest`, bridged via Garmin Connect Mobile on the phone.
- A Python-based cloud backend (on VPS) receives the request and forwards the message using the official WhatsApp Business Cloud API.
- Contacts and message templates are configured via a secure web dashboard (or ConnectIQ settings), not a custom iPhone companion app.

## 4. Functional Requirements
- User can select contact and message template on the Garmin watch.
- Message dispatch is initiated from the watch; the phone only provides network connectivity via Garmin Connect Mobile.
- Contacts and message templates are configurable from a web dashboard (or ConnectIQ settings) and synchronized to the backend.
- Backend exposes HTTPS endpoints secured with token authentication.
- Delivery status is recorded (accepted/sent/failed) using WhatsApp webhook callbacks.

## 5. Non-Functional Requirements
- Backend acknowledgement to the watch: < 500 ms (P95). Message delivery is asynchronous and not guaranteed within a fixed end-to-end SLA.
- Encryption in transit (TLS) and at rest for secrets. No plaintext message bodies are stored in logs; logs reference template IDs only.
- Reliability across iOS/Android Garmin Connect Mobile; graceful degradation when offline with retry/backoff from the backend queue.
