# Wrist2Whats - Entity Relationship Diagram (ERD)
```mermaid
erDiagram
    USER {
        int user_id
        string name
        string phone_e164
    }

    CONTACT {
        int contact_id
        int user_id
        string name
        string phone_e164
    }

    MESSAGE_TEMPLATE {
        int template_id
        int user_id
        string template_name
        string template_text
    }

    MESSAGE_LOG {
        int log_id
        int user_id
        int contact_id
        int template_id
        datetime sent_at
        string status  // accepted | sent | delivered | failed
        string wa_message_id
        string error_code
    }

    USER ||--o{ CONTACT : owns
    USER ||--o{ MESSAGE_TEMPLATE : defines
    USER ||--o{ MESSAGE_LOG : creates
    CONTACT ||--o{ MESSAGE_LOG : receives
    MESSAGE_TEMPLATE ||--o{ MESSAGE_LOG : uses
```

Notes:
- No plaintext message bodies are stored in `MESSAGE_LOG`. Logs reference `template_id`.
- Secrets and tokens are stored encrypted; comply with WhatsApp Cloud API policies and opt-in requirements.
