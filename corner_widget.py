import os
import sys
import ctypes
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import random
from utils import get_resource_path

class CornerWidget(ctk.CTkToplevel):
    """
    Sorufelek - Ders İçi Soru ve Kura Ekranı (GUI HUD Arayüzü).
    Çerçevesiz (frameless) arayüz; Windows başlık çubuğu bulunmaz.
    Ekran sınırları ve Windows DPI ölçeklemesi otomatik hesaba katılır,
    asla ekranın dışına taşmaz ve kalıcı olarak en üst katmanda durur.
    """
    def __init__(self, master, data_manager, sound_player, on_return_to_main):
        super().__init__(master)
        self.dm = data_manager
        self.sound = sound_player
        self.on_return_to_main = on_return_to_main

        # Çerçevesiz arayüz: OS pencere başlığı yok
        self.overrideredirect(True)

        # İkon yükleme (Windows: ico, Linux/Pardus: png)
        try:
            if sys.platform == "win32":
                icon_p = get_resource_path("icon.ico")
                if os.path.exists(icon_p):
                    self.iconbitmap(icon_p)
            else:
                icon_png = get_resource_path("icon.png")
                if os.path.exists(icon_png):
                    from PIL import ImageTk, Image
                    self._icon_img = ImageTk.PhotoImage(Image.open(icon_png))
                    self.iconphoto(False, self._icon_img)
        except Exception:
            pass

        # Boyut tanımları
        self.normal_width = 285
        self.normal_height = 124
        self.mini_height = 34
        self._is_mini_mode = False

        # Durum değişkenleri
        self._drag_x = 0
        self._drag_y = 0
        self._is_animating = False
        self._last_shown_student = None
        self._is_cycle_completed = False

        # Her Zaman En Üstte Tutma Kilidi
        self.attributes("-topmost", True)
        self.lift()

        # Ekran Güvenli Köşe Konumlandırması (DPI ve Çözünürlük Uyumlu)
        self._position_top_right(self.normal_width, self.normal_height)

        # Arayüzü Kur
        self._setup_ui()
        self._bind_events()
        self.refresh_display()

        # Windows seviyesinde en üst katmana kilitle
        self.after(50, self._ensure_topmost_lock)

    def _ensure_topmost_lock(self):
        try:
            self.attributes("-topmost", True)
            self.lift()
            if sys.platform == "win32":
                # Windows API: HWND_TOPMOST (-1), SWP_NOMOVE (0x0002) | SWP_NOSIZE (0x0001) | SWP_NOACTIVATE (0x0010)
                ctypes.windll.user32.SetWindowPos(
                    self.winfo_id(),
                    -1,
                    0, 0, 0, 0,
                    0x0001 | 0x0002 | 0x0010
                )
        except Exception:
            pass

    def _position_top_right(self, w, h):
        """
        DPI ölçeklemesini hesaba katarak pencereyi ekranın sağ üst köşesine
        ekranın dışına asla taşmayacak şekilde güvenli mesafeyle yerleştirir.
        """
        self.update_idletasks()
        scaling = ctk.ScalingTracker.get_widget_scaling(self)
        actual_w = int(w * scaling)
        actual_h = int(h * scaling)

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        margin_x = 24
        margin_y = 20

        # Sağ kenardan güvenli mesafe ile konumlandır
        pos_x = max(10, screen_w - actual_w - margin_x)
        pos_y = max(10, margin_y)
        self.geometry(f"{w}x{h}+{pos_x}+{pos_y}")

    def _setup_ui(self):
        self.main_border = ctk.CTkFrame(
            self,
            corner_radius=8,
            fg_color="#181818",
            border_width=1,
            border_color="#383838"
        )
        self.main_border.pack(fill="both", expand=True)

        # =========================================================================
        # 1. ENTEGRE BAŞLIK ÇUBUĞU (Kompakt ve Ferah Kontrol Alanı)
        # =========================================================================
        self.header_frame = ctk.CTkFrame(
            self.main_border,
            fg_color="#202020",
            corner_radius=6,
            height=28
        )
        self.header_frame.pack(fill="x", padx=4, pady=(4, 2))
        self.header_frame.pack_propagate(False)

        # Sınıf Seçim Açılır Menüsü
        self.class_var = ctk.StringVar(value=self.dm.get_active_class())
        class_names = self.dm.get_class_names() or ["Sınıf Yok"]
        self.class_dropdown = ctk.CTkOptionMenu(
            self.header_frame,
            values=class_names,
            variable=self.class_var,
            command=self._on_class_changed,
            width=76,
            height=22,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#2a2a2a",
            button_color="#333333",
            button_hover_color="#444444",
            dropdown_font=ctk.CTkFont(family="Segoe UI", size=10)
        )
        self.class_dropdown.pack(side="left", padx=(3, 2), pady=3)

        # Durum Sayacı (Kalan / Toplam)
        self.stats_label = ctk.CTkLabel(
            self.header_frame,
            text="0 / 0",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#90caf9"
        )
        self.stats_label.pack(side="left", padx=3)

        # --- Sağ Kontrol Butonları (Yalnızca temel butonlar: Kapat, Mini Çubuk, Ayarlar) ---
        # 1. Kapat Butonu (✕)
        self.close_btn = ctk.CTkButton(
            self.header_frame,
            text="✕",
            width=22,
            height=20,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            fg_color="transparent",
            hover_color="#542525",
            text_color="#cccccc",
            command=self._go_to_main
        )
        self.close_btn.pack(side="right", padx=(1, 3), pady=3)

        # 2. Mini Çubuk Geçiş Butonu (_ / □)
        self.mini_btn = ctk.CTkButton(
            self.header_frame,
            text="—",
            width=22,
            height=20,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            fg_color="transparent",
            hover_color="#333333",
            text_color="#cccccc",
            command=self._toggle_mini_mode
        )
        self.mini_btn.pack(side="right", padx=1, pady=3)

        # 3. Yönetim Paneli Butonu (⚙)
        self.settings_btn = ctk.CTkButton(
            self.header_frame,
            text="⚙",
            width=22,
            height=20,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="transparent",
            hover_color="#333333",
            text_color="#cccccc",
            command=self._go_to_main
        )
        self.settings_btn.pack(side="right", padx=1, pady=3)

        # =========================================================================
        # 2. GÖVDE PANELİ (Mini Modda Gizlenir)
        # =========================================================================
        self.body_frame = ctk.CTkFrame(self.main_border, fg_color="transparent")
        self.body_frame.pack(fill="both", expand=True, padx=4, pady=2)

        # İsim Kartı Alanı
        self.card_frame = ctk.CTkFrame(
            self.body_frame,
            fg_color="#212121",
            corner_radius=6,
            border_width=1,
            border_color="#303030",
            height=48
        )
        self.card_frame.pack(fill="x", padx=2, pady=(1, 3))
        self.card_frame.pack_propagate(False)

        self.name_label = ctk.CTkLabel(
            self.card_frame,
            text="Öğrenci Seçimi Bekleniyor",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#ffffff"
        )
        self.name_label.pack(expand=True, pady=(2, 0))

        self.sub_label = ctk.CTkLabel(
            self.card_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color="#888888"
        )
        self.sub_label.pack(pady=(0, 2))

        # Eylemler Çubuğu
        self.actions_frame = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        self.actions_frame.pack(fill="x", padx=2, pady=(0, 2))

        # Ana Kura Butonu
        self.pick_button = ctk.CTkButton(
            self.actions_frame,
            text="Öğrenci Seç",
            height=28,
            corner_radius=4,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#0067c0",
            hover_color="#005fb8",
            command=self.start_pick
        )
        self.pick_button.pack(side="left", expand=True, fill="x", padx=(0, 3))

        # Geri Al Butonu
        self.undo_btn = ctk.CTkButton(
            self.actions_frame,
            text="Geri Al",
            width=46,
            height=28,
            corner_radius=4,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            fg_color="#2a2a2a",
            hover_color="#383838",
            command=self._undo_last
        )
        self.undo_btn.pack(side="left", padx=2)

        # Sıfırla Butonu
        self.reset_btn = ctk.CTkButton(
            self.actions_frame,
            text="Sıfırla",
            width=46,
            height=28,
            corner_radius=4,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            fg_color="#2a2a2a",
            hover_color="#383838",
            command=self._confirm_manual_reset
        )
        self.reset_btn.pack(side="left", padx=(2, 0))

    def _bind_events(self):
        self.header_frame.bind("<Button-1>", self._start_drag)
        self.header_frame.bind("<B1-Motion>", self._on_drag)

        # Odak kaybolduğunda en üstte kalma kilidini tazele
        self.bind("<FocusOut>", lambda e: self._ensure_topmost_lock())
        self.bind("<FocusIn>", lambda e: self._ensure_topmost_lock())

        # Kısayollar
        self.bind("<space>", lambda e: self.start_pick())
        self.bind("<Return>", lambda e: self.start_pick())
        self.bind("<Escape>", lambda e: self._go_to_main())
        self.bind("<Control-z>", lambda e: self._undo_last())

    def _start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag(self, event):
        new_x = self.winfo_x() + (event.x - self._drag_x)
        new_y = self.winfo_y() + (event.y - self._drag_y)

        # Ekran sınırlarına kelepçele (Kullanıcı pencereyi ekranın dışına sürükleyemez)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        scaling = ctk.ScalingTracker.get_widget_scaling(self)
        cur_h = self.mini_height if self._is_mini_mode else self.normal_height
        actual_w = int(self.normal_width * scaling)
        actual_h = int(cur_h * scaling)

        clamped_x = max(10, min(screen_w - actual_w - 10, new_x))
        clamped_y = max(10, min(screen_h - actual_h - 45, new_y))

        self.geometry(f"+{clamped_x}+{clamped_y}")
        self._ensure_topmost_lock()

    def _toggle_mini_mode(self):
        self._is_mini_mode = not self._is_mini_mode
        cur_x = self.winfo_x()
        cur_y = self.winfo_y()
        if self._is_mini_mode:
            self.body_frame.pack_forget()
            self.geometry(f"{self.normal_width}x{self.mini_height}+{cur_x}+{cur_y}")
            self.mini_btn.configure(text="□")
        else:
            self.body_frame.pack(fill="both", expand=True, padx=4, pady=2)
            self.geometry(f"{self.normal_width}x{self.normal_height}+{cur_x}+{cur_y}")
            self.mini_btn.configure(text="—")
        self._ensure_topmost_lock()

    def _on_class_changed(self, choice):
        self.dm.set_active_class(choice)
        self._last_shown_student = None
        self._is_cycle_completed = False
        self.name_label.configure(
            text="Öğrenci Seçimi Bekleniyor",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        self.sub_label.configure(text="")
        self.refresh_display()
        self._ensure_topmost_lock()

    def _go_to_main(self):
        self.withdraw()
        if self.on_return_to_main:
            self.on_return_to_main()

    def refresh_classes_dropdown(self):
        classes = self.dm.get_class_names() or ["Sınıf Yok"]
        self.class_dropdown.configure(values=classes)
        active = self.dm.get_active_class()
        if active in classes:
            self.class_var.set(active)
        elif classes and classes[0] != "Sınıf Yok":
            self.class_var.set(classes[0])
            self.dm.set_active_class(classes[0])
        else:
            self.class_var.set("Sınıf Yok")
        self._ensure_topmost_lock()

    def refresh_display(self):
        active_class = self.dm.get_active_class()
        self.class_var.set(active_class or "Sınıf Yok")

        if not active_class:
            self.stats_label.configure(text="0/0")
            self.name_label.configure(
                text="Sınıf Tanımlayınız",
                text_color="#e57373",
                font=ctk.CTkFont(family="Segoe UI", size=12)
            )
            self.sub_label.configure(text="Yönetim panelinden sınıf ekleyiniz")
            self.pick_button.configure(state="disabled", text="Sınıf Yok", fg_color="#2a2a2a")
            self._is_cycle_completed = False
            self._ensure_topmost_lock()
            return

        all_students = self.dm.get_all_students(active_class)
        remaining = self.dm.get_remaining_students(active_class)
        exempt = self.dm.get_exempt_students(active_class)
        active_total = len(all_students) - len(exempt)

        self.stats_label.configure(text=f"Kalan: {len(remaining)}/{active_total}")

        if len(all_students) == 0:
            self.name_label.configure(
                text="Öğrenci Kaydı Yok",
                text_color="#e57373",
                font=ctk.CTkFont(family="Segoe UI", size=12)
            )
            self.sub_label.configure(text="Yönetim panelinden öğrenci ekleyiniz")
            self.pick_button.configure(state="disabled", text="Öğrenci Yok", fg_color="#2a2a2a")
            self._is_cycle_completed = False
        elif len(remaining) == 0 and active_total > 0:
            self._is_cycle_completed = True
            if not self._last_shown_student:
                self.name_label.configure(
                    text="Sınıf Listesi Tamamlandı",
                    text_color="#81c784",
                    font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
                )
                self.sub_label.configure(text="Tüm öğrencilere soru yöneltilmiştir")
            self.pick_button.configure(
                state="normal",
                text="Yeni Tur Başlat",
                fg_color="#107c41",
                hover_color="#0b5a2f"
            )
        else:
            self._is_cycle_completed = False
            self.pick_button.configure(
                state="normal",
                text="Öğrenci Seç",
                fg_color="#0067c0",
                hover_color="#005fb8"
            )
        self._ensure_topmost_lock()

    def start_pick(self):
        if self._is_animating:
            return

        active_class = self.dm.get_active_class()
        if not active_class:
            messagebox.showinfo("Bilgilendirme", "Lütfen önce yönetim panelinden bir sınıf tanımlayınız.")
            return

        all_students = self.dm.get_all_students(active_class)
        remaining = self.dm.get_remaining_students(active_class)

        if not all_students:
            messagebox.showinfo("Bilgilendirme", "Seçili sınıfta kayıtlı öğrenci bulunmamaktadır.")
            return

        if self._is_cycle_completed or len(remaining) == 0:
            self._reset_and_start_new_cycle()
            return

        self._is_animating = True
        self.pick_button.configure(state="disabled", text="Seçim Yapılıyor...")
        self.sub_label.configure(text="")

        winner, is_exhausted = self.dm.pick_random(active_class)
        pool = all_students if len(all_students) > 1 else [winner]
        shuffles = 10
        base_delay = 45

        def _step(step_idx):
            if step_idx < shuffles:
                temp_name = random.choice(pool)
                self.name_label.configure(text=temp_name, text_color="#90caf9")
                self.sound.play_tick()
                next_delay = base_delay + int((step_idx / shuffles) ** 2 * 55)
                self.after(next_delay, lambda: _step(step_idx + 1))
            else:
                self._reveal_winner(winner, is_exhausted)

        _step(0)

    def _reveal_winner(self, winner, is_exhausted):
        self._is_animating = False
        self._last_shown_student = winner

        font_size = 12 if len(winner) > 22 else 14
        self.name_label.configure(
            text=winner,
            font=ctk.CTkFont(family="Segoe UI", size=font_size, weight="bold"),
            text_color="#ffffff"
        )

        active_class = self.dm.get_active_class()
        all_students = self.dm.get_all_students(active_class)
        remaining = self.dm.get_remaining_students(active_class)
        exempt = self.dm.get_exempt_students(active_class)
        active_total = len(all_students) - len(exempt)

        self.stats_label.configure(text=f"Kalan: {len(remaining)}/{active_total}")
        self.sound.play_reveal()

        if is_exhausted:
            self._is_cycle_completed = True
            self.sub_label.configure(
                text="Son Öğrenci • Sınıf Listesi Tamamlandı",
                text_color="#81c784"
            )
            self.pick_button.configure(
                state="normal",
                text="Yeni Tur Başlat",
                fg_color="#107c41",
                hover_color="#0b5a2f"
            )
        else:
            self._is_cycle_completed = False
            self.sub_label.configure(text=f"Kalan: {len(remaining)} öğrenci", text_color="#888888")
            self.pick_button.configure(
                state="normal",
                text="Öğrenci Seç",
                fg_color="#0067c0",
                hover_color="#005fb8"
            )
        self._ensure_topmost_lock()

    def _reset_and_start_new_cycle(self):
        active_class = self.dm.get_active_class()
        self.dm.reset_picked(active_class)
        self._last_shown_student = None
        self._is_cycle_completed = False
        self.refresh_display()
        self.name_label.configure(
            text="Yeni Tur Başlatıldı",
            text_color="#81c784",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        self.sub_label.configure(text="Soru yöneltmek için butona basınız")
        self._ensure_topmost_lock()

    def _undo_last(self):
        active_class = self.dm.get_active_class()
        undone = self.dm.undo_pick(active_class)
        if undone:
            self._last_shown_student = None
            self.refresh_display()
            self.name_label.configure(
                text=undone,
                text_color="#e0e0e0",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
            )
            self.sub_label.configure(text="Seçim geri alındı (Listeye iade edildi)")
        else:
            messagebox.showinfo("Bilgilendirme", "Geri alınabilecek aktif bir seçim bulunmamaktadır.")
        self._ensure_topmost_lock()

    def _confirm_manual_reset(self):
        active_class = self.dm.get_active_class()
        res = messagebox.askyesno(
            "Tur Sıfırlama Onayı",
            f"'{active_class}' sınıfına ait soru çözüm sırasını baştan başlatmak istediğinizi onaylıyor musunuz?"
        )
        if res:
            self._reset_and_start_new_cycle()
        self._ensure_topmost_lock()
