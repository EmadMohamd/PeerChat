# PeerChat — Secure Decentralized P2P Messaging System

PeerChat is a decentralized peer-to-peer messaging platform written in Python. Each node acts as both a client and server, enabling direct encrypted communication without relying on a centralized backend. **Identity is cryptographically derived from RSA keys, ensuring that each user is uniquely identifiable and resistant to spoofing.**

The system supports:

* Context-aware private and global messaging
* Automatic peer discovery across LAN and local environments
* RSA-based challenge-response authentication
* Persistent message history with timestamps
* File transfer via Base64-encoded packets
* Modernized, smooth-corner PyQt6 user interface with localized startup configuration view

---

# Releases & Downloads

## 🚀 v1.1.0 — The Multimedia Upgrade

This release brings integrated voice messaging, media processing capabilities, and live playback heads right into the decentralized interface layout.

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
* **Voice Messaging:** Dedicated audio capture state machine (`🎤`/`🛑`) converting hardware input into wave blocks on the fly
* File attachments with automatic download handling and live rendering
* JSON-based message protocol for structured routing
* Local persistence of all messages, audio tracks, and file references via SQLite
* Timestamped message history for accurate chronological reconstruction
* Received files and voice notes are automatically saved to the `downloads/` directory

---

## GUI

The interface has been fully updated to a sleek, modern visual aesthetic based on the dark palette theme.

### Configuration Window (Startup Screen)

* **Glitch-Free UI Rendering:** Fixed setup sizing prevents scaling artifact flickering.
* **Modern Geometric Aesthetics:** High-contrast color assignments utilizing a custom vector layout engine.
* **Validation Subsystem:** Automated networking field sanity checkers before binding.

### Main Chat Window

* **Enhanced Peer List:** 
* **Integrated Control Panels:** 
* **Real-Time Indicators:** 
* **Audio Execution HUD:**
* **Message delivery status indicators (✓ / ✓✓)**

---

# Architecture

![Peer_Discovery_Flow](assets/Peer_Discovery.png)

Each peer contains:

* Configuration interface launcher or CLI interceptor
* Listener server & outgoing client connector
* Message handler & peer discovery engine
* **Audio Capture & Rendering Engines (`PyQt6.QtMultimedia` pipeline)**
* Authentication layer (RSA challenge-response)
* Local SQLite database with timestamped history
* PyQt6 frontend with real-time updates

---

# Authentication Flow

PeerChat uses cryptographic verification instead of passwords.

![Peer_Discovery_Flow](assets/auth_flow.png)

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

## File & Voice Note Transfer Packet

Voice notes take advantage of the structural file transport layout, creating temporary `.wav` tracking binaries before running them through the network encoder wrapper:

```json
{
  "type": "file_transfer",
  "data": {
    "sender": "Alice-a1b2c3d4",
    "recipient": "Bob-e5f6g7h8",
    "file_name": "vnote_1719520109.wav",
    "payload": "BASE64_ENCODED_AUDIO_DATA..."
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
├── assets/             # Static UI resources (icons, logos, images)
│   ├── logo.ico
│   ├── logo.svg
│   ├── peerchat.ico
│   └── peerchat.svg
│
├── keys/               # RSA key storage per user
│   ├── Alice_private.pem
│   └── Alice_public.pem
│
├── downloads/          # Received file attachments and voice notes (.wav, .mp3, etc.)
│
├── gui/
│   ├── app.py          # GUI launcher
│   ├── config_window.py# Smooth anti-flicker configuration screen
│   ├── chat_window.py  # UI, rich text media playback triggers & message rendering logic
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

To run PeerChat with full multimedia capture and system audio playback support, ensure you have the updated requirements installed:

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
python main.py 9000 Bootstrap_node

```

### Terminal 2

```bash
python main.py 9001 Bootstrap_node_1

```

### Terminal 3

```bash
python main.py 9002 Bootstrap_node_2

```

And then after initializing the Bootstrap peers you can start your peers:

### Terminal 4

```bash
python main.py <Port> <Username>

```

---

# Bootstrap Peers Configuration

PeerChat uses default bootstrap peers config to initialize network discovery. These are defined in `network/discovery.py`:

```python
BOOTSTRAP_PEERS = [
    ("192.168.1.2", 9000),
    ("192.168.1.3", 9001),
    ("127.0.0.1", 9002)
]

```

## LAN Setup

For local network deployment, replace IPs with the LAN address of your machines with these or you can choose your desired IPs:

```python
BOOTSTRAP_PEERS = [
    ("192.168.1.2", 9000),
    ("192.168.1.3", 9001)
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

* Typing indicators
* File transfer progress bars

---

# License

MIT License. See `LICENSE` for details.