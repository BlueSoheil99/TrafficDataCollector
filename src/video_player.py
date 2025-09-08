import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSlider
)
from PyQt6.QtCore import QTimer, Qt, QPoint
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QIcon
from sipbuild.generator.parser.rules import start


class VideoPlayer(QWidget):
    def __init__(self, video_path):
        super().__init__()

        # Video capture
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        self.current_frame_idx = 0
        self.playing = False
        self.playback_speed = 1.0
        self.rotation_angle = 0

        # Overlay for drawing
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Video empty")
        self.height, self.width = frame.shape[:2]
        self.global_overlay = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.drawing = False
        self.pen_color = (0, 0, 255)
        self.pen_thickness = 2

        # Layout
        main_layout = QVBoxLayout(self)
        self.video_label = QLabel()
        self.video_label.setFixedSize(self.width, self.height)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.video_label)

        # Timestamp
        self.timestamp_label = QLabel("00:00.000 / 00:00.000")
        main_layout.addWidget(self.timestamp_label)

        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.total_frames - 1)
        self.slider.valueChanged.connect(self.slider_changed)
        main_layout.addWidget(self.slider)

        # Controls
        control_layout = QHBoxLayout()
        self.play_button = QPushButton()
        self.prev_button = QPushButton()
        self.next_button = QPushButton()
        self.clear_button = QPushButton()
        self.rotate_button = QPushButton()
        self.speed_button = QPushButton()
        self.play_button.setIcon(QIcon('data/icons/playPause.png'))
        self.prev_button.setIcon(QIcon('data/icons/rewind.png'))
        self.next_button.setIcon(QIcon('data/icons/forward.png'))
        self.clear_button.setIcon(QIcon('data/icons/eraser.png'))
        self.rotate_button.setIcon(QIcon('data/icons/rotate.png'))
        self.speed_button.setIcon(QIcon('data/icons/speed.png'))
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.prev_button)
        control_layout.addWidget(self.next_button)
        control_layout.addWidget(self.clear_button)
        control_layout.addWidget(self.rotate_button)
        control_layout.addWidget(self.speed_button)
        main_layout.addLayout(control_layout)
        # Connect signals
        self.play_button.clicked.connect(self.toggle_play)
        self.prev_button.clicked.connect(self.prev_frame)
        self.next_button.clicked.connect(self.next_frame)
        self.clear_button.clicked.connect(self.clear_overlay)
        self.rotate_button.clicked.connect(self.rotate_frame)
        self.speed_button.clicked.connect(self.change_playback_speed)

        # Timer for playback
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Mouse events for drawing
        self.video_label.mousePressEvent = self.start_draw
        self.video_label.mouseMoveEvent = self.draw
        self.video_label.mouseReleaseEvent = self.stop_draw

        # Show first frame
        self.show_frame(self.current_frame_idx)

    # --- Playback functions ---
    def toggle_play(self):
        self.playing = not self.playing
        if self.playing:
            self.start_timer()
        else:
            self.timer.stop()

    def start_timer(self):
        delay = int((1000 / self.fps) / self.playback_speed)
        self.timer.start(delay)

    def prev_frame(self):
        self.playing = False
        self.timer.stop()
        self.current_frame_idx = max(0, self.current_frame_idx - 1)
        self.show_frame(self.current_frame_idx)

    def next_frame(self):
        self.playing = False
        self.timer.stop()
        self.current_frame_idx = min(self.total_frames - 1, self.current_frame_idx + 1)
        self.show_frame(self.current_frame_idx)

    def slider_changed(self, value):
        self.playing = False
        self.timer.stop()
        self.current_frame_idx = value
        self.show_frame(self.current_frame_idx)

    # --- Overlay drawing ---
    def start_draw(self, event):
        self.drawing = True
        self.prev_point = (event.position().x(), event.position().y())

    def draw(self, event):
        if self.drawing:
            x1, y1 = map(int, self.prev_point)
            x2, y2 = int(event.position().x()), int(event.position().y())
            cv2.line(self.global_overlay, (x1, y1), (x2, y2), self.pen_color, self.pen_thickness)
            self.prev_point = (x2, y2)
            self.show_frame(self.current_frame_idx)

    def stop_draw(self, event):
        self.drawing = False

    def clear_overlay(self):
        self.global_overlay[:] = 0
        self.show_frame(self.current_frame_idx)

    # --- Frame display ---
    def rotate_frame(self):
        self.rotation_angle += 90
        self.rotation_angle %= 360
        self.show_frame(self.current_frame_idx)

    def change_playback_speed(self):
        if self.playback_speed == 1.0:
            self.playback_speed = 0.75
            self.speed_button.setStyleSheet("background-color: lightgray;")
        elif self.playback_speed == 0.75:
            self.playback_speed = 1.0
            self.speed_button.setStyleSheet("")
        if self.playing:
            self.start_timer()


    def update_frame(self):
        if not self.playing:
            return

        if self.current_frame_idx >= self.total_frames:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.current_frame_idx = 0

        ret, frame = self.cap.read()
        if ret:
            self.show_cv_frame(frame)
            self.current_frame_idx += 1
            # Update slider programmatically without triggering slider_changed
            self.slider.blockSignals(True)
            self.slider.setValue(self.current_frame_idx)
            self.slider.blockSignals(False)
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.current_frame_idx = 0

    def show_frame(self, frame_idx):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = self.cap.read()
        if ret:
            self.show_cv_frame(frame)
            self.slider.setValue(frame_idx)

    def show_cv_frame(self, frame):
        # Apply overlay
        frame = cv2.addWeighted(frame, 1.0, self.global_overlay, 1.0, 0)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Apply rotation
        if self.rotation_angle == 90:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif self.rotation_angle == 180:
            frame = cv2.rotate(frame, cv2.ROTATE_180)
        elif self.rotation_angle == 270:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        else:
            pass  # 0 degree

        # frame_rgb = cv2.cvtColor(frame_with_overlay, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qimg))

        # Update timestamp
        current_time = self.format_time(self.current_frame_idx)
        total_time = self.format_time(self.total_frames)
        self.timestamp_label.setText(f"{current_time} / {total_time}")

    def format_time(self, frame_idx):
        seconds_total = frame_idx / self.fps
        minutes = int(seconds_total // 60)
        seconds = int(seconds_total % 60)
        milliseconds = int((seconds_total - int(seconds_total)) * 1000)
        return f"{minutes:02}:{seconds:02}.{milliseconds:03}"

    def get_current_time(self):
        """Return current video time in seconds"""
        return self.current_frame_idx / self.fps

