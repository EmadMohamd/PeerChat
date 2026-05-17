from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QLabel, QListWidget, QSplitter
)
from PyQt6.QtCore import Qt, QTimer
from gui.signals import event_bus
from network.client import send_chat_message
from storage.database import get_history, save_message
import config


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PeerChat")
        self.resize(900, 650)

        # State management
        self.current_chat_target = "Global Chat"

        # GUI Deduplication tracking to prevent signal echos
        self.recent_rendered_messages = set()

        self.init_ui()

        # Connect network signals safely
        event_bus.message_received.connect(self.handle_incoming_signal)

        # Peer list refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_peer_list)
        self.refresh_timer.start(2000)

        # Load initial Global Chat history on startup
        self.load_history_from_db()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget { background-color: #1e1e2e; color: #cdd6f4; font-family: 'Segoe UI', sans-serif; }
            QTextEdit { background-color: #181825; border-radius: 10px; border: 1px solid #313244; padding: 10px; font-size: 14px; }
            QListWidget { background-color: #181825; border-radius: 10px; border: 1px solid #313244; outline: none; }
            QListWidget::item { padding: 12px; border-bottom: 1px solid #313244; color: #a6adc8; }
            QListWidget::item:selected { background-color: #89b4fa; color: #11111b; border-radius: 5px; }
            QLineEdit { background-color: #313244; border-radius: 15px; padding: 10px 15px; border: 1px solid #45475a; }
            QPushButton { background-color: #89b4fa; color: #11111b; border-radius: 15px; padding: 10px 25px; font-weight: bold; }
            QPushButton:hover { background-color: #b4befe; }
            #AppTitle { font-size: 24px; font-weight: bold; color: #89b4fa; }
            #MyIDLabel { color: #9399b2; font-size: 17px; }
            #ChatStatus { font-size: 16px; font-weight: bold; color: #fab387; }
            #SidebarHeader { font-weight: bold; color: #585b70; font-size: 11px; margin-bottom: 5px; }
        """)

        layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- SIDEBAR SECTION ---
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_header = QLabel("ONLINE PEERS")
        sidebar_header.setObjectName("SidebarHeader")

        self.peer_list_widget = QListWidget()
        self.peer_list_widget.addItem("Global Chat")
        self.peer_list_widget.setCurrentRow(0)
        self.peer_list_widget.itemClicked.connect(self.switch_chat_context)

        sidebar_layout.addWidget(sidebar_header)
        sidebar_layout.addWidget(self.peer_list_widget)

        # --- MAIN CHAT SECTION ---
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)

        header_bar = QHBoxLayout()
        app_name = QLabel("Peer Chat")
        app_name.setObjectName("AppTitle")

        my_id_info = QLabel(f"<b>You:</b> <b style='color: #f5e0dc;'>{config.PEER_ID}</b>")
        my_id_info.setObjectName("MyIDLabel")
        my_id_info.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        header_bar.addWidget(app_name)
        header_bar.addStretch()
        header_bar.addWidget(my_id_info)

        self.chat_status_label = QLabel("Global Chat")
        self.chat_status_label.setObjectName("ChatStatus")

        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)

        input_container = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type your message here...")
        self.input_box.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        input_container.addWidget(self.input_box)
        input_container.addWidget(self.send_button)

        chat_layout.addLayout(header_bar)
        chat_layout.addWidget(self.chat_status_label)
        chat_layout.addWidget(self.chat_box)
        chat_layout.addLayout(input_container)

        splitter.addWidget(sidebar_widget)
        splitter.addWidget(chat_container)
        splitter.setSizes([200, 700])
        layout.addWidget(splitter)

    def update_peer_list(self):
        from network.discover import peer_ids
        current_item = self.peer_list_widget.currentItem()
        selected_name = current_item.text() if current_item else "Global Chat"

        self.peer_list_widget.clear()
        self.peer_list_widget.addItem("Global Chat")

        for pid in sorted(peer_ids.values()):
            if str(pid) != str(config.PEER_ID):
                self.peer_list_widget.addItem(str(pid))

        items = self.peer_list_widget.findItems(selected_name, Qt.MatchFlag.MatchExactly)
        if items:
            self.peer_list_widget.setCurrentItem(items[0])

    def switch_chat_context(self, item):
        self.current_chat_target = item.text()

        if self.current_chat_target == "Global Chat":
            self.chat_status_label.setText("Global Chat")
        else:
            self.chat_status_label.setText(f"Private Chat: {self.current_chat_target}")

        self.load_history_from_db()

    def load_history_from_db(self):
        self.chat_box.clear()
        target = None if self.current_chat_target == "Global Chat" else self.current_chat_target

        history = get_history(target)
        for sender, message in history:
            self.append_to_ui(sender, message)

    def send_message(self):
        text = self.input_box.text().strip()
        if not text:
            return

        recipient = None if self.current_chat_target == "Global Chat" else self.current_chat_target

        # 1. Send via network wire
        send_chat_message(text, recipient)

        # 2. Save directly to database
        save_message(config.PEER_ID, text, recipient)

        # FIX: We no longer call handle_incoming_signal manually here. 
        # The database and network threads will sync back down to update the screen cleanly.

        # 3. Direct local print fallback for instantly responsive local context rendering
        self.append_to_ui(config.PEER_ID, text)

        self.input_box.clear()

    def handle_incoming_signal(self, sender, message, recipient):
        """Processes signals and drops echo duplicates coming from loopback threads."""
        # Drop if it's an echo signature of a message we just processed locally
        msg_signature = f"{sender}:{recipient}:{message}"
        if msg_signature in self.recent_rendered_messages:
            return

        # Add to local short-term cache filter
        self.recent_rendered_messages.add(msg_signature)
        QTimer.singleShot(3000, lambda: self.recent_rendered_messages.discard(msg_signature))

        # Do not render if we sent it (send_message already appended it locally)
        if sender == config.PEER_ID:
            return

        is_global_msg = (recipient is None)

        show_now = False
        if is_global_msg and self.current_chat_target == "Global Chat":
            show_now = True
        elif recipient == config.PEER_ID and sender == self.current_chat_target:
            show_now = True
        elif sender == config.PEER_ID and recipient == self.current_chat_target:
            show_now = True

        if show_now:
            self.append_to_ui(sender, message)

    def append_to_ui(self, sender, message):
        is_me = (sender == config.PEER_ID)
        color = "#f5c2e7" if is_me else "#89b4fa"
        sender_label = "You" if is_me else sender

        formatted = f"<div style='margin-bottom: 8px;'><b style='color: {color};'>{sender_label}:</b> {message}</div>"
        self.chat_box.append(formatted)
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        scrollbar = self.chat_box.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())