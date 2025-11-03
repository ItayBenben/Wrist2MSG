# Wrist2Whats - Software Requirements Specification (SRS)

## 1. Introduction
Wrist2Whats is a smartwatch application for Garmin (Vivoactive 5) that allows the user to send predefined WhatsApp messages from the watch, without needing to access their iPhone.

## 2. Purpose
Enable one-tap emergency or quick communication via WhatsApp, Telegram, or Discord through a Garmin wearable.

## 3. System Overview
- Garmin app sends message trigger via Garmin ConnectIQ and Bluetooth.
- Companion iPhone app receives and processes the trigger.
- A Python-based cloud backend (on VPS) handles message forwarding using a secure integration (via WhatsApp Web automation or API gateway) and now supports Telegram Bot API as well as Discord webhooks.

## 4. Functional Requirements
- User can select contact and message template on Garmin watch.
- Message is sent automatically without requiring phone interaction.
- User can choose WhatsApp, Telegram, or Discord as the delivery channel.
- Contact list and message templates are configurable from mobile app.
- Secure cloud communication via HTTPS + token auth.

## 5. Non-Functional Requirements
- Response time < 2 seconds.
- Encryption of communication and stored data.
- Multi-platform reliability (iOS + Garmin).
