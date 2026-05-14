from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QLabel, QListWidget, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from gui.signals import event_bus
from network.client import send_chat_message
import config


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PeerChat")
        self.resize(900, 650)

        # State management for filtering
        self.current_chat_target = "Global Chat"
        self.message_history = {"Global Chat": ""}

        self.init_ui()

        # Signals and Timers
        event_bus.message_received.connect(self.handle_incoming_signal)

        # Peer list refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_peer_list)
        self.refresh_timer.start(2000)

    def init_ui(self):
        # Professional Dark Theme Palette
        self.setStyleSheet("""
            QWidget { 
                background-color: #1e1e2e; 
                color: #cdd6f4; 
                font-family: 'Segoe UI', sans-serif; 
            }
            QTextEdit { 
                background-color: #181825; 
                border-radius: 10px; 
                border: 1px solid #313244; 
                padding: 10px; 
                font-size: 14px;
            }
            QListWidget { 
                background-color: #181825; 
                border-radius: 10px; 
                border: 1px solid #313244; 
                outline: none; 
            }
            QListWidget::item { 
                padding: 12px; 
                border-bottom: 1px solid #313244; 
                color: #a6adc8;
            }
            QListWidget::item:selected { 
                background-color: #89b4fa; 
                color: #11111b; 
                border-radius: 5px; 
            }
            QLineEdit { 
                background-color: #313244; 
                border-radius: 15px; 
                padding: 10px 15px; 
                border: 1px solid #45475a; 
            }
            QPushButton { 
                background-color: #89b4fa; 
                color: #11111b; 
                border-radius: 15px; 
                padding: 10px 25px; 
                font-weight: bold; 
            }
            QPushButton:hover { 
                background-color: #b4befe; 
            }
            #AppTitle { font-size: 24px; font-weight: bold; color: #89b4fa; }
            #MyIDLabel { color: #9399b2; font-size: 13px; }
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

        # Top Header: App Name [Stretch] User ID Info
        header_bar = QHBoxLayout()
        app_name = QLabel("Peer Chat")
        app_name.setObjectName("AppTitle")

        my_id_info = QLabel(f"You are logged in as ID: <b style='color: #f5e0dc;'>{config.PEER_ID}</b>")
        my_id_info.setObjectName("MyIDLabel")
        my_id_info.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        header_bar.addWidget(app_name)
        header_bar.addStretch()
        header_bar.addWidget(my_id_info)

        # Context Title: Shows who you are currently viewing
        self.chat_status_label = QLabel("Global Chat")
        self.chat_status_label.setObjectName("ChatStatus")

        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)

        # Input Area
        input_container = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type your message here...")
        self.input_box.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_button.clicked.connect(self.send_message)

        input_container.addWidget(self.input_box)
        input_container.addWidget(self.send_button)

        # Assemble Chat Section
        chat_layout.addLayout(header_bar)
        chat_layout.addWidget(self.chat_status_label)
        chat_layout.addWidget(self.chat_box)
        chat_layout.addLayout(input_container)

        # Assemble Splitter
        splitter.addWidget(sidebar_widget)
        splitter.addWidget(chat_container)
        splitter.setSizes([200, 700])
        layout.addWidget(splitter)

    def update_peer_list(self):
        """Refreshes the sidebar list from discovered peers."""
        from network.discover import peer_ids

        # Remember current selection
        current_item = self.peer_list_widget.currentItem()
        selected_name = current_item.text() if current_item else "Global Chat"

        self.peer_list_widget.clear()
        self.peer_list_widget.addItem("Global Chat")

        for pid in peer_ids.values():
            pid_str = str(pid)
            if pid_str != str(config.PEER_ID):
                self.peer_list_widget.addItem(pid_str)

        # Restore selection
        items = self.peer_list_widget.findItems(selected_name, Qt.MatchFlag.MatchExactly)
        if items:
            self.peer_list_widget.setCurrentItem(items[0])

    def switch_chat_context(self, item):
        """Changes the chat view to a specific peer or global."""
        self.current_chat_target = item.text()
        self.chat_status_label.setText(self.current_chat_target)

        # Load filtered history
        history = self.message_history.get(self.current_chat_target, "")
        self.chat_box.setHtml(history)
        self.scroll_to_bottom()

    def send_message(self):
        text = self.input_box.text().strip()
        if not text:
            return

        # Send via network
        recipient = None if self.current_chat_target == "Global Chat" else self.current_chat_target
        send_chat_message(text, recipient)

        # Display on UI
        formatted_msg = f"<div style='margin-bottom: 8px;'><b style='color: #f5c2e7;'>You:</b> {text}</div>"

        # Save to history for this specific target
        self.message_history[self.current_chat_target] = self.message_history.get(self.current_chat_target,
                                                                                  "") + formatted_msg

        self.chat_box.append(formatted_msg)
        self.input_box.clear()
        self.scroll_to_bottom()

    def handle_incoming_signal(self, full_message):
        """Processes incoming messages and sorts them into the correct history bucket."""
        is_private = "(Private)" in full_message

        # Simple extraction of sender from string "(Type) Sender: Message"
        try:
            sender = full_message.split(":", 1)[0].split(")")[-1].strip()
        except:
            sender = "Unknown"

        # Determine which history 'bucket' to save to
        bucket = sender if is_private else "Global Chat"

        formatted_line = f"<div style='margin-bottom: 8px;'>{full_message}</div>"

        if bucket not in self.message_history:
            self.message_history[bucket] = ""
        self.message_history[bucket] += formatted_line

        # Only append to screen if we are currently looking at that chat
        if self.current_chat_target == bucket:
            self.chat_box.append(formatted_line)
            self.scroll_to_bottom()

    def scroll_to_bottom(self):
        """Helper to ensure the latest messages are always visible."""
        scrollbar = self.chat_box.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())