import os

import pygame

from src.constants import MUSIC_DIR
from src.utils import clamp


class MusicManager:
    END_EVENT = pygame.USEREVENT + 1
    SUPPORTED_EXTENSIONS = {".mp3", ".ogg", ".wav"}

    def __init__(self, volume=0.5):
        self.enabled = False
        self.volume = clamp(volume, 0.0, 1.0)
        self.music_dir = MUSIC_DIR
        self.tracks = []
        self.current_index = -1
        self.ensure_music_dir()
        self._init_mixer()
        self.reload_tracks()
        self.set_volume(self.volume)
        self.play()

    def ensure_music_dir(self):
        os.makedirs(self.music_dir, exist_ok=True)

    def _init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.set_endevent(self.END_EVENT)
            self.enabled = True
        except pygame.error:
            self.enabled = False

    def reload_tracks(self):
        if not os.path.isdir(self.music_dir):
            self.tracks = []
            return

        self.tracks = sorted(
            os.path.join(self.music_dir, name)
            for name in os.listdir(self.music_dir)
            if os.path.splitext(name)[1].lower() in self.SUPPORTED_EXTENSIONS
        )
        if self.current_index >= len(self.tracks):
            self.current_index = -1

    def set_volume(self, volume):
        self.volume = clamp(volume, 0.0, 1.0)
        if self.enabled:
            pygame.mixer.music.set_volume(self.volume)

    def play(self):
        if not self.enabled:
            return
        self.reload_tracks()
        if not self.tracks:
            pygame.mixer.music.stop()
            return
        if pygame.mixer.music.get_busy():
            return
        self.play_next()

    def play_next(self):
        if not self.enabled or not self.tracks:
            return
        self.current_index = (self.current_index + 1) % len(self.tracks)
        track = self.tracks[self.current_index]
        try:
            pygame.mixer.music.load(track)
            pygame.mixer.music.play()
            pygame.mixer.music.set_volume(self.volume)
        except pygame.error:
            pass

    def handle_event(self, event):
        if event.type == self.END_EVENT:
            self.play_next()
