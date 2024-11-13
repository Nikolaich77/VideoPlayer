import os
import json
import logging
from datetime import datetime

class HistoryManager:
    def __init__(self, history_filename="history.json", favorites_filename="favorites.json"):
        self.history_filename = history_filename
        self.favorites_filename = favorites_filename
        self.history = self.load_data(self.history_filename)
        self.favorites = self.load_data(self.favorites_filename)

    def load_data(self, filename):
        """Завантажує дані з файлу."""
        try:
            if os.path.exists(filename):
                with open(filename, "r", encoding='utf-8') as file:
                    return json.load(file)
            return []
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return []

    def save_data(self, filename, data):
        """Зберігає дані в файл."""
        try:
            with open(filename, "w", encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving {filename}: {e}")

    def add_to_history(self, filename, time_code):
        """Додає файл до історії."""
        self.history.append({"filename": filename, "time_code": time_code})
        self.save_data(self.history_filename, self.history)

    def add_to_favorites(self, filename):
        """Додає файл в улюблені."""
        if filename not in self.favorites:
            self.favorites.append(filename)
            self.save_data(self.favorites_filename, self.favorites)

    def remove_from_favorites(self, filename):
        """Видаляє файл з улюблених."""
        if filename in self.favorites:
            self.favorites.remove(filename)
            self.save_data(self.favorites_filename, self.favorites)