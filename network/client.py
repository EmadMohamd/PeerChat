import socket, threading, time, config
from network.protocol import create_packet
from network.discover import connected_peers, known_peers, BOOTSTRAP_PEERS, add_known_peer, network_lock

private_key, public_key = None, None


def init_client_keys():
    global private_key, public_key
    from security.keys import ensure_keys_exist, load_private_key, load_public_key
    ensure_keys_exist()
    private_key, public_key = load_private_key(), load_public_key()


def connect_to_peer(ip, port, receive_loop):
    port, my_port = int(port), int(config.PORT)
    if ip == "127.0.0.1" and port == my_port: return
    with network_lock:
        if (ip, port) in connected_peers: return
    if ip == "127.0.0.1" and my_port > port: time.sleep(0.2)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3.0)
        sock.connect((ip, port))
        sock.settimeout(None)

        threading.Thread(target=receive_loop, args=(sock,), daemon=True).start()

        from security.keys import public_key_to_pem
        sock.sendall(create_packet("identity", {
            "peer_id": config.PEER_ID, "public_key": public_key_to_pem(public_key), "listening_port": my_port
        }))
    except:
        pass


def handle_challenge(sock, challenge):
    from security.crypto import sign_message
    signature = sign_message(private_key, challenge)
    try:
        sock.sendall(create_packet("challenge_response", {"signature": signature.hex()}))
    except:
        pass


def send_chat_message(message, target_peer_id=None):
    from network.protocol import create_packet
    from network.discover import network_lock, peer_ids, authenticated_peers
    import config

    packet = create_packet("chat", {
        "sender": config.PEER_ID,
        "recipient": target_peer_id,
        "message": message
    })

    sent_peers = set()  # Tracks unique peer IDs that have received the packet

    with network_lock:
        # Create a safe snapshot of current authenticated connections
        active_sockets = [sock for sock in authenticated_peers if sock in peer_ids]

        for sock in active_sockets:
            p_id = peer_ids[sock]

            # 1. If it's a direct message, only send it to the matching target
            if target_peer_id and p_id != target_peer_id:
                continue

            # 2. Prevent duplicate transmissions to the same logical identity
            if p_id in sent_peers:
                continue

            try:
                sock.sendall(packet)
                sent_peers.add(p_id)
            except:
                pass


def start_discovery_loop(receive_loop):
    def loop():
        for ip, port in BOOTSTRAP_PEERS:
            if int(port) != int(config.PORT): add_known_peer(ip, port)
        while True:
            with network_lock:
                targets = list(known_peers)
            for ip, port in targets:
                with network_lock:
                    linked = (ip, port) in connected_peers
                if not linked: connect_to_peer(ip, port, receive_loop)

            from network.discover import get_all_connections
            all_socks = get_all_connections()
            if all_socks:
                p = create_packet("peer_request", {})
                for sock in all_socks:
                    try:
                        sock.sendall(p)
                    except:
                        pass
            time.sleep(4)

    threading.Thread(target=loop, daemon=True).start()