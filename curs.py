import sys
import os
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import (QMessageBox, QLabel, 
                           QSlider, QAction, QFileDialog,
                           QVBoxLayout, QHBoxLayout, QDockWidget, QHBoxLayout, QListWidget, QPushButton, QWidget)
from PyQt5.QtCore import Qt, QTimer
from pathlib import Path
import logging
from MediaController import MediaController
from Settings import Settings
from HistoryManager import HistoryManager
from PlaylistManager import PlaylistManager

# Configure logging
logging.basicConfig(
    filename='video_player.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class VideoPlayer(QtWidgets.QMainWindow):
    def __init__(self):
        super(VideoPlayer, self).__init__()
        self.setWindowTitle("Відеоплеєр Pro")
        self.setGeometry(100, 100, 1200, 700)
        
        # Initialize managers and settings
        self.settings_manager = Settings()
        self.history_manager = HistoryManager()
        self.playlist_manager = PlaylistManager()
        self.last_directory = str(Path.home())

        # Створення бокової панелі
        self.create_side_panel()
        self.setup_ui()
        self.setup_shortcuts()
        self.setup_menu()
        
        # Load saved settings
        self.settings_manager.load_window_state(self)

        # Завантажуємо історію та улюблені файли в інтерфейс
        self.update_lists()  # Оновлюємо інтерфейс для історії та улюблених
        
        # Initialize media controller and state
        self.media_controller = MediaController(self.video_frame)
        self.playlist = []
        self.current_index = -1
        
    def create_side_panel(self):
        """Створення бічної панелі для відображення історії та улюблених файлів."""
        if not hasattr(self, 'dock_widget'):  # Перевірка чи вже є dock_widget
            self.dock_widget = QDockWidget("Side Panel", self)  # Створюємо тільки якщо ще не існує
            self.dock_widget.setObjectName("SidePanel")  # Встановлюємо objectName
            self.dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

            side_panel_widget = QWidget()
            side_panel_layout = QVBoxLayout()

            # Список для улюблених
            self.favorites_list = QListWidget()
            side_panel_layout.addWidget(self.favorites_list)

            # Кнопка для додавання в улюблене
            add_favorite_button = QPushButton("Add to Favorites")
            add_favorite_button.clicked.connect(self.add_to_favorites)
            side_panel_layout.addWidget(add_favorite_button)

            # Кнопка для видалення з улюбленого
            remove_favorite_button = QPushButton("Remove from Favorites")
            remove_favorite_button.clicked.connect(self.remove_from_favorites)
            side_panel_layout.addWidget(remove_favorite_button)

            # Список для історії
            self.history_list = QListWidget()
            side_panel_layout.addWidget(self.history_list)

            side_panel_widget.setLayout(side_panel_layout)
            self.dock_widget.setWidget(side_panel_widget)
            self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)

    def add_to_history(self, filename, time_code):
        """Додає файл до історії вручну (як приклад)."""
        # Перевірка, чи є вже файл в історії
        if not any(item['filename'] == filename for item in self.history_manager.history):
            self.history_manager.add_to_history(filename, time_code)
            self.update_lists()

    def add_to_favorites(self):
        """Додає файл в улюблені вручну (як приклад)."""
        current_file = self.current_file  # або отримати назву файлу з іншого місця
        if current_file:  # Перевірка, чи файл є
            self.history_manager.add_to_favorites(current_file)
            self.update_lists()

    def remove_from_favorites(self):
        """Видаляє файл з улюблених вручну (як приклад)."""
        # Отримуємо вибраний елемент зі списку
        selected_item = self.favorites_list.currentItem()
        if selected_item:
            filename = selected_item.text()  # Отримуємо назву файлу з тексту елемента списку
            self.history_manager.remove_from_favorites(filename)  # Видаляємо з улюблених
            self.update_lists()  # Оновлюємо список на інтерфейсі

    def update_lists(self):
        """Оновлює списки на боковій панелі для історії та улюблених."""
        # Оновлюємо список історії
        self.history_list.clear()
        for item in self.history_manager.history:
            self.history_list.addItem(f"{item['filename']} - {item['time_code']}")

        # Оновлюємо список улюблених
        self.favorites_list.clear()
        for item in self.history_manager.favorites:
            self.favorites_list.addItem(item)  # Переконатися, що це рядок

    def play_file(self, filename, time_code):
        """При відтворенні файлу додаємо його в історію."""
        # Перевірка, чи вже є файл у історії
        if not any(item['filename'] == filename for item in self.history_manager.history):
            self.history_manager.add_to_history(filename, time_code)
            self.update_lists()
        print(f"Playing {filename} at {time_code}")

    def setup_timer(self):
        # Update the video time and slider every 500ms
        self.update_timer.timeout.connect(self.update_time)
        self.update_timer.start(500)

    def connect_signals(self):
        # Connect buttons and sliders to their respective functions
        self.play_button.clicked.connect(self.toggle_play_pause)
        self.pause_button.clicked.connect(self.pause_video)
        self.stop_button.clicked.connect(self.stop_video)
        self.time_slider.valueChanged.connect(self.seek_video)
        self.volume_slider.valueChanged.connect(self.adjust_volume)

    def update_time(self):
        """Update the time slider and label based on the current video position."""
        if self.media_controller.is_playing():
            current_time = self.media_controller.get_time() / 1000  # Convert ms to seconds
            total_time = self.media_controller.get_length() / 1000  # Convert ms to seconds

            self.time_slider.setValue(int((current_time / total_time) * 1000))
            minutes, seconds = divmod(int(current_time), 60)
            total_minutes, total_seconds = divmod(int(total_time), 60)

            self.time_label.setText(f"{minutes:02}:{seconds:02} / {total_minutes:02}:{total_seconds:02}")

    def toggle_play_pause(self):
        """Toggle between play and pause states."""
        if self.media_controller.is_playing():
            self.media_controller.pause()
        else:
            self.media_controller.play()

    def pause_video(self):
        """Pause the video."""
        self.media_controller.pause()

    def stop_video(self):
        """Stop the video and reset the position."""
        self.media_controller.stop()
        self.time_slider.setValue(0)
        self.time_label.setText("00:00 / 00:00")

    def seek_video(self):
        """Seek the video to the selected position."""
        position = self.time_slider.value() / 1000  # Convert to seconds
        self.media_controller.set_position(position)

    def adjust_volume(self):
        """Adjust the volume based on the volume slider."""
        volume = self.volume_slider.value()
        self.media_controller.set_volume(volume)

    def set_playback_speed(self, speed):
        """Set the playback speed for the video."""
        self.media_controller.set_playback_rate(speed)

    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        self.media_controller.toggle_fullscreen()

    def open_file(self):
        """Open a file dialog to select a video file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", self.last_directory, "Videos (*.mp4 *.avi *.mkv *.mov)")
        if file_path:
            self.last_directory = os.path.dirname(file_path)
            self.load_video(file_path)

    def open_folder(self):
        """Open a folder dialog to select a folder."""
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder", self.last_directory)
        if folder_path:
            self.last_directory = folder_path
            print(f"Selected folder: {folder_path}")

    def add_to_recent_files(self, file_path):
        """Додає файл до списку нещодавно відкритих файлів."""
        if file_path not in self.history_manager.history:
            time_code = self.media_controller.get_time()  # Отримуємо поточний час відео в мілісекундах
            time_code = self.format_time(time_code)  # Перетворюємо мілісекунди в формат hh:mm:ss
            self.history_manager.add_to_history(file_path, time_code)  # Зберігає файл з базовими значеннями

    def save_recent_files(self):
        """Зберігає список нещодавно відкритих файлів."""
        self.history_manager.save_history()  # Використовує менеджер історії для збереження даних

    def load_video(self, file_path):
        """Load a video and play it."""
        if self.media_controller.set_media(file_path):
            self.media_controller.play()
            time_code = self.media_controller.get_time()  # Отримуємо поточний час відео в мілісекундах
            time_code = self.format_time(time_code)  # Перетворюємо мілісекунди в формат hh:mm:ss
            self.history_manager.add_to_history(file_path, time_code)
            self.update_lists()  # Оновлюємо інтерфейс з новим відео

    def load_recent_files(self):
        """Load recently opened files from history."""
        for entry in self.history_manager.history:
            print(f"Recently opened: {entry['path']}")

    def closeEvent(self, event):
        """Handle application closing event."""
        self.settings_manager.save_window_state(self)
        event.accept()

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.toggle_fullscreen()
        super(VideoPlayer, self).keyPressEvent(event)

    def setup_ui(self):
        # Main widget and layout
        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        
        # Video frame
        self.video_frame = QtWidgets.QFrame()
        self.video_frame.setStyleSheet("background-color: black;")
        self.video_frame.setMinimumSize(800, 450)
        
        # Controls layout
        self.controls_layout = QHBoxLayout()
        
        # Create and setup controls
        self.setup_controls()
        
        # Add widgets to main layout
        self.main_layout.addWidget(self.video_frame)
        self.main_layout.addLayout(self.controls_layout)
        
        self.setCentralWidget(self.main_widget)



    def setup_controls(self):
        # Playback controls
        self.play_button = QtWidgets.QPushButton(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay), "")
        self.pause_button = QtWidgets.QPushButton(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPause), "")
        self.stop_button = QtWidgets.QPushButton(self.style().standardIcon(QtWidgets.QStyle.SP_MediaStop), "")

        self.play_button.clicked.connect(self.toggle_play_pause)  # Прив'язка кнопки Play до відповідного методу
        self.pause_button.clicked.connect(self.pause_video)
        self.stop_button.clicked.connect(self.stop_video)
        
        # Time slider
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(0, 1000)
        self.time_slider.sliderMoved.connect(self.seek_video)
        
        # Volume control
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.sliderMoved.connect(self.adjust_volume)
        
        # Time label
        self.time_label = QLabel("00:00 / 00:00")
        # Timer for updating time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second
        
        # Add controls to layout
        self.controls_layout.addWidget(self.play_button)
        self.controls_layout.addWidget(self.pause_button)
        self.controls_layout.addWidget(self.stop_button)
        self.controls_layout.addWidget(self.time_slider)
        self.controls_layout.addWidget(self.time_label)
        self.controls_layout.addWidget(self.volume_slider)

    def setup_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        
        open_folder_action = QAction('Open Folder', self)
        open_folder_action.setShortcut('Ctrl+D')
        open_folder_action.triggered.connect(self.open_folder)
        
        file_menu.addAction(open_action)
        file_menu.addAction(open_folder_action)
        
        # Playback menu
        playback_menu = menubar.addMenu('Playback')
        
        speed_menu = playback_menu.addMenu('Speed')
        speeds = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
        for speed in speeds:
            action = QAction(f'{speed}x', self)
            action.triggered.connect(lambda checked, s=speed: self.set_playback_speed(s))
            speed_menu.addAction(action)
            
        # View menu
        view_menu = menubar.addMenu('View')
        
        fullscreen_action = QAction('Fullscreen', self)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        
        view_menu.addAction(fullscreen_action)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for various actions."""
        # Shortcut for adding to favorites (Ctrl+Shift+F)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Shift+F"), self, self.add_to_favorites)

        # Shortcut for removing from favorites (Ctrl+Shift+R)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Shift+R"), self, self.remove_from_favorites)

        # Shortcut for opening/closing the side panel (Ctrl+P)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+P"), self, self.toggle_side_panel)

        # Playback shortcuts
        QtWidgets.QShortcut(QtGui.QKeySequence("Space"), self, self.toggle_play_pause)
        QtWidgets.QShortcut(QtGui.QKeySequence("Left"), self, self.seek_backward)
        QtWidgets.QShortcut(QtGui.QKeySequence("Right"), self, self.seek_forward)
        QtWidgets.QShortcut(QtGui.QKeySequence("Up"), self, self.volume_up)
        QtWidgets.QShortcut(QtGui.QKeySequence("Down"), self, self.volume_down)

    def toggle_side_panel(self):
            """Toggle the visibility of the side panel."""
            if hasattr(self, 'dock_widget'):
                if self.dock_widget.isVisible():
                    self.dock_widget.hide()
                else:
                    self.dock_widget.show()

    def setup_timer(self):
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(1000)

    def connect_signals(self):
        self.play_button.clicked.connect(lambda: self.control_video("play"))
        self.pause_button.clicked.connect(lambda: self.control_video("pause"))
        self.stop_button.clicked.connect(lambda: self.control_video("stop"))
        self.time_slider.sliderMoved.connect(self.seek)
        self.volume_slider.valueChanged.connect(self.set_volume)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video",
            self.last_directory,
            "Video Files (*.mp4 *.avi *.mkv *.mov);;All Files (*.*)"
        )
        
        if file_path:
            self.last_directory = os.path.dirname(file_path)
            self.load_file(file_path)

    def load_file(self, file_path):
        try:
            self.media_controller.set_media(file_path)
            self.setWindowTitle(f"Відеоплеєр Pro - {os.path.basename(file_path)}")
            self.current_file = file_path
            self.control_video("play")
            self.add_to_recent_files(file_path)
        except Exception as e:
            logging.error(f"Error loading file: {str(e)}")
            QMessageBox.critical(self, "Error", f"Could not load video file: {str(e)}")

    def control_video(self, action):
        try:
            if action == "play":
                self.media_controller.play()
                self.play_button.setEnabled(True)
                self.pause_button.setEnabled(True)
            elif action == "pause":
                self.media_controller.pause()
                self.play_button.setEnabled(True)
                self.pause_button.setEnabled(True)
            elif action == "stop":
                self.media_controller.stop()
                self.play_button.setEnabled(True)
                self.pause_button.setEnabled(True)
                
            self.add_to_history()
        except Exception as e:
            logging.error(f"Error controlling video: {str(e)}")

    def update_ui(self):
        if hasattr(self, 'media_controller'):
            try:
                # Update time
                current_time = self.media_controller.player.get_time()
                total_time = self.media_controller.player.get_length()
                
                if total_time > 0:
                    # Update slider
                    self.time_slider.setValue(int(1000 * current_time / total_time))
                    
                    # Update time label
                    current_str = self.format_time(current_time)
                    total_str = self.format_time(total_time)
                    self.time_label.setText(f"{current_str} / {total_str}")
            except Exception as e:
                logging.error(f"Error updating UI: {str(e)}")

    def format_time(self, ms):
        s = ms // 1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"

    def closeEvent(self, event):
        try:
            self.settings_manager.save_window_state(self)
            self.save_recent_files()
            event.accept()
        except Exception as e:
            logging.error(f"Error during close: {str(e)}")
            event.accept()

    # Additional utility methods
    def toggle_play_pause(self):
        if self.media_controller.is_playing():
            self.media_controller.pause()

        else:
            self.media_controller.play()


    def seek_forward(self):
        current_time = self.media_controller.player.get_time()
        self.media_controller.player.set_time(current_time + 10000)  # +10 seconds

    def seek_backward(self):
        current_time = self.media_controller.player.get_time()
        self.media_controller.player.set_time(max(0, current_time - 10000))  # -10 seconds

    def volume_up(self):
        current_volume = self.volume_slider.value()
        self.volume_slider.setValue(min(100, current_volume + 5))

    def volume_down(self):
        current_volume = self.volume_slider.value()
        self.volume_slider.setValue(max(0, current_volume - 5))

    def set_playback_speed(self, speed):
        try:
            self.media_controller.player.set_rate(speed)
        except Exception as e:
            logging.error(f"Error setting playback speed: {str(e)}")

if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle('Fusion')  # Consistent style across platforms
        
        # Set application-wide stylesheet
        app.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2e2e2e;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3a3a3a;
                border: none;
                padding: 5px;
                min-width: 30px;
                border-radius: 5px;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #575757;
            }
            QSlider {
                background-color: #444444;
                height: 6px;
            }
            QSlider::handle:horizontal {
                background-color: #3a3a3a;
                border-radius: 5px;
                width: 15px;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
        """)
        
        # Create the main window
        main_window = VideoPlayer()
        main_window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"Error starting application: {str(e)}")