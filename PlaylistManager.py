import os
import json
import logging

class PlaylistManager:
    def __init__(self, filename="playlist.json"):
        self.filename = filename
        self.playlists = self.load_playlists()

    def load_playlists(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, "r", encoding='utf-8') as file:
                    return json.load(file)
            return {"favorites": [], "custom_playlists": {}}
        except Exception as e:
            logging.error(f"Error loading playlists: {str(e)}")
            return {"favorites": [], "custom_playlists": {}}

    def save_playlists(self):
        try:
            with open(self.filename, "w", encoding='utf-8') as file:
                json.dump(self.playlists, file, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"Error saving playlists: {str(e)}")

    def add_to_favorites(self, video_path):
        if video_path not in self.playlists["favorites"]:
            self.playlists["favorites"].append(video_path)
            self.save_playlists()
            return True
        return False

    def remove_from_favorites(self, video_path):
        if video_path in self.playlists["favorites"]:
            self.playlists["favorites"].remove(video_path)
            self.save_playlists()
            return True
        return False