import sys
import threading
import time
import config
from network.server import (
    start_server,
    receive_loop
)

from network.client import (
    connect_to_peer,
    init_client_keys
)
from network.discover import (
    BOOTSTRAP_PEERS
)

from security.keys import (
    ensure_keys_exist

)

from gui.app import start_gui


def start_network(port):

    server_thread = threading.Thread(
        target=start_server,
        args=(port,)
    )

    server_thread.daemon = True

    server_thread.start()

    time.sleep(2)

    for ip, port in BOOTSTRAP_PEERS:

        if port != MY_PORT:

            connect_to_peer(
                ip,
                port,
                receive_loop
            )


if __name__ == "__main__":

    if len(sys.argv) < 3:

        print("Usage:")
        print("Usage: python main.py <port> <username>")

        sys.exit()

    MY_PORT = int(sys.argv[1])
    config.USERNAME = sys.argv[2]

    peer_id = ensure_keys_exist()
    print(f"--- PeerChat  Started ---")
    print(f"User:    {config.USERNAME}")
    print(f"Net ID:  {config.PEER_ID}")
    print(f"Port:    {config.PORT}")
    print(f"-----------------------------")
    ensure_keys_exist()
    init_client_keys()

    network_thread = threading.Thread(
        target=start_network,
        args=(MY_PORT,)
    )

    network_thread.daemon = True

    network_thread.start()

    start_gui()