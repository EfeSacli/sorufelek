import json
import os
import sys
import re
import random
from datetime import datetime

class DataManager:
    """
    Sorufelek - Veritabanı ve Sınıf Yönetim Modülü.
    Otomatik sınıf oluşturmaz; öğretmen kendi sınıflarını tanımlar.
    Kura döngülerini, devamsızlık durumlarını ve ders geçmişini yönetir.
    """
    def __init__(self):
        # Sorufelek veri dizini (Windows: %APPDATA%/Sorufelek, Linux/Pardus: ~/.config/Sorufelek)
        if sys.platform == 'win32':
            base_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
        else:
            base_dir = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
        appdata_dir = os.path.join(base_dir, 'Sorufelek')
        os.makedirs(appdata_dir, exist_ok=True)
        self.file_path = os.path.join(appdata_dir, 'sorufelek_verileri.json')
        
        # Eski veri dosyası varsa geriye dönük kontrol
        old_appdata = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'OgrenciSecici', 'ogrenci_verileri.json')
        if not os.path.exists(self.file_path) and os.path.exists(old_appdata):
            try:
                import shutil
                shutil.copy2(old_appdata, self.file_path)
            except Exception:
                pass

        self.local_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sorufelek_verileri.json')
        
        self.data = {
            "active_class": "",
            "settings": {
                "sound_enabled": True,
                "always_on_top": True,
                "opacity": 1.0,
                "corner_position": "top_right",
                "animation_duration_ms": 1100,
                "theme": "dark"
            },
            "classes": {}
        }
        self.load_data()

    def _get_default_classes(self):
        # Otomatik sınıf üretilmez; öğretmen kendi sınıflarını oluşturur
        return {}

    def load_data(self):
        target = self.file_path
        if not os.path.exists(target) and os.path.exists(self.local_file_path):
            target = self.local_file_path

        if os.path.exists(target):
            try:
                with open(target, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict) and "classes" in loaded:
                        self.data = loaded
            except Exception as e:
                print(f"Veri yükleme hatası: {e}")
                self.data["classes"] = {}
        else:
            self.data["classes"] = {}
            self.save_data()

        # Otomatik eklenen eski varsayılan sınıfları (9-B, 10-A mock data) temizle
        mock_students_sample = {"Ada Korkmaz", "Bora Çakır", "Ahmet Yılmaz", "Ayşe Kaya"}
        to_remove = []
        for cname, cdata in self.data.get("classes", {}).items():
            st_set = set(cdata.get("students", []))
            # Eğer sadece mock öğrencilerden oluşuyorsa kaldır
            if st_set and st_set.issubset(mock_students_sample | {"Doruk Yıldırım", "Ege Çiftçi", "Irmak Aslan", "Kuzey Tunç", "Lara Tekin", "Miraç Özdemir", "Nehir Kaplan", "Rüzgar Çelebi", "Yağmur Akın"}):
                to_remove.append(cname)
        for cname in to_remove:
            del self.data["classes"][cname]

        # Alt alanları doğrula
        for cname, cdata in self.data.get("classes", {}).items():
            if "exempt" not in cdata:
                cdata["exempt"] = []
            if "history" not in cdata:
                cdata["history"] = []

        active = self.data.get("active_class")
        classes = self.get_class_names()
        if not active or active not in self.data["classes"]:
            self.data["active_class"] = classes[0] if classes else ""
        
        self.save_data()

    def save_data(self):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Veri kaydetme hatası: {e}")

    # --- Sınıf Yönetimi ---
    def get_class_names(self):
        return sorted(list(self.data["classes"].keys()))

    def get_active_class(self):
        active = self.data.get("active_class")
        if active not in self.data["classes"]:
            classes = self.get_class_names()
            self.data["active_class"] = classes[0] if classes else ""
        return self.data["active_class"]

    def set_active_class(self, class_name):
        if class_name in self.data["classes"]:
            self.data["active_class"] = class_name
            self.save_data()

    def add_class(self, class_name):
        class_name = class_name.strip()
        if not class_name:
            return False, "Sınıf adı boş bırakılamaz."
        if class_name in self.data["classes"]:
            return False, f"'{class_name}' adına sahip bir sınıf kaydı sistemde zaten mevcuttur."
        
        self.data["classes"][class_name] = {
            "students": [],
            "picked": [],
            "exempt": [],
            "history": []
        }
        self.data["active_class"] = class_name
        self.save_data()
        return True, "Sınıf kaydı başarıyla oluşturulmuştur."

    def delete_class(self, class_name):
        if class_name in self.data["classes"]:
            del self.data["classes"][class_name]
            names = self.get_class_names()
            self.data["active_class"] = names[0] if names else ""
            self.save_data()
            return True
        return False

    def rename_class(self, old_name, new_name):
        new_name = new_name.strip()
        if not new_name:
            return False, "Sınıf adı boş bırakılamaz."
        if old_name not in self.data["classes"]:
            return False, "Belirtilen sınıf sistemde bulunamadı."
        if new_name != old_name and new_name in self.data["classes"]:
            return False, f"'{new_name}' adına sahip bir sınıf kaydı zaten mevcuttur."

        self.data["classes"][new_name] = self.data["classes"].pop(old_name)
        if self.data.get("active_class") == old_name:
            self.data["active_class"] = new_name
        self.save_data()
        return True, "Sınıf bilgisi güncellenmiştir."

    # --- Öğrenci ve Durum Yönetimi ---
    def get_all_students(self, class_name=None):
        cname = class_name or self.get_active_class()
        if not cname or cname not in self.data["classes"]:
            return []
        return self.data["classes"][cname].get("students", [])

    def get_picked_students(self, class_name=None):
        cname = class_name or self.get_active_class()
        if not cname or cname not in self.data["classes"]:
            return []
        return self.data["classes"][cname].get("picked", [])

    def get_exempt_students(self, class_name=None):
        cname = class_name or self.get_active_class()
        if not cname or cname not in self.data["classes"]:
            return []
        return self.data["classes"][cname].get("exempt", [])

    def get_remaining_students(self, class_name=None):
        cname = class_name or self.get_active_class()
        if not cname or cname not in self.data["classes"]:
            return []
        all_s = self.get_all_students(cname)
        picked_s = set(self.get_picked_students(cname))
        exempt_s = set(self.get_exempt_students(cname))
        return [s for s in all_s if s not in picked_s and s not in exempt_s]

    def add_student(self, student_name, class_name=None):
        cname = class_name or self.get_active_class()
        student_name = student_name.strip()
        if not student_name or not cname or cname not in self.data["classes"]:
            return False, "Geçersiz öğrenci kaydı veya sınıf seçimi."
        
        students = self.data["classes"][cname]["students"]
        if student_name in students:
            return False, f"'{student_name}' isimli öğrenci bu sınıfta kayıtlıdır."
        
        students.append(student_name)
        self.save_data()
        return True, "Öğrenci kaydı başarıyla eklendi."

    def remove_student(self, student_name, class_name=None):
        cname = class_name or self.get_active_class()
        if not cname or cname not in self.data["classes"]:
            return False
        
        c = self.data["classes"][cname]
        for lst_key in ("students", "picked", "exempt"):
            if student_name in c.get(lst_key, []):
                c[lst_key].remove(student_name)
        
        self.save_data()
        return True

    def set_students_list(self, students_list, class_name=None):
        cname = class_name or self.get_active_class()
        if not cname or cname not in self.data["classes"]:
            return False
        
        unique_students = []
        for s in students_list:
            clean = s.strip()
            if clean and clean not in unique_students:
                unique_students.append(clean)
        
        c = self.data["classes"][cname]
        c["students"] = unique_students
        existing_set = set(unique_students)
        c["picked"] = [p for p in c.get("picked", []) if p in existing_set]
        c["exempt"] = [e for e in c.get("exempt", []) if e in existing_set]
        self.save_data()
        return True

    def parse_bulk_text(self, text):
        lines = text.strip().split('\n')
        parsed = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if '\t' in line:
                parts = [p.strip() for p in line.split('\t') if p.strip()]
                name_candidate = None
                for part in parts:
                    if not part.replace('.', '').replace('-', '').isdigit():
                        name_candidate = part
                        break
                if name_candidate:
                    line = name_candidate
                elif parts:
                    line = parts[-1]

            cleaned = re.sub(r'^\s*\d+[\.\-\)\:\s\t]+', '', line).strip()
            if not cleaned:
                cleaned = line.strip()
            
            cleaned = cleaned.strip('"\'')
            if cleaned and cleaned not in parsed:
                parsed.append(cleaned)
        return parsed

    # --- Kura Seçim Algoritması ---
    def pick_random(self, class_name=None):
        cname = class_name or self.get_active_class()
        remaining = self.get_remaining_students(cname)
        if not remaining:
            return None, True
        
        chosen = random.choice(remaining)
        c = self.data["classes"][cname]
        c["picked"].append(chosen)
        
        if "history" not in c:
            c["history"] = []
        c["history"].append({
            "student": chosen,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

        self.save_data()
        
        new_remaining_count = len(self.get_remaining_students(cname))
        return chosen, (new_remaining_count == 0)

    def undo_pick(self, class_name=None):
        cname = class_name or self.get_active_class()
        if not cname or cname not in self.data["classes"]:
            return None
        
        c = self.data["classes"][cname]
        picked = c.get("picked", [])
        if picked:
            undone = picked.pop()
            if c.get("history") and c["history"][-1].get("student") == undone:
                c["history"].pop()
            self.save_data()
            return undone
        return None

    def reset_picked(self, class_name=None):
        cname = class_name or self.get_active_class()
        if cname and cname in self.data["classes"]:
            self.data["classes"][cname]["picked"] = []
            self.save_data()
            return True
        return False

    def cycle_student_status(self, student_name, class_name=None):
        cname = class_name or self.get_active_class()
        if not cname or cname not in self.data["classes"]:
            return "remaining"
        
        c = self.data["classes"][cname]
        picked = c.setdefault("picked", [])
        exempt = c.setdefault("exempt", [])
        
        if student_name in picked:
            picked.remove(student_name)
            if student_name not in exempt:
                exempt.append(student_name)
            new_status = "exempt"
        elif student_name in exempt:
            exempt.remove(student_name)
            new_status = "remaining"
        else:
            if student_name not in picked:
                picked.append(student_name)
            new_status = "picked"

        self.save_data()
        return new_status

    def get_student_status(self, student_name, class_name=None):
        cname = class_name or self.get_active_class()
        if not cname or cname not in self.data["classes"]:
            return "remaining"
        c = self.data["classes"][cname]
        if student_name in c.get("picked", []):
            return "picked"
        if student_name in c.get("exempt", []):
            return "exempt"
        return "remaining"

    def get_history(self, class_name=None):
        cname = class_name or self.get_active_class()
        if not cname or cname not in self.data["classes"]:
            return []
        return self.data["classes"][cname].get("history", [])

    def clear_history(self, class_name=None):
        cname = class_name or self.get_active_class()
        if cname and cname in self.data["classes"]:
            self.data["classes"][cname]["history"] = []
            self.save_data()

    # --- Sistem Ayarları ---
    def get_setting(self, key, default=None):
        return self.data.get("settings", {}).get(key, default)

    def set_setting(self, key, value):
        if "settings" not in self.data:
            self.data["settings"] = {}
        self.data["settings"][key] = value
        self.save_data()
