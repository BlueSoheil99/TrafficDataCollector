import json
import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout

from src.ui_menu import SetupDialog, CacheDialog
from src.video_player import VideoPlayer
from src.counter_panel import CounterPanel
from src.intersection_config import IntersectionConfig


class MainWindow(QMainWindow):
    def __init__(self, config:IntersectionConfig):
        super().__init__()
        self.setWindowTitle("Traffic Counter")
        # Central widget layout
        central = QWidget()
        layout = QHBoxLayout(central)
        self.setCentralWidget(central)
        # Video player on the left
        self.video_player = VideoPlayer(config)
        layout.addWidget(self.video_player)
        # Counter panel on the right
        self.counter_panel = CounterPanel(config,
                                          get_current_time_callback=self.video_player.get_current_time)
        layout.addWidget(self.counter_panel)


def cache_exists(cache_path="data/cache.json"):
    try:
        with open(cache_path, "r") as f:
            data = json.load(f)
        os.remove(cache_path)
        print("-- Loading Cache: loaded and deleted")
        return data
    except FileNotFoundError:
        print("-- Loading Cache: not found")
        return None


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('data/icons/traffic.png'))
    #If there is cache, see if user wants to reload. If user declines or there's no cache, run new project
    cache = cache_exists()
    cache_reader = CacheDialog()
    if cache and cache_reader.exec() == cache_reader.DialogCode.Accepted:
            run(app, cache)
    else:
        # Run setup dialog
        dialog = SetupDialog()
        if dialog.exec() == dialog.DialogCode.Accepted:
            run(app, dialog.get_config())
        else:
            sys.exit()

def run(app, config:dict):
    config = IntersectionConfig(config)
    window = MainWindow(config)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
