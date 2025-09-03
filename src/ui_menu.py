from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QFileDialog,
    QSpinBox, QLabel, QDialogButtonBox
)
from .intersection_config import IntersectionConfig


class SetupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Setup Intersection")

        layout = QVBoxLayout(self)

        self.video_path = ""

        # Select video button
        self.video_btn = QPushButton("Select Video")
        self.video_btn.clicked.connect(self.select_video)
        layout.addWidget(self.video_btn)

        # Example: ask for number of approaches
        layout.addWidget(QLabel("Number of approaches:"))
        self.approaches_spin = QSpinBox()
        self.approaches_spin.setRange(1, 8)
        self.approaches_spin.setValue(4)
        layout.addWidget(self.approaches_spin)

        # OK/Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def select_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Video")
        if path:
            self.video_path = path

    def get_config(self):
        return IntersectionConfig(self.approaches_spin.value())

    def get_video_path(self):
        return self.video_path
