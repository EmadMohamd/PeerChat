# Python P2P Chat System

A peer-to-peer (P2P) chat application written in Python. This system allows multiple peers to communicate directly without a central server, supporting direct messaging, broadcasts, and optional encryption.

---

## Features

* Direct Messaging: Send text messages directly to a specific peer.
* Broadcast Messaging: Send messages to all connected peers.
* Multi-Peer Support: Connect multiple peers simultaneously.
* Configurable Peer Identity: Each peer has a unique ID and optional group.
* Message History: Log messages locally with timestamps.
* Optional Encryption: End-to-end encryption for secure messaging.
* Media Transfer: Send files in chunks between peers.
* Automatic Reconnection: Reconnect to peers if connections drop.

---

## Architecture

[Peer A] <----> [Peer B] <----> [Peer C]
     \                          /
      \                        /
       \------ [Peer D] -------

* Listener Server: Each peer runs a server socket to accept connections.
* Client Connector: Each peer can initiate connections to others.
* Message Handler: Processes incoming messages and dispatches to interface.
* Config/Identity: Stores peer-specific ID, credentials, and known peers.

---

## Message Protocol

Messages are JSON objects:

{
    "sender_id": "peer_001",
    "recipient_id": "peer_002",
    "timestamp": "2026-05-01 15:30:12",
    "message_type": "text",
    "content": "Hello, world!"
}

* recipient_id = "all" for broadcast.
* message_type can be text or file.

---

## Security
* Encryption: AES symmetric encryption.
* Authentication: Peers verify identity using public keys.
* Integrity: HMAC signatures prevent message tampering.

---

## Folder Structure

p2p-chat-python/
├─ peer.py            # Main peer script
├─ config.json        # Per-peer configuration
├─ requirements.txt   # Dependencies
├─ utils.py           # Helper functions (networking, encryption)
└─ README.md          # Project documentation

---

## Future Enhancements

* GUI interface (Tkinter or PyQt)
* NAT traversal for peers behind firewalls
* Group chat with peer-to-peer routing
* Persistent message storage across sessions

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
