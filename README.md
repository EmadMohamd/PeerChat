# PeerChat — Secure Decentralized P2P Messaging System

PeerChat is a decentralized peer-to-peer messaging platform written in Python. Each node acts as both a client and server, enabling direct encrypted communication without relying on a centralized backend. **Identity is cryptographically derived from RSA keys, ensuring that your username is uniquely yours.**

The system now supports:

* **Context-Aware Filtering:** Private messages are isolated from Global Chat via a dual-pane UI.
* **Automatic Peer Discovery:** Dynamic network expansion through bootstrap peers.
* **RSA Identity Verification:** Secure challenge-response authentication.
* **Modernized GUI:** Polished PyQt6 interface with dark mode and sidebar navigation.
* **Local Persistence:** Full message history stored and retrieved via SQLite.

---

# Features

## Networking

* Fully decentralized peer-to-peer architecture.
* TCP socket communication with newline-delimited JSON streaming.
* Automatic peer discovery through bootstrap peers and dynamic peer list exchange.
* Multi-peer simultaneous communication with continuous receive loops.
* **Connectivity Note:** Ensure your **trusted bootstrap peers** are online and reachable on their specified ports to join the network swarm successfully.

## Security

* **RSA Public/Private Keys:** Identity proven via cryptographic signatures.
* **Cryptographic Peer IDs:** Peer IDs are generated as a hash of your RSA Public Key (`Username-Hash`), preventing identity spoofing.
* **Challenge-Response Flow:** Prevents identity theft without ever transmitting private keys or passwords.
* **Key Isolation:** All sensitive `.pem` files are stored in a dedicated `keys/` directory, organized by username.

## Messaging

* **Direct Private Messaging:** Target specific peers for 1-on-1 filtered conversations.
* **Global Broadcast:** Message all connected peers in the swarm simultaneously.
* **JSON Packet Protocol:** Structured 3-part communication (Sender, Message, Recipient) for precise routing.
* **Persistence:** All incoming and outgoing messages are saved to `chat_history.db`.

## GUI

* **Modern PyQt6 Interface:** Sidebar for peer selection and a sleek dark-themed chat area.
* **Identity Header:** Clear display of your unique cryptographic Peer ID at the top right.
* **Contextual History:** Automatic message retrieval from SQLite based on the selected peer in the sidebar.

---

# Architecture

```text
                ┌───────────────┐
                │   Peer A      │
                └──────┬────────┘
                       │
         ┌─────────────┼─────────────┐
         │                           │
┌────────▼────────┐         ┌────────▼────────┐
│    Peer B       │         │    Peer C       │
└────────┬────────┘         └────────┬────────┘
         │                           │
         └─────────────┬─────────────┘
                       │
                ┌──────▼────────┐
                │    Peer D     │
                └───────────────┘

```

Each peer contains:

* Listener Server & Outgoing Client Connector
* Message Handler & Peer Discovery Engine
* Authentication Layer (RSA)
* Local SQLite Database & Modern PyQt6 Frontend

---

# Authentication Flow

PeerChat uses cryptographic verification instead of passwords.

```text
1. Connect
      ↓
2. Exchange Public Keys (Identity Packet)
      ↓
3. Generate Random Challenge
      ↓
4. Sign Challenge with Private Key
      ↓
5. Verify Signature using Public Key
      ↓
6. Authenticated Communication Begins

```

---

# Message Protocol

## Chat Packet (Direct/Global)

```json
{
    "type": "chat",
    "data": {
        "sender": "Alice-a1b2c3d4",
        "recipient": "Bob-e5f6g7h8", 
        "message": "Hello, Bob!"
    }
}

```

*If `recipient` is null, the message is treated as a Global Broadcast.*

---

# Folder Structure

```text
peerchat/
│
├── main.py             # Entry point (Handles CLI arguments for Port/Username)
├── config.py           # Runtime settings (Username, Peer ID, Port)
│
├── keys/               # Secure storage for RSA keys
│   ├── Alice_private.pem
│   └── Alice_public.pem
│
├── gui/
│   ├── chat_window.py  # Filtered UI logic & Context Switching
│   └── signals.py      # Event bus (3-part signaling: Sender, Msg, Recipient)
│
├── network/
│   ├── server.py       # Handshake, Routing & Signal Emission
│   ├── client.py       # Connection & Transmission logic
│   └── discovery.py    # Global peer registry
│
├── security/
│   └── keys.py         # Key generation, hashing, and filename management
│
└── storage/
    └── database.py     # SQLite history (get_history, save_message)

```

---

# Running PeerChat

## Install Dependencies

```bash
pip install pyqt6 cryptography

```

## Running Multiple Instances

To run peers locally, provide the **Port** and **Username** as arguments. The system will automatically generate or load keys for that username.

**Terminal 1 (Alice):**

```bash
python main.py 5000 Alice

```

**Terminal 2 (Bob):**

```bash
python main.py 5001 Bob

```

**Terminal 3 (Charlie):**

```bash
python main.py 5002 Charlie

```

---

# Planned Improvements

* **E2EE Messaging:** Encrypting message payloads with RSA Public Keys/AES-GCM.
* **NAT Traversal:** UDP hole punching and STUN support for over-the-internet P2P.
* **Advanced UI:** Unread message indicators and file transfer progress bars.

---

# License

MIT License. See `LICENSE` for details.