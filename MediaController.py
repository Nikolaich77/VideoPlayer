import sys
import os
import vlc
import logging

class MediaController:
    def __init__(self, video_frame):
        """
        Ініціалізація медіа контролера
        Args:
            video_frame: QFrame для відображення відео
        """
        try:
            self.instance = vlc.Instance('--no-xlib')  # Покращена ініціалізація VLC
            self.player = self.instance.media_player_new()
            self.event_manager = self.player.event_manager()
            
            # Налаштування відображення відео в залежності від операційної системи
            if sys.platform.startswith('linux'):
                self.player.set_xwindow(video_frame.winId())
            elif sys.platform == "win32":
                self.player.set_hwnd(video_frame.winId())
            elif sys.platform == "darwin":
                self.player.set_nsobject(int(video_frame.winId()))
                
            # Початкові налаштування
            self.player.audio_set_volume(50)
            self._current_media = None
            self.video_frame = video_frame
            
        except Exception as e:
            logging.error(f"Error initializing MediaController: {str(e)}")
            raise

    def set_media(self, media_path):
        """
        Встановлення медіа файлу для відтворення
        Args:
            media_path: Шлях до медіа файлу
        """
        try:
            if os.path.exists(media_path):
                self._current_media = self.instance.media_new(media_path)
                self.player.set_media(self._current_media)
                return True
            else:
                logging.error(f"Media file not found: {media_path}")
                return False
        except Exception as e:
            logging.error(f"Error setting media: {str(e)}")
            return False

    def play(self):
        """Відтворення медіа"""
        try:
            return self.player.play()
        except Exception as e:
            logging.error(f"Error playing media: {str(e)}")
            return -1

    def pause(self):
        """Пауза відтворення"""
        try:
            self.player.pause()
        except Exception as e:
            logging.error(f"Error pausing media: {str(e)}")

    def stop(self):
        """Зупинка відтворення"""
        try:
            self.player.stop()
        except Exception as e:
            logging.error(f"Error stopping media: {str(e)}")

    def set_position(self, position):
        """
        Встановлення позиції відтворення
        Args:
            position: Позиція від 0 до 1
        """
        try:
            if 0 <= position <= 1:
                self.player.set_position(position)
        except Exception as e:
            logging.error(f"Error setting position: {str(e)}")

    def get_position(self):
        """
        Отримання поточної позиції відтворення
        Returns:
            float: Позиція від 0 до 1
        """
        try:
            return self.player.get_position()
        except Exception as e:
            logging.error(f"Error getting position: {str(e)}")
            return 0

    def set_volume(self, volume):
        """
        Встановлення гучності
        Args:
            volume: Гучність від 0 до 100
        """
        try:
            if 0 <= volume <= 100:
                self.player.audio_set_volume(volume)
        except Exception as e:
            logging.error(f"Error setting volume: {str(e)}")

    def get_volume(self):
        """
        Отримання поточної гучності
        Returns:
            int: Гучність від 0 до 100
        """
        try:
            return self.player.audio_get_volume()
        except Exception as e:
            logging.error(f"Error getting volume: {str(e)}")
            return 50

    def set_playback_rate(self, rate):
        """
        Встановлення швидкості відтворення
        Args:
            rate: Швидкість відтворення (1.0 = нормальна швидкість)
        """
        try:
            self.player.set_rate(rate)
        except Exception as e:
            logging.error(f"Error setting playback rate: {str(e)}")

    def get_playback_rate(self):
        """
        Отримання поточної швидкості відтворення
        Returns:
            float: Поточна швидкість відтворення
        """
        try:
            return self.player.get_rate()
        except Exception as e:
            logging.error(f"Error getting playback rate: {str(e)}")
            return 1.0

    def toggle_fullscreen(self):
        """Переключення повноекранного режиму"""
        try:
            self.player.toggle_fullscreen()
        except Exception as e:
            logging.error(f"Error toggling fullscreen: {str(e)}")

    def is_playing(self):
        """
        Перевірка чи відтворюється медіа
        Returns:
            bool: True якщо відтворюється, False якщо ні
        """
        try:
            return self.player.is_playing()
        except Exception as e:
            logging.error(f"Error checking play status: {str(e)}")
            return False

    def get_time(self):
        """
        Отримання поточного часу відтворення в мілісекундах
        Returns:
            int: Поточний час в мс
        """
        try:
            return self.player.get_time()
        except Exception as e:
            logging.error(f"Error getting time: {str(e)}")
            return 0

    def get_length(self):
        """
        Отримання загальної тривалості медіа в мілісекундах
        Returns:
            int: Тривалість в мс
        """
        try:
            return self.player.get_length()
        except Exception as e:
            logging.error(f"Error getting length: {str(e)}")
            return 0

    def add_event_listener(self, event_type, callback):
        """
        Додавання обробника подій
        Args:
            event_type: Тип події VLC
            callback: Функція обробник
        """
        try:
            self.event_manager.event_attach(event_type, callback)
        except Exception as e:
            logging.error(f"Error adding event listener: {str(e)}")

    def remove_event_listener(self, event_type, callback):
        """
        Видалення обробника подій
        Args:
            event_type: Тип події VLC
            callback: Функція обробник
        """
        try:
            self.event_manager.event_detach(event_type, callback)
        except Exception as e:
            logging.error(f"Error removing event listener: {str(e)}")

    def cleanup(self):
        """Очищення ресурсів"""
        try:
            self.player.stop()
            self.player.release()
            self.instance.release()
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")