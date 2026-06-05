import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QFrame, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer


class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PeerChat — Configuration")
        self.resize(640, 680)
        self.setMinimumSize(560, 600)
        self.setMaximumSize(780, 800)

        self.username = None
        self.port = None

        self.init_ui()
        QTimer.singleShot(50, self.animate_in)

    def init_ui(self):
        self.setStyleSheet("""
            /* ── BASE ─────────────────────────────────────────────── */
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            }

            /* ── CARD ─────────────────────────────────────────────── */
            QFrame#MainCard {
                background-color: #181825;
                border: 1px solid #2a2a3d;
                border-radius: 22px;
            }

            /* ── BADGE ────────────────────────────────────────────── */
            QLabel#Badge {
                background-color: #1e3a5f;
                color: #89b4fa;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1.5px;
                border-radius: 10px;
                padding: 4px 12px;
            }

            /* ── TYPOGRAPHY ───────────────────────────────────────── */
            QLabel#MainTitle {
                font-size: 36px;
                font-weight: 800;
                color: #cdd6f4;
                letter-spacing: -0.5px;
            }
            QLabel#Subtitle {
                color: #7f849c;
                font-size: 14px;
                font-weight: 400;
                line-height: 1.6;
            }
            QLabel#FieldLabel {
                color: #a6adc8;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 0.6px;
            }

            /* ── INPUTS ───────────────────────────────────────────── */
            QLineEdit {
                background-color: #11111b;
                border-radius: 14px;
                padding: 14px 18px;
                border: 1.5px solid #2a2a3d;
                font-size: 14px;
                color: #cdd6f4;
                font-weight: 400;
                selection-background-color: #313244;
            }
            QLineEdit:focus {
                border: 1.5px solid #89b4fa;
                background-color: #13131f;
            }
            QLineEdit::placeholder {
                color: #45475a;
                font-weight: 400;
            }

            /* ── DIVIDER ──────────────────────────────────────────── */
            QFrame#Divider {
                background-color: #2a2a3d;
                max-height: 1px;
            }

            /* ── BUTTON ───────────────────────────────────────────── */
            QPushButton#LaunchButton {
                background-color: #89b4fa;
                color: #11111b;
                border-radius: 14px;
                font-weight: 800;
                font-size: 14px;
                letter-spacing: 0.3px;
                border: none;
            }
            QPushButton#LaunchButton:hover {
                background-color: #a6c8ff;
            }
            QPushButton#LaunchButton:pressed {
                background-color: #74a8f8;
            }

            /* ── ERROR ────────────────────────────────────────────── */
            QLabel#ErrorLabel {
                color: #f38ba8;
                font-size: 12px;
                font-weight: 600;
            }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 28, 28, 28)

        # ── Card ───────────────────────────────────────────────────
        card = QFrame()
        card.setObjectName("MainCard")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(52, 48, 52, 48)
        cl.setSpacing(0)

        # ── Badge ──────────────────────────────────────────────────
        badge_row = QHBoxLayout()
        badge = QLabel("P2P NODE")
        badge.setObjectName("Badge")
        badge.setFixedHeight(24)
        badge_row.addWidget(badge)
        badge_row.addStretch()
        cl.addLayout(badge_row)
        cl.addSpacing(28)

        # ── Title ──────────────────────────────────────────────────
        title = QLabel("PeerChat")
        title.setObjectName("MainTitle")

        subtitle = QLabel(
            "Configure your network identity and listening port"
        )
        subtitle.setObjectName("Subtitle")
        subtitle.setWordWrap(True)

        cl.addWidget(title)
        cl.addSpacing(10)
        cl.addWidget(subtitle)
        cl.addSpacing(36)

        # ── Divider ────────────────────────────────────────────────
        divider = QFrame()
        divider.setObjectName("Divider")
        divider.setFrameShape(QFrame.Shape.HLine)
        cl.addWidget(divider)
        cl.addSpacing(36)

        # ── Username field ─────────────────────────────────────────
        user_label = QLabel("USERNAME")
        user_label.setObjectName("FieldLabel")
        self.username_input = QLineEdit()
        self.username_input.setMinimumHeight(52)
        self.username_input.setPlaceholderText("e.g. alice_node")

        cl.addWidget(user_label)
        cl.addSpacing(8)
        cl.addWidget(self.username_input)
        cl.addSpacing(24)

        # ── Port field ─────────────────────────────────────────────
        port_label = QLabel("LISTENING PORT")
        port_label.setObjectName("FieldLabel")
        self.port_input = QLineEdit()
        self.port_input.setMinimumHeight(52)
        self.port_input.setPlaceholderText("1024 – 65535")

        cl.addWidget(port_label)
        cl.addSpacing(8)
        cl.addWidget(self.port_input)
        cl.addSpacing(20)

        # ── Error ──────────────────────────────────────────────────
        self.error_label = QLabel("")
        self.error_label.setObjectName("ErrorLabel")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setMinimumHeight(22)
        cl.addWidget(self.error_label)
        cl.addSpacing(24)

        # ── Launch button ──────────────────────────────────────────
        self.launch_btn = QPushButton("Launch Session →")
        self.launch_btn.setObjectName("LaunchButton")
        self.launch_btn.setMinimumHeight(54)
        self.launch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.launch_btn.clicked.connect(self.validate_and_submit)
        cl.addWidget(self.launch_btn)

        outer.addWidget(card)

    # ── Fade-in ────────────────────────────────────────────────────
    def animate_in(self):
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)
        self._anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self._anim.setDuration(300)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.start()

    # ── Shake on error ─────────────────────────────────────────────
    def shake_error(self):
        original_x = self.x()
        offsets = [6, -6, 4, -4, 2, -2, 0]
        delay = 0
        for offset in offsets:
            QTimer.singleShot(delay, lambda o=offset: self.move(original_x + o, self.y()))
            delay += 40

    # ── Validation ─────────────────────────────────────────────────
    def validate_and_submit(self):
        user_text = self.username_input.text().strip()
        port_text = self.port_input.text().strip()

        if not user_text:
            self.error_label.setText("⚠  Username cannot be empty.")
            self.username_input.setFocus()
            self.shake_error()
            return

        if not port_text:
            self.error_label.setText("⚠  Listening port is required.")
            self.port_input.setFocus()
            self.shake_error()
            return

        try:
            port_num = int(port_text)
            if not (1024 <= port_num <= 65535):
                raise ValueError()
        except ValueError:
            self.error_label.setText("⚠  Port must be an integer between 1024 – 65535.")
            self.port_input.setFocus()
            self.shake_error()
            return

        self.error_label.setText("")
        self.username = user_text
        self.port = port_num
        self.close()