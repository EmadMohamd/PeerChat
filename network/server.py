import socket
import threading
import secrets
import config

from network.protocol import parse_packet, create_packet
from network.discover import (
    known_peers,
    connected_peers,
    authenticated_peers,
    peer_public_keys,
    pending_challenges,
    peer_ids  # Ensure this is in your discover.py
)
from storage.database import save_message
from security.keys import pem_to_public_key
from security.crypto import verify_signature

HOST = "127.0.0.1"


def receive_loop(conn):
    # makefile('rb') creates a file-like object to read line-by-line
    # This is critical for parsing newline-delimited JSON
    f = conn.makefile('rb')

    while True:
        try:
            line = f.readline()
            if not line:
                break

            packet = parse_packet(line)
            p_type = packet["type"]
            p_data = packet["data"]

            # =========================
            # 1. IDENTITY (The Handshake)
            # =========================
            if p_type == "identity":
                peer_id = p_data["peer_id"]
                pub_key = pem_to_public_key(p_data["public_key"])

                # Link the socket to the Peer's Name for the GUI sidebar
                peer_ids[conn] = peer_id
                peer_public_keys[conn] = pub_key

                # Prepare a random challenge for the peer to sign
                challenge = secrets.token_hex(16)
                pending_challenges[conn] = challenge

                conn.send(create_packet("challenge", {"challenge": challenge}))

            # =========================
            # 2. CHALLENGE RESPONSE
            # =========================
            elif p_type == "challenge_response":
                signature = bytes.fromhex(p_data["signature"])
                challenge = pending_challenges.get(conn)
                public_key = peer_public_keys.get(conn)

                if challenge and public_key and verify_signature(public_key, challenge, signature):
                    authenticated_peers.add(conn)
                    print(f"[AUTHENTICATED] {peer_ids.get(conn)} is verified.")
                else:
                    print("[AUTH FAILED] Closing connection.")
                    break

            # =========================
            # 3. CHALLENGE (Peer challenging US)
            # =========================
            elif p_type == "challenge":
                from network.client import handle_challenge
                handle_challenge(conn, p_data["challenge"])

            # =========================
            # 4. CHAT (Filtered Logic)
            # =========================
            elif p_type == "chat":
                if conn not in authenticated_peers:
                    continue

                recipient = p_data.get("recipient")
                sender = p_data["sender"]
                message = p_data["message"]

                # Logic: Is this for everyone or specifically for me?
                my_id = str(config.PEER_ID)
                target_id = str(recipient) if recipient else None

                if target_id is None or target_id == my_id:
                    from gui.signals import event_bus

                    # Prefix helps the GUI sort into the right "bucket"
                    prefix = "(Private)" if target_id == my_id else "(Global)"
                    display_msg = f"{prefix} {sender}: {message}"

                    event_bus.message_received.emit(display_msg)
                    save_message(sender, message)

            # =========================
            # 5. PEER DISCOVERY
            # =========================
            elif p_type == "peer_request":
                conn.send(create_packet("peer_response", list(known_peers)))

            elif p_type == "peer_response":
                from network.client import connect_to_peer
                for ip, port in p_data:
                    if (ip, port) not in known_peers:
                        known_peers.add((ip, port))
                        connect_to_peer(ip, port, receive_loop)

        except Exception as e:
            print(f"[SERVER ERROR] {e}")
            break

    # CLEANUP: Remove data when peer disconnects
    if conn in peer_ids: del peer_ids[conn]
    if conn in peer_public_keys: del peer_public_keys[conn]
    if conn in pending_challenges: del pending_challenges[conn]
    authenticated_peers.discard(conn)
    conn.close()


def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, port))
    server.listen()

    print(f"[LISTENING] {HOST}:{port}")

    while True:
        conn, addr = server.accept()
        connected_peers[addr] = conn

        thread = threading.Thread(target=receive_loop, args=(conn,))
        thread.daemon = True
        thread.start()

        # Immediately send our identity so the other side can authenticate us
        from network.client import send_identity
        send_identity(conn)