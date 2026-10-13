import sys
import ctypes
import customtkinter as ctk

# Enable High-DPI awareness on Windows across all resolutions & scaling settings
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Per-Monitor DPI aware
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

from data_manager import DataManager
from sound_effects import SoundPlayer
from main_window import MainWindow
from corner_widget import CornerWidget

class OgrenciSeciciApp:
    """
    Main Application Controller coordinating MainWindow and CornerWidget.
    """
    def __init__(self):
        self.dm = DataManager()
        self.sound = SoundPlayer(self.dm)
        
        # Initialize MainWindow
        self.main_window = MainWindow(
            data_manager=self.dm,
            sound_player=self.sound,
            on_launch_corner_mode=self.show_corner_mode
        )
        
        # Corner widget instance
        self.corner_widget = None

        # Clean exit hook
        self.main_window.protocol("WM_DELETE_WINDOW", self.on_main_close)

    def show_corner_mode(self):
        if self.corner_widget is None or not self.corner_widget.winfo_exists():
            self.corner_widget = CornerWidget(
                master=self.main_window,
                data_manager=self.dm,
                sound_player=self.sound,
                on_return_to_main=self.show_main_mode
            )
        else:
            self.corner_widget.deiconify()
            self.corner_widget.refresh_classes_dropdown()
            self.corner_widget.refresh_display()
            self.corner_widget.lift()

    def show_main_mode(self):
        if self.corner_widget and self.corner_widget.winfo_exists():
            self.corner_widget.withdraw()
        self.main_window.deiconify()
        self.main_window.refresh_all()
        self.main_window.lift()

    def on_main_close(self):
        if self.corner_widget and self.corner_widget.winfo_exists():
            self.corner_widget.destroy()
        self.main_window.destroy()
        sys.exit(0)

    def run(self):
        self.main_window.mainloop()

if __name__ == "__main__":
    app = OgrenciSeciciApp()
    app.run()
