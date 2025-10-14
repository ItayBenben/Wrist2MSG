# Wrist2Whats - Entity Relationship Diagram (ERD)
```mermaid
erDiagram
    USER {
        int user_id
        string name
        string phone
    }
    MESSAGE_TEMPLATE {
        int template_id
        string text
        int user_id
    }
    MESSAGE_LOG {
        int log_id
        int user_id
        string contact_name
        datetime sent_at
        string message_text
        string platform // whatsapp | telegram | discord
        string provider_status // delivered | failed | queued
    }

    USER ||--o{ MESSAGE_TEMPLATE : has
    USER ||--o{ MESSAGE_LOG : sends
```
