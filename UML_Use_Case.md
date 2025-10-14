# Wrist2Whats - UML Use Case Diagram
```mermaid
usecaseDiagram
    actor User
    User --> (Select Contact)
    User --> (Select Message)
    User --> (Choose Platform)
    User --> (Send Message)
    (Send Message) --> (Transmit via Backend)
    (Transmit via Backend) --> (Deliver via WhatsApp)
    (Transmit via Backend) --> (Deliver via Telegram)
    (Transmit via Backend) --> (Deliver via Discord)
```
