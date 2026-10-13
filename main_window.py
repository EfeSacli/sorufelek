import os
import sys
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from utils import get_resource_path

class MainWindow(ctk.CTk):
    """
    Sorufelek - Merkezi Sınıf ve Kura Yönetim Paneli.
    Öğretmen kendi sınıflarını ve öğrenci listelerini yönetir.
    """
    def __init__(self, data_manager, sound_player, on_launch_corner_mode):
        super().__init__()
        self.dm = data_manager
        self.sound = sound_player
        self.on_launch_corner_mode = on_launch_corner_mode

        self.title("Sorufelek - Ders İçi Soru ve Kura Sistemi")

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

        # Ekran Çözünürlüğüne Duyarlı Boyutlandırma
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        win_w = min(940, max(720, int(screen_w * 0.75)))
        win_h = min(630, max(460, int(screen_h * 0.75)))
        pos_x = max(10, (screen_w - win_w) // 2)
        pos_y = max(10, (screen_h - win_h) // 2)
        self.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.minsize(700, 460)

        # Tema
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.search_filter = ""
        self._setup_layout()
        self.refresh_all()

    def _setup_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # =========================================================================
        # 1. SOL PANEL (Sınıf Listesi ve Kontroller)
        # =========================================================================
        self.sidebar_frame = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color="#181818")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(2, weight=1)

        # Sorufelek Başlığı
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Sorufelek",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#ffffff"
        )
        self.logo_label.grid(row=0, column=0, padx=16, pady=(16, 2), sticky="w")

        self.subtitle_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Ders İçi Soru ve Kura Sistemi",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#888888"
        )
        self.subtitle_label.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="w")

        # Sınıflar Kaydırma Alanı
        self.class_scroll = ctk.CTkScrollableFrame(
            self.sidebar_frame,
            label_text="Sınıflar",
            label_font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            label_text_color="#999999",
            fg_color="transparent"
        )
        self.class_scroll.grid(row=2, column=0, padx=10, pady=4, sticky="nsew")

        # Sınıf Butonları
        self.class_btns_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.class_btns_frame.grid(row=3, column=0, padx=12, pady=6, sticky="ew")

        self.add_class_btn = ctk.CTkButton(
            self.class_btns_frame,
            text="Yeni Sınıf Tanımla",
            height=30,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#0067c0",
            hover_color="#005fb8",
            command=self._prompt_add_class
        )
        self.add_class_btn.pack(fill="x", pady=2)

        self.rename_class_btn = ctk.CTkButton(
            self.class_btns_frame,
            text="Sınıf Adını Değiştir",
            height=28,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#2b2b2b",
            hover_color="#383838",
            command=self._prompt_rename_class
        )
        self.rename_class_btn.pack(fill="x", pady=2)

        self.del_class_btn = ctk.CTkButton(
            self.class_btns_frame,
            text="Sınıfı Sil",
            height=28,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#3a1c1c",
            hover_color="#542525",
            text_color="#f87171",
            command=self._confirm_delete_class
        )
        self.del_class_btn.pack(fill="x", pady=2)

        # Alt Alan (Ders Modunu Başlat)
        self.bottom_sidebar = ctk.CTkFrame(self.sidebar_frame, fg_color="#222222", corner_radius=8)
        self.bottom_sidebar.grid(row=4, column=0, padx=10, pady=(6, 12), sticky="ew")

        self.launch_corner_btn = ctk.CTkButton(
            self.bottom_sidebar,
            text="Ders Ekranını Başlat",
            height=40,
            corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#107c41",
            hover_color="#0b5a2f",
            command=self.launch_corner_mode
        )
        self.launch_corner_btn.pack(fill="x", padx=8, pady=8)

        self.sound_switch = ctk.CTkSwitch(
            self.bottom_sidebar,
            text="Ses Efektleri",
            command=self._toggle_sound_switch,
            font=ctk.CTkFont(family="Segoe UI", size=11)
        )
        if self.dm.get_setting("sound_enabled", True):
            self.sound_switch.select()
        else:
            self.sound_switch.deselect()
        self.sound_switch.pack(padx=10, pady=(0, 8), anchor="w")

        # =========================================================================
        # 2. SAĞ PANEL (Öğrenci Yönetimi)
        # =========================================================================
        self.main_frame = ctk.CTkFrame(self, fg_color="#202020", corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Başlık ve Seçim Geçmişi Butonu
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(16, 8), sticky="ew")

        self.current_class_title = ctk.CTkLabel(
            self.header_frame,
            text="Sınıf Seçimi Yapınız",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#ffffff"
        )
        self.current_class_title.pack(side="left")

        self.history_btn = ctk.CTkButton(
            self.header_frame,
            text="Seçim Geçmişi",
            height=28,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#2b2b2b",
            hover_color="#383838",
            command=self._open_history_dialog
        )
        self.history_btn.pack(side="right")

        # İstatistik Kartları
        self.stats_cards_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.stats_cards_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.card_total = self._create_stat_card(self.stats_cards_frame, "Toplam Kayıt", "0", "#ffffff")
        self.card_total.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.card_picked = self._create_stat_card(self.stats_cards_frame, "Soru Yöneltilen", "0", "#b0b0b0")
        self.card_picked.pack(side="left", expand=True, fill="x", padx=6)

        self.card_remaining = self._create_stat_card(self.stats_cards_frame, "Sırada Bekleyen", "0", "#81c784")
        self.card_remaining.pack(side="left", expand=True, fill="x", padx=(6, 0))

        # Araç Çubuğu
        self.toolbar_frame = ctk.CTkFrame(self.main_frame, fg_color="#282828", corner_radius=8)
        self.toolbar_frame.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.bulk_paste_btn = ctk.CTkButton(
            self.toolbar_frame,
            text="Toplu Liste Aktarımı (Excel / e-Okul)",
            height=32,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#0067c0",
            hover_color="#005fb8",
            command=self._open_bulk_paste_dialog
        )
        self.bulk_paste_btn.pack(side="left", padx=(8, 6), pady=6)

        self.single_entry = ctk.CTkEntry(
            self.toolbar_frame,
            placeholder_text="Öğrenci Adı Soyadı...",
            width=180,
            height=32,
            font=ctk.CTkFont(family="Segoe UI", size=11)
        )
        self.single_entry.pack(side="left", padx=4, pady=6)
        self.single_entry.bind("<Return>", lambda e: self._add_single_student())

        self.add_single_btn = ctk.CTkButton(
            self.toolbar_frame,
            text="Kaydet",
            width=60,
            height=32,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#2b2b2b",
            hover_color="#383838",
            command=self._add_single_student
        )
        self.add_single_btn.pack(side="left", padx=(2, 8), pady=6)

        self.clear_roster_btn = ctk.CTkButton(
            self.toolbar_frame,
            text="Listeyi Temizle",
            height=32,
            width=100,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#3a1c1c",
            hover_color="#542525",
            text_color="#f87171",
            command=self._confirm_clear_roster
        )
        self.clear_roster_btn.pack(side="right", padx=(4, 8), pady=6)

        self.reset_cycle_btn = ctk.CTkButton(
            self.toolbar_frame,
            text="Soru Turunu Sıfırla",
            height=32,
            width=130,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#2b2b2b",
            hover_color="#383838",
            command=self._confirm_reset_cycle
        )
        self.reset_cycle_btn.pack(side="right", padx=4, pady=6)

        # Öğrenci Tablosu
        self.roster_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.roster_container.grid(row=3, column=0, padx=20, pady=(0, 12), sticky="nsew")
        self.roster_container.grid_rowconfigure(1, weight=1)
        self.roster_container.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            self.roster_container,
            placeholder_text="Listede ara...",
            height=30,
            font=ctk.CTkFont(family="Segoe UI", size=11)
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.search_entry.bind("<KeyRelease>", self._on_search_typed)

        self.roster_scroll = ctk.CTkScrollableFrame(
            self.roster_container,
            fg_color="#181818",
            corner_radius=8
        )
        self.roster_scroll.grid(row=1, column=0, sticky="nsew")

    def _create_stat_card(self, parent, title, initial_val, color):
        frame = ctk.CTkFrame(parent, fg_color="#282828", corner_radius=8, height=64)
        frame.pack_propagate(False)

        val_label = ctk.CTkLabel(
            frame,
            text=initial_val,
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=color
        )
        val_label.pack(pady=(6, 0))

        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#888888"
        )
        title_label.pack(pady=(0, 4))

        frame._val_label = val_label
        return frame

    def _toggle_sound_switch(self):
        val = bool(self.sound_switch.get())
        self.dm.set_setting("sound_enabled", val)

    def _on_search_typed(self, event):
        self.search_filter = self.search_entry.get().strip().lower()
        self.refresh_roster()

    def launch_corner_mode(self):
        active = self.dm.get_active_class()
        if not active:
            messagebox.showwarning(
                "Sınıf Tanımlanmadı",
                "Ders ekranını başlatabilmek için lütfen öncelikle sol menüden 'Yeni Sınıf Tanımla' butonuna basarak bir sınıf oluşturunuz."
            )
            return

        students = self.dm.get_all_students(active)
        if not students:
            messagebox.showwarning(
                "Öğrenci Kaydı Yok",
                f"'{active}' sınıfında henüz kayıtlı öğrenci bulunmuyor.\n"
                "Lütfen 'Toplu Liste Aktarımı' veya tek tek öğrenci ekleyiniz."
            )
            return
        
        self.withdraw()
        self.on_launch_corner_mode()

    # --- REFRESH LOGIC ---
    def refresh_all(self):
        self.refresh_classes_sidebar()
        self.refresh_roster()

    def refresh_classes_sidebar(self):
        for widget in self.class_scroll.winfo_children():
            widget.destroy()

        class_names = self.dm.get_class_names()
        active = self.dm.get_active_class()

        if not class_names:
            lbl = ctk.CTkLabel(
                self.class_scroll,
                text="Henüz sınıf tanımlanmadı.\nAşağıdaki butondan ekleyiniz.",
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color="#777777",
                justify="center"
            )
            lbl.pack(pady=20)
            return

        for cname in class_names:
            count = len(self.dm.get_all_students(cname))
            is_active = (cname == active)
            
            btn_text = f"  {cname}  ({count})"
            btn = ctk.CTkButton(
                self.class_scroll,
                text=btn_text,
                anchor="w",
                height=32,
                corner_radius=6,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold" if is_active else "normal"),
                fg_color="#0067c0" if is_active else "#202020",
                hover_color="#005fb8" if is_active else "#2b2b2b",
                text_color="#ffffff" if is_active else "#cccccc",
                command=lambda cn=cname: self._select_class(cn)
            )
            btn.pack(fill="x", pady=2)

    def _select_class(self, class_name):
        self.dm.set_active_class(class_name)
        self.refresh_all()

    def refresh_roster(self):
        active = self.dm.get_active_class()
        classes = self.dm.get_class_names()

        for widget in self.roster_scroll.winfo_children():
            widget.destroy()

        if not classes or not active:
            self.current_class_title.configure(text="Sorufelek'e Hoş Geldiniz")
            self.card_total._val_label.configure(text="0")
            self.card_picked._val_label.configure(text="0")
            self.card_remaining._val_label.configure(text="0")

            welcome_frame = ctk.CTkFrame(self.roster_scroll, fg_color="transparent")
            welcome_frame.pack(expand=True, fill="both", pady=40)

            w_title = ctk.CTkLabel(
                welcome_frame,
                text="Başlamak İçin Yeni Bir Sınıf Tanımlayınız",
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                text_color="#ffffff"
            )
            w_title.pack(pady=(10, 6))

            w_desc = ctk.CTkLabel(
                welcome_frame,
                text="Sol paneldeki 'Yeni Sınıf Tanımla' butonuna basarak ilk sınıfınızı oluşturabilir,\nardından e-Okul veya Excel'den öğrenci listenizi aktarabilirsiniz.",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color="#888888",
                justify="center"
            )
            w_desc.pack(pady=(0, 16))

            create_first_btn = ctk.CTkButton(
                welcome_frame,
                text="➕ İlk Sınıfınızı Tanımlayın",
                height=36,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                fg_color="#0067c0",
                hover_color="#005fb8",
                command=self._prompt_add_class
            )
            create_first_btn.pack()
            return

        self.current_class_title.configure(text=f"{active} Sınıfı")

        all_students = self.dm.get_all_students(active)
        picked_set = set(self.dm.get_picked_students(active))
        exempt_set = set(self.dm.get_exempt_students(active))
        remaining = [s for s in all_students if s not in picked_set and s not in exempt_set]

        self.card_total._val_label.configure(text=str(len(all_students)))
        self.card_picked._val_label.configure(text=str(len(picked_set)))
        self.card_remaining._val_label.configure(text=str(len(remaining)))

        filtered = [
            (idx + 1, s) for idx, s in enumerate(all_students)
            if not self.search_filter or self.search_filter in s.lower()
        ]

        if not filtered:
            msg = "Sınıfta henüz öğrenci kaydı yok. Yukarıdaki 'Toplu Liste Aktarımı' butonunu kullanabilirsiniz." if not all_students else "Arama kriterine uygun öğrenci bulunamadı."
            lbl = ctk.CTkLabel(
                self.roster_scroll,
                text=msg,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color="#888888",
                justify="center"
            )
            lbl.pack(pady=35)
            return

        for original_num, name in filtered:
            status = self.dm.get_student_status(name, active)
            
            row = ctk.CTkFrame(
                self.roster_scroll,
                fg_color="#202020" if status == "remaining" else "#181818",
                corner_radius=6,
                border_width=1,
                border_color="#2b2b2b" if status == "remaining" else "#333333"
            )
            row.pack(fill="x", padx=4, pady=2)

            num_lbl = ctk.CTkLabel(
                row,
                text=f"{original_num:02d}",
                width=32,
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color="#777777"
            )
            num_lbl.pack(side="left", padx=(6, 2), pady=4)

            name_lbl = ctk.CTkLabel(
                row,
                text=name,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold" if status == "remaining" else "normal"),
                text_color="#ffffff" if status == "remaining" else ("#b0b0b0" if status == "picked" else "#ffb74d")
            )
            name_lbl.pack(side="left", padx=6, pady=4)

            if status == "picked":
                badge_text = "Soru Yöneltildi"
                badge_fg = "#2a2a2a"
                badge_hover = "#383838"
                badge_tc = "#b0b0b0"
            elif status == "exempt":
                badge_text = "Muaf (Devamsız)"
                badge_fg = "#382a17"
                badge_hover = "#4a3820"
                badge_tc = "#ffb74d"
            else:
                badge_text = "Sırada"
                badge_fg = "#1b3a2b"
                badge_hover = "#234a37"
                badge_tc = "#81c784"

            badge = ctk.CTkButton(
                row,
                text=badge_text,
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold" if status == "remaining" else "normal"),
                text_color=badge_tc,
                fg_color=badge_fg,
                hover_color=badge_hover,
                corner_radius=4,
                height=22,
                width=110,
                command=lambda s=name: self._cycle_student_status(s)
            )
            badge.pack(side="right", padx=(4, 6), pady=4)

            del_btn = ctk.CTkButton(
                row,
                text="✕",
                width=22,
                height=22,
                font=ctk.CTkFont(size=11),
                fg_color="transparent",
                hover_color="#3a1c1c",
                text_color="#888888",
                command=lambda s=name: self._delete_student(s)
            )
            del_btn.pack(side="right", padx=2, pady=4)

        spacer = ctk.CTkFrame(self.roster_scroll, height=30, fg_color="transparent")
        spacer.pack(fill="x", pady=(0, 15))

    # --- İŞLEMLER ---
    def _prompt_add_class(self):
        dialog = ctk.CTkInputDialog(text="Tanımlanacak sınıf adı (Örn: 9-A, 10-B, 11-F):", title="Yeni Sınıf Tanımlama")
        name = dialog.get_input()
        if name:
            success, msg = self.dm.add_class(name)
            if success:
                self.refresh_all()
            else:
                messagebox.showerror("Hata", msg)

    def _prompt_rename_class(self):
        active = self.dm.get_active_class()
        if not active:
            messagebox.showinfo("Bilgilendirme", "Lütfen önce bir sınıf seçiniz.")
            return
        dialog = ctk.CTkInputDialog(text=f"'{active}' için güncel sınıf adı:", title="Sınıf Adını Güncelle")
        new_name = dialog.get_input()
        if new_name:
            success, msg = self.dm.rename_class(active, new_name)
            if success:
                self.refresh_all()
            else:
                messagebox.showerror("Hata", msg)

    def _confirm_delete_class(self):
        active = self.dm.get_active_class()
        if not active:
            return
        res = messagebox.askyesno(
            "Silme Onayı",
            f"'{active}' sınıfını ve bu sınıfa ait tüm öğrenci kayıtlarını sistemden silmek istediğinizi onaylıyor musunuz?"
        )
        if res:
            self.dm.delete_class(active)
            self.refresh_all()

    def _add_single_student(self):
        active = self.dm.get_active_class()
        if not active:
            messagebox.showinfo("Bilgilendirme", "Lütfen önce bir sınıf tanımlayınız.")
            return

        name = self.single_entry.get().strip()
        if not name:
            return
        success, msg = self.dm.add_student(name)
        if success:
            self.single_entry.delete(0, "end")
            self.refresh_all()
        else:
            messagebox.showwarning("Uyarı", msg)

    def _delete_student(self, student_name):
        self.dm.remove_student(student_name)
        self.refresh_all()

    def _cycle_student_status(self, student_name):
        self.dm.cycle_student_status(student_name)
        self.refresh_all()

    def _confirm_clear_roster(self):
        active = self.dm.get_active_class()
        if not active:
            return
        res = messagebox.askyesno(
            "Listeyi Temizleme Onayı",
            f"'{active}' sınıfındaki tüm öğrenci kayıtlarını silmek istediğinizi onaylıyor musunuz?"
        )
        if res:
            self.dm.set_students_list([])
            self.refresh_all()

    def _confirm_reset_cycle(self):
        active = self.dm.get_active_class()
        if not active:
            return
        res = messagebox.askyesno(
            "Soru Turunu Sıfırlama Onayı",
            f"'{active}' sınıfı için soru çözüm sırasını baştan başlatmak istediğinizi onaylıyor musunuz?"
        )
        if res:
            self.dm.reset_picked()
            self.refresh_all()

    def _open_history_dialog(self):
        active = self.dm.get_active_class()
        if not active:
            messagebox.showinfo("Bilgilendirme", "Lütfen önce bir sınıf seçiniz.")
            return

        history = self.dm.get_history(active)

        modal = ctk.CTkToplevel(self)
        modal.title(f"Seçim Geçmişi - {active}")
        modal.geometry("440x480")
        modal.resizable(False, False)
        modal.grab_set()

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        modal.geometry(f"440x480+{(screen_w - 440)//2}+{(screen_h - 480)//2}")

        head_lbl = ctk.CTkLabel(
            modal,
            text=f"{active} Sınıfı Ders İçi Soru Sırası Kaydı",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#ffffff"
        )
        head_lbl.pack(padx=16, pady=(16, 8), anchor="w")

        scroll = ctk.CTkScrollableFrame(modal, fg_color="#181818", corner_radius=6)
        scroll.pack(fill="both", expand=True, padx=16, pady=8)

        if not history:
            no_lbl = ctk.CTkLabel(scroll, text="Bu oturumda henüz soru yöneltilen öğrenci bulunmuyor.", text_color="#888888")
            no_lbl.pack(pady=40)
        else:
            for idx, item in enumerate(history, 1):
                row = ctk.CTkFrame(scroll, fg_color="#202020", height=32, corner_radius=4)
                row.pack(fill="x", pady=2)
                row.pack_propagate(False)

                num_l = ctk.CTkLabel(row, text=f"{idx:02d}.", width=30, font=ctk.CTkFont(size=10), text_color="#777777")
                num_l.pack(side="left", padx=4)

                name_l = ctk.CTkLabel(row, text=item.get("student", ""), font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#ffffff")
                name_l.pack(side="left", padx=6)

                time_l = ctk.CTkLabel(row, text=item.get("timestamp", ""), font=ctk.CTkFont(size=10), text_color="#888888")
                time_l.pack(side="right", padx=8)

        btn_bar = ctk.CTkFrame(modal, fg_color="transparent")
        btn_bar.pack(fill="x", padx=16, pady=(4, 12))

        def _clear_h():
            self.dm.clear_history(active)
            modal.destroy()
            messagebox.showinfo("Bilgilendirme", "Seçim geçmişi temizlenmiştir.")

        clear_btn = ctk.CTkButton(
            btn_bar,
            text="Geçmişi Temizle",
            height=30,
            fg_color="#3a1c1c",
            hover_color="#542525",
            text_color="#f87171",
            command=_clear_h
        )
        clear_btn.pack(side="left")

        close_btn = ctk.CTkButton(
            btn_bar,
            text="Kapat",
            height=30,
            width=70,
            fg_color="#2b2b2b",
            hover_color="#383838",
            command=modal.destroy
        )
        close_btn.pack(side="right")

    def _open_bulk_paste_dialog(self):
        active = self.dm.get_active_class()
        if not active:
            messagebox.showinfo("Bilgilendirme", "Lütfen önce bir sınıf tanımlayınız.")
            return

        modal = ctk.CTkToplevel(self)
        modal.title(f"Toplu Liste Aktarımı - {active}")
        modal.geometry("520x460")
        modal.resizable(False, False)
        modal.grab_set()

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        modal.geometry(f"520x460+{(screen_w - 520)//2}+{(screen_h - 460)//2}")

        desc_lbl = ctk.CTkLabel(
            modal,
            text=(
                "e-Okul veya Excel üzerinden kopyalanan listeyi bu alana aktarabilirsiniz.\n"
                "Sıra numaraları ve gereksiz karakterler sistem tarafından otomatik temizlenir."
            ),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#888888",
            justify="left"
        )
        desc_lbl.pack(padx=16, pady=(12, 6), anchor="w")

        textbox = ctk.CTkTextbox(
            modal,
            height=280,
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=6
        )
        textbox.pack(fill="both", expand=True, padx=16, pady=6)

        current_students = self.dm.get_all_students(active)
        if current_students:
            textbox.insert("1.0", "\n".join(current_students))

        btn_frame = ctk.CTkFrame(modal, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(6, 12))

        def _save():
            text = textbox.get("1.0", "end")
            parsed = self.dm.parse_bulk_text(text)
            if not parsed:
                messagebox.showwarning("Uyarı", "Geçerli bir öğrenci kaydı tespit edilemedi.", parent=modal)
                return
            self.dm.set_students_list(parsed, active)
            modal.destroy()
            self.refresh_all()
            messagebox.showinfo("İşlem Başarılı", f"{len(parsed)} adet öğrenci kaydı sisteme aktarılmıştır.")

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Kaydet ve Aktar",
            height=34,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#107c41",
            hover_color="#0b5a2f",
            command=_save
        )
        save_btn.pack(side="right", padx=(6, 0))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="İptal",
            height=34,
            width=70,
            fg_color="#2b2b2b",
            hover_color="#383838",
            command=modal.destroy
        )
        cancel_btn.pack(side="right")
