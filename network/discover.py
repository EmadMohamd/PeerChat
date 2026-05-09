# network/discovery.py

authenticated_peers = set()

peer_public_keys = {}

pending_challenges = {}

# Stores all discovered peers
# Format:
# {
#     ("127.0.0.1", 5001),
#     ("127.0.0.1", 5002)
# }
known_peers = set()


# Stores active socket connections
# Format:
# {
#     ("127.0.0.1", 5001): socket_object
# }
connected_peers = {}


# Initial peers known when app starts
# These are only for bootstrapping
BOOTSTRAP_PEERS = [
    ("127.0.0.1", 5000),
    ("127.0.0.1", 5001),
    ("127.0.0.1", 5002),
]


def add_known_peer(ip, port):

    """
    Add peer to discovered peer list.
    """

    known_peers.add((ip, port))


def remove_known_peer(ip, port):

    """
    Remove peer from known peers.
    """

    if (ip, port) in known_peers:

        known_peers.remove((ip, port))


def add_connection(ip, port, sock):

    """
    Store active socket connection.
    """

    connected_peers[(ip, port)] = sock


def remove_connection(ip, port):

    """
    Remove disconnected socket.
    """

    if (ip, port) in connected_peers:

        try:
            connected_peers[(ip, port)].close()

        except:
            pass

        del connected_peers[(ip, port)]


def is_connected(ip, port):

    """
    Check whether already connected.
    """

    return (ip, port) in connected_peers


def get_all_known_peers():

    """
    Return all discovered peers.
    """

    return list(known_peers)


def get_all_connections():

    """
    Return all active sockets.
    """

    return connected_peers.values()


def print_known_peers():

    """
    Debug helper.
    """

    print("\n=== KNOWN PEERS ===")

    if not known_peers:

        print("No known peers")

    for ip, port in known_peers:

        print(f"{ip}:{port}")

    print("===================\n")


def print_connected_peers():

    """
    Debug helper.
    """

    print("\n=== CONNECTED PEERS ===")

    if not connected_peers:

        print("No active connections")

    for ip, port in connected_peers:

        print(f"{ip}:{port}")

    print("=======================\n")