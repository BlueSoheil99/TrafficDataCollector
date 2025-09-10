from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QHBoxLayout, QCheckBox, QDateEdit, QTimeEdit,
    QComboBox
)
from PyQt6.QtCore import QDate, QTime


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

        # --- Observation date ---
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        layout.addWidget(QLabel("Date of observation:"))
        layout.addWidget(self.date_input)

        # --- Video start time ---
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime(12, 0))
        layout.addWidget(QLabel("Video starting time:"))
        layout.addWidget(self.time_input)

        # Approaches
        layout.addWidget(QLabel("Select approaches:"))
        self.approaches = {}
        approaches_layout = QHBoxLayout()
        for name in ["NB", "SB", "WB", "EB"]:
            cb = QCheckBox(name)
            cb.setChecked(True)
            self.approaches[name] = cb
            approaches_layout.addWidget(cb)
        layout.addLayout(approaches_layout)

        # --- Dropdown menu ---
        layout.addWidget(QLabel("Select data collection type:"))
        self.collection_type = QComboBox()
        self.collection_type.addItems(["Volume only", "speed only", "Volume and Speed", 'Near miss'])
        layout.addWidget(self.collection_type)

        # OK/Cancel
        buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)


    def select_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Video")
        if path:
            self.video_path = path
            self.video_btn.setText(path.split("/")[-1])

    def get_config(self):
        """Return dict with selected approaches, date, and start time."""
        selected_approaches = [name for name, cb in self.approaches.items() if cb.isChecked()]
        t = self.get_start_time()
        return {
            "video_path": self.video_path,
            "collection_type": self.collection_type.currentText(),
            "approaches": selected_approaches,
            "date": self.get_date(),
            "start_time": t[0],
            "start_time_seconds": t[1]
        }


    def get_date(self):
        """Return selected date as YYYY-MM-DD string"""
        return self.date_input.date().toString("yyyy-MM-dd")

    def get_start_time(self):
        """Return starting time in seconds"""
        t = self.time_input.time()
        ts = t.hour() * 3600 + t.minute() * 60 + t.second()
        return [f'{t.hour():02}:{t.minute():02}:{t.second():02}',ts]

