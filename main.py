import sys
import threading
import time
import socket
from PyQt6.QtWidgets import QApplication
from pathlib import Path
import config
from network.server import start_server
from network.client import init_client_keys
from security.keys import ensure_keys_exist
from gui.app import start_gui
from gui.config_window import ConfigWindow  # IMPORTED: New isolated layout module

sys.path.insert(0, str(Path(__file__).resolve().parent))


def get_runtime_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        s.close()
    return local_ip


def start_network(my_port):
    """Launches the localized binding instance safely."""
    server_thread = threading.Thread(target=start_server, args=(my_port,), daemon=True)
    server_thread.start()
    print(f"[MAIN] Server process bound and running on listening port: {my_port}")

    time.sleep(1)
    print(f"[MAIN] Background peer discovery system fully deployed.")


if __name__ == "__main__":
    # Create the single global Qt Application instance needed for windows
    app = QApplication(sys.argv)

    # Check if configurations are missing from sys.argv CLI parsing
    if len(sys.argv) < 3:
        # Load the newly separated interactive GUI settings prompt
        config_screen = ConfigWindow()
        config_screen.show()

        # Blocks and processes the execution window safely until closed
        app.exec()

        # If the user closed out of configuration window without submitting data, abort cleanly
        if config_screen.username is None or config_screen.port is None:
            print("[MAIN] Configuration setup cancelled. Exiting.")
            sys.exit(0)

        # Extract variables from state container objects
        runtime_port = config_screen.port
        runtime_user = config_screen.username
    else:
        # Fallback implementation directly supports standard CLI arg bindings
        runtime_port = int(sys.argv[1])
        runtime_user = sys.argv[2]

    # Assign state parameters over to static system scope variables
    config.PORT = runtime_port
    config.USERNAME = runtime_user

    # Storing node structural ID parameters safely
    node_id = ensure_keys_exist()
    config.PEER_ID = node_id

    current_lan_ip = get_runtime_lan_ip()

    print(f"--- PeerChat Network Mode ---")
    print(f"User Identification: {config.USERNAME}")
    print(f"Cryptographic ID:    {config.PEER_ID}")
    print(f"Local Network IP:    {current_lan_ip}")
    print(f"Listening Port:      {config.PORT}")
    print(f"-----------------------------")

    init_client_keys()

    network_thread = threading.Thread(target=start_network, args=(config.PORT,), daemon=True)
    network_thread.start()

    # Pass primary application execution over to the main GUI chat dashboard window context
    start_gui()