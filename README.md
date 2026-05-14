# PeerChat — Secure Decentralized P2P Messaging System

PeerChat is a decentralized peer-to-peer messaging platform written in Python. Each node acts as both a client and server, enabling direct encrypted communication without relying on a centralized backend.

The system now supports:

* **Context-Aware Filtering:** Private messages are isolated from Global Chat via a dual-pane UI.
* **Automatic Peer Discovery:** Dynamic network expansion through bootstrap peers.
* **RSA Identity Verification:** Secure challenge-response authentication.
* **Modernized GUI:** Polished PyQt6 interface with dark mode and sidebar navigation.
* **Local Persistence:** Message history stored via SQLite.

---

# Features

## Networking

* Fully decentralized peer-to-peer architecture.
* TCP socket communication with newline-delimited JSON streaming.
* Automatic peer discovery through bootstrap peers and dynamic peer list exchange.
* Multi-peer simultaneous communication with continuous receive loops.

## Security

* **RSA Public/Private Keys:** Identity proven via cryptographic signatures.
* **Challenge-Response Flow:** Prevents identity spoofing without ever transmitting private keys or passwords.
* **Key Isolation:** All sensitive `.pem` files are stored in a dedicated `keys/` directory.

## Messaging

* **Direct Private Messaging:** Target specific peers for 1-on-1 filtered conversations.
* **Global Broadcast:** Message all connected peers in the swarm.
* **JSON Packet Protocol:** Structured communication for identity, challenges, and chat.

## GUI

* **Modern PyQt6 Interface:** Sidebar for peer selection and a sleek dark-themed chat area.
* **Identity Header:** Clear display of "Peer Chat" title and your unique Peer ID at the top right.
* **Contextual History:** Automatic message sorting based on the selected peer in the sidebar.

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

PeerChat uses cryptographic authentication instead of passwords.

```text
Connect
   ↓
Exchange public keys (Identity Packet)
   ↓
Generate random challenge
   ↓
Sign challenge with private key
   ↓
Verify signature using public key
   ↓
Authenticated communication begins

```

---

# Message Protocol

## Chat Packet (Direct/Global)

```json
{
    "type": "chat",
    "data": {
        "sender": "5001",
        "recipient": "5002", 
        "message": "Hello!"
    }
}

```

*If `recipient` is null, the message is treated as Global.*

## Identity Packet

```json
{
    "type": "identity",
    "data": {
        "peer_id": "5001",
        "public_key": "PEM_STRING"
    }
}

```

---

# Folder Structure

```text
peerchat/
│
├── main.py
├── config.py           # Local settings (Peer ID, Ports)
│
├── keys/               # Secure storage for RSA keys
│   ├── private.pem
│   └── public.pem
│
├── gui/
│   ├── app.py          # GUI Launcher
│   ├── chat_window.py  # Filtered UI logic & Context Switching
│   └── signals.py      # Event bus
│
├── network/
│   ├── protocol.py     # Packet creation/parsing
│   ├── server.py       # Handshake & Routing
│   ├── client.py       # Connection logic
│   └── discovery.py    # Global peer registry
│
├── security/
│   ├── keys.py         # Key management & folder logic
│   └── crypto.py       # Signing/Verification
│
└── storage/
    └── database.py     # SQLite history

```

---

# Module Overview

## `network/`

Handles all socket communication, peer discovery, and packet parsing.

* `server.py`: Incoming connections, handshake verification, and message routing.
* `client.py`: Outgoing connections and packet transmission.
* `discovery.py`: Maintains the list of authenticated `peer_ids` for the GUI.

## `security/`

Handles cryptographic tasks.

* `keys.py`: RSA key generation and directory enforcement (`/keys`).
* `crypto.py`: Signature creation and verification.

---

# Running PeerChat

## Install Dependencies

```bash
pip install pyqt6 cryptography

```

## Running Multiple Instances

Run each peer in a new terminal window:

**Terminal 1:** `python main.py 5000 <PEER ID>`

**Terminal 2:** `python main.py 5001 <PEER ID>`

**Terminal 3:** `python main.py 5002 <PEER ID>`

---

# Planned Improvements

* **E2EE Messaging:** Encrypting message payloads with RSA Public Keys/AES-GCM.
* **NAT Traversal:** UDP hole punching and STUN support for over-the-internet P2P.
* **Advanced UI:** Unread message indicators, file transfer progress bars, and custom themes.
* **DHT Integration:** Kademlia-based distributed hash table for decentralized node discovery at scale.

---

# License

MIT License. See `LICENSE` for details.