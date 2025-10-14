# Wrist2Whats - UML Use Case Diagram
```mermaid
usecaseDiagram
    actor User as U
    U --> (Select Contact)
    U --> (Select Message)
    U --> (Send Message)
    (Send Message) --> (Forward via Backend using WhatsApp Cloud API)

    actor Admin as A
    A --> (Manage Contacts)
    A --> (Manage Message Templates)
```
