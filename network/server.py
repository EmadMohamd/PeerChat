import socket
import threading
import secrets

from network.protocol import (
    parse_packet,
    create_packet
)

from network.discover import (
    known_peers,
    connected_peers,
    authenticated_peers,
    peer_public_keys,
    pending_challenges
)

from storage.database import save_message

from security.keys import pem_to_public_key

from security.crypto import verify_signature

HOST = "127.0.0.1"


def receive_loop(conn):

    while True:

        try:

            data = conn.recv(4096)

            if not data:
                break

            packet = parse_packet(data)

            packet_type = packet["type"]

            # =========================
            # IDENTITY
            # =========================

            if packet_type == "identity":

                peer_id = packet["data"]["peer_id"]

                public_key_pem = packet["data"]["public_key"]

                public_key = pem_to_public_key(
                    public_key_pem
                )

                peer_public_keys[conn] = public_key

                challenge = secrets.token_hex(16)

                pending_challenges[conn] = challenge

                response = create_packet(
                    "challenge",
                    {
                        "challenge": challenge
                    }
                )

                conn.send(response)

            # =========================
            # CHALLENGE RESPONSE
            # =========================

            elif packet_type == "challenge_response":

                signature = bytes.fromhex(
                    packet["data"]["signature"]
                )

                challenge = pending_challenges[conn]

                public_key = peer_public_keys[conn]

                valid = verify_signature(
                    public_key,
                    challenge,
                    signature
                )

                if valid:

                    authenticated_peers.add(conn)

                    print("[AUTHENTICATED]")

                else:

                    print("[AUTH FAILED]")

                    conn.close()

            # =========================
            # CHALLENGE
            # =========================

            elif packet_type == "challenge":

                from network.client import handle_challenge

                challenge = packet["data"]["challenge"]

                handle_challenge(conn, challenge)

            # =========================
            # CHAT
            # =========================

            elif packet_type == "chat":

                if conn not in authenticated_peers:
                    print("[REJECTED UNAUTHENTICATED MESSAGE]")

                    continue

                sender = packet["data"]["sender"]

                message = packet["data"]["message"]

                from gui.signals import event_bus

                event_bus.message_received.emit(

                    f"<b>{sender}:</b> {message}"

                )

                save_message(sender, message)

            # =========================
            # PEER REQUEST
            # =========================

            elif packet_type == "peer_request":

                response = create_packet(
                    "peer_response",
                    list(known_peers)
                )

                conn.send(response)

            # =========================
            # PEER RESPONSE
            # =========================

            elif packet_type == "peer_response":

                peers = packet["data"]

                from network.client import connect_to_peer

                for peer in peers:

                    ip, port = peer

                    if (ip, port) not in known_peers:

                        known_peers.add((ip, port))

                        print(f"[DISCOVERED] {ip}:{port}")

                        connect_to_peer(
                            ip,
                            port,
                            receive_loop
                        )

        except Exception as e:

            print(e)

            break

    conn.close()


def start_server(port):

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.bind((HOST, port))

    server.listen()

    print(f"[LISTENING] {HOST}:{port}")

    while True:

        conn, addr = server.accept()

        print(f"[NEW CONNECTION] {addr}")

        connected_peers[addr] = conn

        thread = threading.Thread(
            target=receive_loop,
            args=(conn,)
        )

        thread.daemon = True

        thread.start()