import threading
import time
import sys

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

class SoundPlayer:
    """
    Non-blocking sound player for Windows (winsound) and Pardus/Linux (bell / safe fallback).
    Plays ticks during name shuffling and a chime upon reveal.
    """
    def __init__(self, data_manager):
        self.dm = data_manager

    def is_enabled(self):
        return bool(self.dm.get_setting("sound_enabled", True))

    def play_tick(self):
        if not self.is_enabled():
            return
        def _run():
            try:
                if HAS_WINSOUND:
                    winsound.Beep(900, 25)
                else:
                    sys.stdout.write('\a')
                    sys.stdout.flush()
            except Exception:
                pass
        threading.Thread(target=_run, daemon=True).start()

    def play_reveal(self):
        if not self.is_enabled():
            return
        def _run():
            try:
                if HAS_WINSOUND:
                    # Pleasant high-pitch celebratory chime
                    chords = [(659, 70), (784, 80), (1046, 200)]  # E5, G5, C6
                    for freq, dur in chords:
                        winsound.Beep(freq, dur)
                        time.sleep(0.02)
                else:
                    sys.stdout.write('\a')
                    sys.stdout.flush()
            except Exception:
                pass
        threading.Thread(target=_run, daemon=True).start()

    def play_complete_fanfare(self):
        if not self.is_enabled():
            return
        def _run():
            try:
                if HAS_WINSOUND:
                    melody = [(523, 100), (659, 100), (784, 100), (1046, 300)]
                    for freq, dur in melody:
                        winsound.Beep(freq, dur)
                        time.sleep(0.03)
                else:
                    sys.stdout.write('\a')
                    sys.stdout.flush()
            except Exception:
                pass
        threading.Thread(target=_run, daemon=True).start()
