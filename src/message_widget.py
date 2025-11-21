from PyQt6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout,  QSizePolicy
)


class MessageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.last_action_label = QLabel("Last Action:")
        self.message_label = QLabel()
        style_message_section(self.layout, self.last_action_label, self.message_label)

    def update_message_box(self, text):
        if text:  # not None
            self.message_label.setText(text)


def style_message_section(msg_layout, last_action_label, message_label):
    msg_layout.setSpacing(5)  # small gap between label and message
    msg_layout.setContentsMargins(0, 0, 0, 0)  # remove extra padding around layout

    # Left-side label
    last_action_label.setStyleSheet("""
            QLabel {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: normal;
                color: #2C3E50;   /* subtle dark color */
            }
        """)
    msg_layout.addWidget(last_action_label)

    # Message label
    message_label.setStyleSheet("""
            QLabel {
                font-family: 'Courier New', Courier, monospace;
                font-weight: normal;
                color: #555555;
                background-color: #F7F7F7;
                border-radius: 3px;
                padding: 2px 6px;
            }
        """)
    # Let the message stretch to fill remaining horizontal space
    message_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    msg_layout.addWidget(message_label)
