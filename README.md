# PeerChat — Secure Decentralized P2P Messaging System

PeerChat is a decentralized peer-to-peer messaging platform written in Python.
Each node acts as both a client and server, enabling direct encrypted communication without relying on a centralized backend.

The system now supports:

* automatic peer discovery
* dynamic network expansion
* RSA public/private key authentication
* decentralized messaging
* local message persistence
* PyQt6 graphical interface

---

# Features

## Networking

* Fully decentralized peer-to-peer architecture
* TCP socket communication
* Automatic peer discovery through bootstrap peers
* Dynamic peer list exchange
* Auto-connect to newly discovered peers
* Multi-peer simultaneous communication
* Continuous receive loops for real-time messaging

---

## Security

* RSA public/private key authentication
* Challenge-response identity verification
* Cryptographic peer authentication
* No password transmission
* Replay-resistant authentication flow
* Foundation for future AES encrypted messaging

---

## Messaging

* Direct peer messaging
* Broadcast messaging to connected peers
* JSON packet protocol
* Local SQLite message history
* Real-time message propagation

---

## GUI

* Modern PyQt6 interface
* Real-time chat updates
* Thread-safe UI event system
* Multi-window peer instances
* Extensible architecture for tabs/groups/files

---

# Architecture

```text
                ┌───────────────┐
                │   Peer A      │
                └──────┬────────┘
                       │
         ┌─────────────┼─────────────┐
         │                             │
┌────────▼────────┐         ┌────────▼────────┐
│    Peer B       │         │    Peer C       │
└────────┬────────┘         └────────┬────────┘
         │                             │
         └─────────────┬─────────────┘
                       │
                ┌──────▼────────┐
                │    Peer D     │
                └───────────────┘
```

Each peer contains:

* Listener Server
* Outgoing Client Connector
* Message Handler
* Peer Discovery Engine
* Authentication Layer
* Local Database
* GUI Frontend

---

# Authentication Flow

PeerChat uses cryptographic authentication instead of passwords.

```text
Connect
   ↓
Exchange public keys
   ↓
Generate random challenge
   ↓
Sign challenge with private key
   ↓
Verify signature using public key
   ↓
Authenticated communication begins
```

This ensures peers can prove identity without transmitting secrets.

---

# Peer Discovery Flow

The network expands dynamically.

```text
Bootstrap Peer
      ↓
Request peer list
      ↓
Receive discovered peers
      ↓
Auto-connect
      ↓
Expand network graph
```

Peers continuously exchange known peer information, allowing decentralized discovery similar to distributed systems and overlay networks.

---

# Message Protocol

Messages use JSON packets.

## Chat Packet

```json
{
    "type": "chat",
    "data": {
        "sender": "peer_001",
        "message": "Hello world"
    }
}
```

---

## Identity Packet

```json
{
    "type": "identity",
    "data": {
        "peer_id": "peer_001",
        "public_key": "PEM_PUBLIC_KEY"
    }
}
```

---

## Challenge Packet

```json
{
    "type": "challenge",
    "data": {
        "challenge": "ABCD1234"
    }
}
```

---

## Peer Discovery Packet

```json
{
    "type": "peer_response",
    "data": [
        ["127.0.0.1", 5001],
        ["127.0.0.1", 5002]
    ]
}
```

---

# Folder Structure

```text
peerchat/
│
├── main.py
│
├── gui/
│   ├── __init__.py
│   ├── app.py
│   ├── chat_window.py
│   └── signals.py
│
├── network/
│   ├── __init__.py
│   ├── protocol.py
│   ├── server.py
│   ├── client.py
│   └── discovery.py
│
├── security/
│   ├── __init__.py
│   ├── keys.py
│   └── crypto.py
│
├── storage/
│   ├── __init__.py
│   └── database.py
│
├── private.pem
├── public.pem
│
├── requirements.txt
└── README.md
```

---

# Module Overview

## `network/`

Handles all socket communication, peer discovery, packet parsing, and connection management.

### Components

* `server.py` → incoming connections + packet handling
* `client.py` → outgoing connections + messaging
* `protocol.py` → JSON packet creation/parsing
* `discovery.py` → peer registry and bootstrap discovery

---

## `security/`

Handles cryptographic authentication.

### Components

* `keys.py` → RSA key generation/loading
* `crypto.py` → signing and signature verification

---

## `storage/`

Handles local message persistence using SQLite.

---

## `gui/`

PyQt6 graphical frontend.

### Components

* `app.py` → GUI launcher
* `chat_window.py` → chat interface
* `signals.py` → thread-safe event communication

---

# Installation

## Clone Repository

```bash
git clone <repository-url>
cd peerchat
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install pyqt6 cryptography
```

---

# Running PeerChat

Run multiple peers on different ports.

---

## Terminal 1

```bash
python main.py 5000
```

---

## Terminal 2

```bash
python main.py 5001
```

---

## Terminal 3

```bash
python main.py 5002
```

Each peer automatically:

* generates RSA keys
* starts listening server
* connects to bootstrap peers
* exchanges peer lists
* authenticates peers
* launches GUI

---

# Current Capabilities

* Decentralized networking
* Dynamic peer discovery
* Public/private key authentication
* Automatic network expansion
* Local message history
* Real-time GUI messaging
* Multi-peer communication

---

# Planned Improvements

## Networking

* NAT traversal
* UDP hole punching
* Distributed hash table (DHT)
* Asyncio networking
* Advanced routing

---

## Security

* AES-GCM encrypted messaging
* Session key negotiation
* Perfect forward secrecy
* Peer trust management

---

## GUI

* Chat tabs
* Online peer list
* File transfer UI
* Notifications
* Message bubbles
* Themes

---

## Messaging

* Group chats
* Media/file sharing
* Voice/video calls
* Typing indicators
* Emoji/stickers

---

# Recommended Future Stack

| Purpose         | Technology   |
| --------------- | ------------ |
| GUI             | PyQt6        |
| Networking      | asyncio      |
| Encryption      | cryptography |
| Database        | SQLite       |
| NAT Traversal   | aiortc       |
| Large-scale P2P | libp2p       |

---

# License

This project is licensed under the MIT License.

See the `LICENSE` file for details.
