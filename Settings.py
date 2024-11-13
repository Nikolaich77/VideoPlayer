from PyQt5.QtCore import QSettings
from pathlib import Path

class Settings:
    def __init__(self):
        self.settings = QSettings('VideoPlayer', 'Settings')
        
    def save_window_state(self, window):
        self.settings.setValue('geometry', window.saveGeometry())
        self.settings.setValue('windowState', window.saveState())
        self.settings.setValue('volume', window.volume_slider.value())
        self.settings.setValue('last_directory', window.last_directory)
        
    def load_window_state(self, window):
        if self.settings.value('geometry'):
            window.restoreGeometry(self.settings.value('geometry'))
            window.restoreState(self.settings.value('windowState'))
        window.volume_slider.setValue(self.settings.value('volume', 50))
        window.last_directory = self.settings.value('last_directory', str(Path.home()))