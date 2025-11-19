import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QComboBox, QStackedLayout
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap, QImage, QIcon, QShortcut, QKeySequence

from .intersection_config import  IntersectionConfig

MAX_WIDTH, MAX_HEIGHT = 800, 600  # choose values that fit your screen




class VideoPlayer(QWidget):
    def __init__(self, config):
        super().__init__()

        self.config = config
        self.video_paths = config.video_paths   # list of video files
        self.icons = config.icons
        self.last_actions = getattr(config, "last_actions", {})

        # Layout
        main_layout = QVBoxLayout(self)
        self.video_selector = QComboBox()
        for path in self.video_paths:
            self.video_selector.addItem(path.split("/")[-1])
        main_layout.addWidget(self.video_selector)

        # Stacked layout for multiple players
        self.stack = QStackedLayout()
        self.players = []
        for path in self.video_paths:
            player = SingleVideoPlayer(
                video_path=path,
                icons=self.icons,
                last_action=self.last_actions.get(path)
            )
            self.players.append(player)
            self.stack.addWidget(player)
        main_layout.addLayout(self.stack)

        # Connect selector
        self.video_selector.currentIndexChanged.connect(self.switch_video)

        # to enable play/pause with space key
        self.space_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)

        # Track which one is visible
        self.current_index = 0
        # self.switch_video(0)
        self.stack.setCurrentIndex(self.current_index)
        self.space_shortcut.activated.connect(self.players[self.current_index].toggle_play)




    def switch_video(self, index):
        # Stop current player before switching
        current_player = self.players[self.current_index]
        current_player.playing = False
        current_player.timer.stop()
        self.space_shortcut.activated.disconnect(current_player.toggle_play)

        # Switch layout to new player
        self.stack.setCurrentIndex(index)
        self.current_index = index
        self.space_shortcut.activated.connect(self.players[index].toggle_play)


    def get_current_time_and_video(self):
        """Return current time (in seconds) of active video"""
        current_player = self.players[self.current_index]
        # return current_player.get_current_time()
        return current_player.get_current_time(), current_player.video_path




class SingleVideoPlayer(QWidget):
    # def __init__(self, config:IntersectionConfig):
    def __init__(self, video_path, icons, last_action=None):
        super().__init__()

        self.video_path = video_path
        # Video capture
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        self.current_frame_idx = 0
        self.playing = False
        self.playback_speed = 1.0
        self.fast_speed = 1.5
        self.slow_speed = 0.75
        self.rotation_angle = 0

        print(f'last action: {last_action}')
        if last_action: # not none
            self.start_frame = int(_restore_time(last_action)*self.fps)
            print(f'start frame: {self.start_frame}')
            self.current_frame_idx = self.start_frame

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
        # self.video_label.setFixedSize(self.width, self.height)
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
        self.slow_down_button = QPushButton(f'{self.slow_speed}X')
        self.speed_up_button = QPushButton(f'{self.fast_speed}X')  # this will be a hold/release button
        self.play_button.setIcon(QIcon(icons['playPause']))
        self.prev_button.setIcon(QIcon(icons['rewind']))
        self.next_button.setIcon(QIcon(icons['forward']))
        self.clear_button.setIcon(QIcon(icons['erase']))
        self.rotate_button.setIcon(QIcon(icons['rotate']))
        # self.slow_down_button.setIcon(QIcon(icons['speed']))
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.prev_button)
        control_layout.addWidget(self.next_button)
        control_layout.addWidget(self.clear_button)
        control_layout.addWidget(self.rotate_button)
        control_layout.addWidget(self.slow_down_button)
        control_layout.addWidget(self.speed_up_button)
        main_layout.addLayout(control_layout)
        # Connect signals
        self.play_button.clicked.connect(self.toggle_play)
        self.prev_button.clicked.connect(self.prev_frame)
        self.next_button.clicked.connect(self.next_frame)
        self.clear_button.clicked.connect(self.clear_overlay)
        self.rotate_button.clicked.connect(self.rotate_frame)
        self.slow_down_button.clicked.connect(self.change_playback_speed)
        self.speed_up_button.pressed.connect(self.start_fast_playback)
        self.speed_up_button.released.connect(self.restore_normal_speed)

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
        # self.prev_point = (event.position().x(), event.position().y())
        self.prev_point = self._map_to_frame(event.position())

    def draw(self, event):
        if self.drawing:
            x1, y1 = map(int, self.prev_point)
            # x2, y2 = int(event.position().x()), int(event.position().y())
            x2, y2 = self._map_to_frame(event.position())

            cv2.line(self.global_overlay, (x1, y1), (x2, y2), self.pen_color, self.pen_thickness)
            self.prev_point = (x2, y2)
            self.show_frame(self.current_frame_idx)

    def stop_draw(self, event):
        self.drawing = False

    def clear_overlay(self):
        self.global_overlay[:] = 0
        self.show_frame(self.current_frame_idx)

    # def _map_to_frame(self, pos):
    #     """Map QLabel coordinates to video frame coordinates."""
    #     label_w = self.video_label.width()
    #     label_h = self.video_label.height()
    #     frame_h, frame_w = self.global_overlay.shape[:2]
    #
    #     x_ratio = frame_w / label_w
    #     y_ratio = frame_h / label_h
    #     x = int(pos.x() * x_ratio)
    #     y = int(pos.y() * y_ratio)
    #
    #     if self.rotation_angle == 90:
    #         x, y = y, frame_w - x
    #     elif self.rotation_angle == 180:
    #         x, y = frame_w - x, frame_h - y
    #     elif self.rotation_angle == 270:
    #         x, y = frame_h - y, x
    #     return x, y

    def _map_to_frame(self, pos):
        """
        Map a mouse position (QPointF-like with .x()/.y()) inside the QLabel to
        coordinates in the original (unrotated) frame used by global_overlay.
        Handles:
          - QLabel pixmap centering / letterboxing
          - Pixmap scaling
          - Rotation that was applied for display (0/90/180/270)
        Returns: (x, y) integer coords in original frame coordinate space (cols, rows).
        """
        # safety
        if not hasattr(self, "_current_frame") or self._current_frame is None:
            return 0, 0

        label_rect = self.video_label.contentsRect()
        label_w, label_h = label_rect.width(), label_rect.height()

        pixmap = self.video_label.pixmap()
        if pixmap is None:
            # fallback: map linearly to original frame
            frame_h, frame_w = self.global_overlay.shape[:2]
            x = int(pos.x() * frame_w / max(1, label_w))
            y = int(pos.y() * frame_h / max(1, label_h))
            return max(0, min(frame_w - 1, x)), max(0, min(frame_h - 1, y))

        # displayed pixmap size (in widget coordinates)
        p_w = pixmap.width()
        p_h = pixmap.height()

        # calculate offsets (pixmap is centered in the label)
        offset_x = (label_w - p_w) / 2.0
        offset_y = (label_h - p_h) / 2.0

        # mouse pos relative to label's contentRect origin
        rel_x = pos.x() - label_rect.x()
        rel_y = pos.y() - label_rect.y()

        # pos relative to pixmap's top-left
        x_in_pixmap = rel_x - offset_x
        y_in_pixmap = rel_y - offset_y

        # clamp into pixmap area
        x_in_pixmap = max(0, min(p_w - 1, x_in_pixmap))
        y_in_pixmap = max(0, min(p_h - 1, y_in_pixmap))

        # Map to coordinates in the displayed (rotated) frame
        # Use the cached display frame size (the actual image used to create the pixmap)
        if not hasattr(self, "_display_frame") or self._display_frame is None:
            # safe fallback: treat displayed frame as same size as pixmap
            disp_h, disp_w = int(p_h), int(p_w)
        else:
            disp_h, disp_w = self._display_frame.shape[:2]

        # ratio from pixmap->display image (they may differ if QPixmap was scaled)
        x_disp = int(x_in_pixmap * (disp_w / p_w))
        y_disp = int(y_in_pixmap * (disp_h / p_h))

        # Now x_disp,y_disp are coordinates in the *rotated/display* frame.
        # We must map them back (inverse rotation) to the coordinates in the original frame.
        orig_h, orig_w = self._current_frame.shape[:2]  # original frame height/width

        if self.rotation_angle == 0:
            orig_x = x_disp
            orig_y = y_disp
        elif self.rotation_angle == 90:
            # displayed = original rotated 90 CCW
            # inverse mapping:
            # original_x = orig_w - 1 - rotated_y
            # original_y = rotated_x
            orig_x = orig_w - 1 - y_disp
            orig_y = x_disp
        elif self.rotation_angle == 180:
            # displayed = original rotated 180
            orig_x = orig_w - 1 - x_disp
            orig_y = orig_h - 1 - y_disp
        elif self.rotation_angle == 270:
            # displayed = original rotated 90 CW
            # inverse mapping:
            # original_x = rotated_y
            # original_y = orig_h - 1 - rotated_x
            orig_x = y_disp
            orig_y = orig_h - 1 - x_disp
        else:
            orig_x, orig_y = x_disp, y_disp

        # clamp into original frame bounds and return ints
        orig_x = int(max(0, min(orig_w - 1, orig_x)))
        orig_y = int(max(0, min(orig_h - 1, orig_y)))
        return orig_x, orig_y

    # --- Frame display ---
    def rotate_frame(self):
        self.rotation_angle += 90
        self.rotation_angle %= 360
        self.show_frame(self.current_frame_idx)

    def change_playback_speed(self):
        if self.playback_speed == 1.0:
            self.playback_speed = self.slow_speed
            self.slow_down_button.setStyleSheet("background-color: lightgray;")
        elif self.playback_speed == self.slow_speed:
            self.playback_speed = 1.0
            self.slow_down_button.setStyleSheet("")
        if self.playing:
            self.start_timer()

    def start_fast_playback(self):
        """When speedup button is pressed, temporarily speed up playback."""
        self.normal_speed = self.playback_speed  # save current normal speed
        self.playback_speed = self.fast_speed  # set fast speed
        self.speed_up_button.setStyleSheet("background-color: lightgray;")

        if self.playing:
            self.start_timer()  # restart timer with new speed

    def restore_normal_speed(self):
        """When speedup  button is released, restore original playback speed."""
        self.playback_speed = self.normal_speed
        self.speed_up_button.setStyleSheet("")
        if self.playing:
            self.start_timer()  # restart timer with normal speed

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

    # def show_frame(self, frame_idx):
    #     self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    #     ret, frame = self.cap.read()
    #     if ret:
    #         self.show_cv_frame(frame)
    #         self.slider.setValue(frame_idx)

    def show_frame(self, frame_idx):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = self.cap.read()
        if ret:
            self._current_frame = frame.copy()  # original, unrotated frame (H,W,3)
            self.show_cv_frame(frame)
            self.slider.setValue(frame_idx)

    # def show_cv_frame(self, frame):
    #     # Apply overlay
    #     frame = cv2.addWeighted(frame, 1.0, self.global_overlay, 1.0, 0)
    #     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #     # Apply rotation
    #     if self.rotation_angle == 90:
    #         frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    #     elif self.rotation_angle == 180:
    #         frame = cv2.rotate(frame, cv2.ROTATE_180)
    #     elif self.rotation_angle == 270:
    #         frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    #     else:
    #         pass  # 0 degree
    #
    #     # frame_rgb = cv2.cvtColor(frame_with_overlay, cv2.COLOR_BGR2RGB)
    #     h, w, ch = frame.shape
    #     bytes_per_line = ch * w
    #     qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
    #     pixmap = QPixmap.fromImage(qimg)
    #     # 🔹 Impose max display size
    #     if w > MAX_WIDTH or h > MAX_HEIGHT:
    #         pixmap = pixmap.scaled(
    #             MAX_WIDTH, MAX_HEIGHT,
    #             Qt.AspectRatioMode.KeepAspectRatio,
    #             Qt.TransformationMode.SmoothTransformation
    #         )
    #     self.video_label.setPixmap(pixmap)
    #     # self.video_label.setPixmap(QPixmap.fromImage(qimg))
    #     # Update timestamp
    #     current_time = self.format_time(self.current_frame_idx)
    #     total_time = self.format_time(self.total_frames)
    #     self.timestamp_label.setText(f"{current_time} / {total_time}")

    def show_cv_frame(self, frame):
        # Apply overlay BEFORE rotation so they align in the same original coord space
        frame_with_overlay = cv2.addWeighted(frame, 1.0, self.global_overlay, 1.0, 0)
        frame_rgb = cv2.cvtColor(frame_with_overlay, cv2.COLOR_BGR2RGB)

        # Apply rotation to the frame we will *display*
        if self.rotation_angle == 90:
            disp_frame = cv2.rotate(frame_rgb, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif self.rotation_angle == 180:
            disp_frame = cv2.rotate(frame_rgb, cv2.ROTATE_180)
        elif self.rotation_angle == 270:
            disp_frame = cv2.rotate(frame_rgb, cv2.ROTATE_90_CLOCKWISE)
        else:
            disp_frame = frame_rgb

        # Cache the rotated/display frame for coordinate mapping
        self._display_frame = disp_frame.copy()  # shape: (disp_h, disp_w, 3)

        # convert to QImage / QPixmap as before
        h, w, ch = disp_frame.shape
        bytes_per_line = ch * w
        qimg = QImage(disp_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        # impose max size (this returns a scaled pixmap if needed)
        if w > MAX_WIDTH or h > MAX_HEIGHT:
            pixmap = pixmap.scaled(
                MAX_WIDTH, MAX_HEIGHT,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

        self.video_label.setPixmap(pixmap)

        # update timestamp etc (unchanged)
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
        # return round(self.current_frame_idx / self.fps, 1)
        return self.current_frame_idx / self.fps



def _restore_time(formatted_time):
    minutes, seconds = formatted_time.split(':')
    return 60.0*int(minutes) + float(seconds)