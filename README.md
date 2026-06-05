# PeerChat — Secure Decentralized P2P Messaging System

PeerChat is a decentralized peer-to-peer messaging platform written in Python. Each node acts as both a client and server, enabling direct encrypted communication without relying on a centralized backend. **Identity is cryptographically derived from RSA keys, ensuring that each user is uniquely identifiable and resistant to spoofing.**

The system supports:

* Context-aware private and global messaging
* Automatic peer discovery across LAN and local environments
* RSA-based challenge-response authentication
* Persistent message history with timestamps
* Online/offline peer visibility tracking
* File transfer via Base64-encoded packets
* Modernized, smooth-corner PyQt6 user interface with localized startup configuration view

---

# Releases & Downloads

## 🚀 v1.0.0 — The Initial Decentralized Release

This marks the first stable release of PeerChat, moving the project from a command-line proof-of-concept to a fully-realized desktop application with a modern graphical interface.

### Release Notes

* **Standalone Executables:** Packaged binaries for quick deployment without needing a local Python environment.
* **Cryptographic Identity Core:** Fully integrated the RSA key generation and challenge-response handshake to eliminate traditional password systems.
* **Anti-Flicker GUI Engine:** Implemented locked structural layouts in PyQt6 to ensure a glitch-free configuration startup sequence.
* **Cross-Platform File Exchange:** Validated Base64-encoded file chunking for seamless document sharing between different operating systems.

### Binary Downloads

* 🖥️ **Windows (x64):** `peerchat.exe` 

> ⚠️ **Note on Build Generation:** If compiling from source using PyInstaller, use the following command to match the official release naming convention:
> ```bash
> pyinstaller --onefile --windowed --name=peerchat --icon=assets/peerchat.ico main.py
> 
> ```
> 
> 

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

The interface has been fully updated to a sleek, modern visual aesthetic based on the dark palette theme.

### Configuration Window (Startup Screen)

* **Glitch-Free UI Rendering:** Form fields use locked structural bounds and anti-flicker layout placeholders to prevent font shaking or popping on app initialization.
* **Modern Geometric Aesthetics:** Features soft floating container cards with rounded corners (24px border-radius).
* **Validation Subsystem:** Handles improper or unassigned form fields locally before spinning up network socket resources.

### Main Chat Window

* **Enhanced Peer List:** Bold, high-contrast typography displaying active peer statuses against rich background blocks for excellent visibility.
* **Integrated Control Panels:** The attachment clip button (`📎`) and message entry boxes are seamlessly styled side-by-side inside custom inner frames.
* **Real-Time Indicators:** Real-time online/offline peer visibility tracking:
* 🟢 Online (currently connected)
* ⚫ Offline (seen before but not currently connected)



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

* Configuration interface launcher or CLI interceptor
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
├── main.py             # Entry point (Launches Configuration GUI or parses fallback args)
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
│   ├── config_window.py# Smooth anti-flicker configuration screen
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

# Running PeerChat from Source

## Install Dependencies

```bash
pip install pyqt6 cryptography

```

---

## Running via Configuration GUI

You can launch PeerChat without flags. A high-contrast setup screen will collect your configurations before starting network listeners:

```bash
python main.py

```

---

## Running via Classic Terminal Fallback

The entry system retains full backward compatibility for command-line arguments:

### Terminal 1

```bash
python main.py 9000 Alice

```

### Terminal 2

```bash
python main.py 9001 Bob

```

---

# Bootstrap Peers Configuration

PeerChat uses bootstrap peers to initialize network discovery. These are defined in `network/discovery.py`:

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