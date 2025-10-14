# Wrist2Whats - Software Requirements Specification (SRS)

## 1. Introduction
Wrist2Whats is a smartwatch application for Garmin (Vivoactive 5) that allows the user to send predefined WhatsApp messages from the watch, without needing to access their iPhone.

## 2. Purpose
Enable one-tap emergency or quick communication via WhatsApp through a Garmin wearable.

## 3. System Overview
- Garmin app sends message trigger via Garmin ConnectIQ and Bluetooth.
- Companion iPhone app receives and processes the trigger.
- A Python-based cloud backend (on VPS) handles message forwarding using a secure integration via provider adapters (WhatsApp, Telegram, Discord).

## 4. Functional Requirements
- User can select contact and message template on Garmin watch.
- Message is sent automatically without requiring phone interaction.
- Contact list and message templates are configurable from mobile app.
- Secure cloud communication via HTTPS + token auth.
- User or mobile app can choose `platform` per message: `whatsapp`, `telegram`, or `discord`.
- The backend routes the message to the selected platform provider.

## 5. Non-Functional Requirements
- Response time < 2 seconds.
- Encryption of communication and stored data.
- Multi-platform reliability (iOS + Garmin).
- Provider isolation: a failure in one provider must not impact others.
- Observability: log platform, delivery status, and error codes per message.
