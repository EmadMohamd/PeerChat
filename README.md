# PeerChat — Secure Decentralized P2P Messaging System

PeerChat is a decentralized peer-to-peer messaging platform written in Python. Each node acts as both a client and server, enabling direct encrypted communication without relying on a centralized backend. **Identity is cryptographically derived from RSA keys, ensuring that each user is uniquely identifiable and resistant to spoofing.**

The system supports:

* Context-aware private and global messaging
* Automatic peer discovery across LAN and local environments
* RSA-based challenge-response authentication
* Persistent message history with timestamps
* Online/offline peer visibility tracking
* File transfer via Base64-encoded packets
* Modern PyQt6 interface with real-time updates

---

# Features

## Networking & Data Transfer

* Fully decentralized peer-to-peer architecture
* TCP socket communication using newline-delimited JSON packets
* Automatic peer discovery through bootstrap peers and gossip-based routing
* Multi-peer simultaneous communication with continuous receive loops
* Robust file transfer using Base64 encoding to ensure cross-platform integrity
* Network resilience through retry cooldowns and peer revalidation

**Connectivity Note:** At least one bootstrap peer must be reachable for network discovery to begin.

---

## Security

* RSA Public/Private key cryptography for identity verification
* Cryptographic Peer IDs derived from public keys
* Challenge-response authentication prevents impersonation
* No passwords or centralized identity storage
* Secure key storage in local `keys/` directory

---

## Messaging & Sharing

* Direct private messaging between peers
* Global broadcast messaging to all connected peers
* File attachments with automatic download handling
* JSON-based message protocol for structured routing
* Local persistence of all messages and file references
* Timestamped message history for accurate chronological reconstruction

---

## GUI

* Modern PyQt6 interface with dark theme
* Sidebar-based peer navigation system
* Real-time chat window with message rendering
* Attachment button (📎) for file selection
* Display of user identity (Peer ID) in header
* Context-aware message history loading

### Message Features

* Each message includes a timestamp
* Sent and received messages are stored consistently
* History is reconstructed automatically per chat context

### Peer List Features

* Displays **all known peers from history and network discovery**
* Real-time online/offline status indicators:

  * 🟢 Online (currently connected)
  * ⚫ Offline (seen before but not currently connected)
* Peers remain visible even when offline (persistent identity model)

---

# Architecture

```
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

* Listener server & outgoing client connector
* Message handler & peer discovery engine
* Authentication layer (RSA challenge-response)
* Local SQLite database with timestamped history
* PyQt6 frontend with real-time updates

---

# Authentication Flow

PeerChat uses cryptographic verification instead of passwords.

```
1. Connect
   ↓
2. Exchange public keys (identity packet)
   ↓
3. Generate random challenge
   ↓
4. Sign challenge with private key
   ↓
5. Verify signature using public key
   ↓
6. Authenticated communication begins
```

---

# Message Protocol

## Chat Packet (Direct / Global)

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

If `recipient` is `null`, the message is treated as a global broadcast.

---

## File Transfer Packet

```json
{
  "type": "file_transfer",
  "data": {
    "sender": "Alice-a1b2c3d4",
    "recipient": "Bob-e5f6g7h8",
    "file_name": "document.pdf",
    "payload": "BASE64_ENCODED_DATA..."
  }
}
```

---

# Folder Structure

```
peerchat/
│
├── main.py             # Entry point (CLI args: port, username)
├── config.py           # Runtime settings (Peer ID, Port, Username)
│
├── keys/               # RSA key storage per user
│   ├── Alice_private.pem
│   └── Alice_public.pem
│
├── downloads/          # Received file attachments
│
├── gui/
│   ├── app.py          # GUI launcher
│   ├── chat_window.py  # UI + message rendering logic
│   └── signals.py      # Event bus system
│
├── network/
│   ├── server.py       # Handshake, routing, file handling
│   ├── client.py       # Sending messages + file transfers
│   └── discovery.py    # Peer discovery + registry
│
├── security/
│   ├── keys.py         # Key generation & loading
│   └── crypto.py       # Cryptographic utilities
│
└── storage/
    └── database.py     # SQLite persistence layer (timestamps included)
```

---

# Running PeerChat

## Install Dependencies

```bash
pip install pyqt6 cryptography
```

---

## Running Multiple Instances

### Terminal 1

```bash
python main.py 9000 Alice
```

### Terminal 2

```bash
python main.py 9001 Bob
```

### Terminal 3

```bash
python main.py 9002 Charlie
```

---

# Bootstrap Peers Configuration

PeerChat uses bootstrap peers to initialize network discovery.

These are defined in `network/discovery.py`:

```python
BOOTSTRAP_PEERS = [
    ("192.168.1.41", 9000),
    ("192.168.1.41", 9001),
    ("127.0.0.1", 9002)
]
```

## LAN Setup

For local network deployment, replace IPs with the LAN address of your machines:

```python
BOOTSTRAP_PEERS = [
    ("192.168.1.50", 9000),
    ("192.168.1.50", 9001)
]
```

## Local Testing (Single Machine)

```python
BOOTSTRAP_PEERS = [
    ("127.0.0.1", 9000),
    ("127.0.0.1", 9001),
    ("127.0.0.1", 9002)
]
```

At least one bootstrap peer must be online for initial network discovery. Once connected, peers automatically exchange routing information and expand the network.

---

# Planned Improvements

* Message delivery status indicators (✓ / ✓✓)
* Unread message counters
* Typing indicators
* File transfer progress bars

---

# License

MIT License. See `LICENSE` for details.

---