import socket, threading, secrets, config
from network.protocol import parse_packet, create_packet
from network.discover import (
    connected_peers, authenticated_peers, peer_public_keys, pending_challenges,
    peer_ids, add_known_peer, remove_connection, network_lock,
    register_authenticated_connection, get_authenticated_peer_addresses
)
from storage.database import save_message
from security.keys import pem_to_public_key
from security.crypto import verify_signature

HOST = "127.0.0.1"


def push_routing_table(target_sock):
    peers = [[ip, port] for ip, port in get_authenticated_peer_addresses()]
    peers.append([HOST, int(config.PORT)])
    try:
        target_sock.sendall(create_packet("peer_response", {"peers": peers}))
    except:
        pass


def broadcast_new_peer(new_ip, new_port, exception_sock):
    packet = create_packet("peer_response", {"peers": [[new_ip, int(new_port)]]})
    with network_lock:
        all_socks = list(authenticated_peers)
    for sock in all_socks:
        if sock != exception_sock:
            try:
                sock.sendall(packet)
            except:
                pass


def receive_loop(conn):
    f = conn.makefile('rb')
    remote_listening_addr, temp_peer_id = None, None

    while True:
        try:
            line = f.readline()
            if not line: break
            packet = parse_packet(line)
            p_type, p_data = packet["type"], packet["data"]

            if p_type == "identity":
                temp_peer_id = p_data["peer_id"]
                remote_listening_addr = (conn.getpeername()[0], int(p_data["listening_port"]))
                if remote_listening_addr[0] == "127.0.0.1" and remote_listening_addr[1] == int(config.PORT): break

                with network_lock:
                    peer_public_keys[conn] = pem_to_public_key(p_data["public_key"])
                challenge = secrets.token_hex(16)
                with network_lock:
                    pending_challenges[conn] = challenge
                conn.sendall(create_packet("challenge", {"challenge": challenge}))

            elif p_type == "challenge_response":
                with network_lock:
                    ch, pub = pending_challenges.get(conn), peer_public_keys.get(conn)
                if ch and pub and verify_signature(pub, ch, bytes.fromhex(p_data["signature"])):
                    if remote_listening_addr and temp_peer_id:
                        register_authenticated_connection(remote_listening_addr[0], remote_listening_addr[1], conn,
                                                          temp_peer_id)
                        conn.sendall(create_packet("peer_welcome",
                                                   {"peer_id": config.PEER_ID, "listening_port": int(config.PORT)}))
                        push_routing_table(conn)
                        broadcast_new_peer(remote_listening_addr[0], remote_listening_addr[1], conn)
                else:
                    break

            elif p_type == "peer_welcome":
                register_authenticated_connection(conn.getpeername()[0], int(p_data["listening_port"]), conn,
                                                  p_data["peer_id"])

            elif p_type == "challenge":
                from network.client import handle_challenge
                handle_challenge(conn, p_data["challenge"])


            elif p_type == "chat":

                with network_lock:

                    authenticated = conn in authenticated_peers

                if not authenticated:
                    continue

                sender = p_data["sender"]

                recipient = p_data.get("recipient")

                message = p_data["message"]

                # FIX: If the sender is our own ID, do not save it again or emit a signal!

                # We already wrote it to our DB and UI when pressing 'Send' in chat_window.py

                if sender == config.PEER_ID:
                    continue

                # Process and save incoming messages from external peers exactly once

                save_message(sender, message, recipient)

                from gui.signals import event_bus

                event_bus.message_received.emit(sender, message, recipient)

            elif p_type == "peer_request":
                with network_lock:
                    authenticated = conn in authenticated_peers
                if authenticated: push_routing_table(conn)

            elif p_type == "peer_response":
                from network.client import connect_to_peer
                for ip, port in p_data.get("peers", []):
                    port = int(port)
                    if ip == HOST and port == int(config.PORT): continue
                    with network_lock:
                        connected = (ip, port) in connected_peers
                    if not connected:
                        add_known_peer(ip, port)
                        connect_to_peer(ip, port, receive_loop)
        except:
            break
    remove_connection(conn)


def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, port))
    server.listen()
    from network.client import start_discovery_loop
    start_discovery_loop(receive_loop)
    while True:
        try:
            conn, _ = server.accept()
            threading.Thread(target=receive_loop, args=(conn,), daemon=True).start()
        except:
            pass