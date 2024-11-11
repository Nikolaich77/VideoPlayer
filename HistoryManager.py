import os
import json
import logging
from datetime import datetime

class HistoryManager:
    def __init__(self, filename="history.json"):
        self.filename = filename
        self.history = self.load_history()

    def load_history(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, "r", encoding='utf-8') as file:
                    return json.load(file)
            return []
        except Exception as e:
            logging.error(f"Error loading history: {str(e)}")
            return []

    def save_history(self):
        try:
            with open(self.filename, "w", encoding='utf-8') as file:
                json.dump(self.history, file, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"Error saving history: {str(e)}")

    def add_to_history(self, video_path, timestamp, duration, volume):
        try:
            entry = {
                "path": video_path,
                "timestamp": timestamp,
                "duration": duration,
                "volume": volume,
                "date_added": datetime.now().isoformat()
            }
            self.history.append(entry)
            self.save_history()
        except Exception as e:
            logging.error(f"Error adding to history: {str(e)}")

    def clear_history(self):
        self.history = []
        self.save_history()