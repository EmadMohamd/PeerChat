from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel
)

from gui.signals import event_bus

from network.client import send_chat_message


class ChatWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("PeerChat")

        self.resize(600, 500)

        layout = QVBoxLayout()

        self.status_label = QLabel(
            "Connected to network"
        )

        self.chat_box = QTextEdit()

        self.chat_box.setReadOnly(True)

        self.input_box = QLineEdit()

        self.send_button = QPushButton("Send")

        layout.addWidget(self.status_label)
        layout.addWidget(self.chat_box)
        layout.addWidget(self.input_box)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

        self.send_button.clicked.connect(
            self.send_message
        )

        event_bus.message_received.connect(
            self.display_message
        )

    def send_message(self):

        message = self.input_box.text()

        if not message:
            return

        send_chat_message(message)

        self.chat_box.append(
            f"<b>You:</b> {message}"
        )

        self.input_box.clear()

    def display_message(self, message):

        self.chat_box.append(message)