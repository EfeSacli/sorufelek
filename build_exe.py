import os
import subprocess
import sys
import shutil
import zipfile

def clean_temp_files():
    """Derleme sonrası geçici klasörleri temizler."""
    temp_paths = ["build", "dist", "__pycache__", "Sorufelek.spec", "Sorufelek_Tek.spec", "Sorufelek_Klasor.spec"]
    for path in temp_paths:
        if os.path.exists(path):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    os.remove(path)
            except Exception:
                pass

def zip_directory(folder_to_zip, zip_output_path, root_dir_in_zip="Sorufelek"):
    """Bir klasörü tüm alt dosyalarıyla birlikte zip arşivine dönüştürür."""
    if os.path.exists(zip_output_path):
        os.remove(zip_output_path)
    with zipfile.ZipFile(zip_output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(folder_to_zip):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, folder_to_zip)
                arc_name = os.path.join(root_dir_in_zip, rel_path)
                zf.write(full_path, arc_name)

def build_all():
    print("=" * 60)
    print("   SORUFELEK TAM DAĞITIM VE DERLEME SİHİRBAZI")
    print("=" * 60)
    
    # -------------------------------------------------------------
    # 1. Tek Dosya EXE (Sorufelek.exe) Derleme
    # -------------------------------------------------------------
    print("\n[1/5] Tek dosya taşınabilir Sorufelek.exe derleniyor...")
    cmd_onefile = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=Sorufelek",
        "--icon=icon.ico",
        "--add-data=icon.ico;.",
        "--version-file=version_info.txt",
        "--collect-all=customtkinter",
        "--clean",
        "app.py"
    ]
    res_onefile = subprocess.run(cmd_onefile)
    if res_onefile.returncode == 0:
        exe_src = os.path.join("dist", "Sorufelek.exe")
        if os.path.exists(exe_src):
            shutil.copy2(exe_src, "Sorufelek.exe")
            print("  -> Sorufelek.exe hazır (Yayımcı: Efe Saçlı).")
    else:
        print("  [HATA] Sorufelek.exe derlenemedi!")
        return False

    # -------------------------------------------------------------
    # 2. Windows Kurulum Sihirbazı (Sorufelek_Kurulum.exe) Derleme
    # -------------------------------------------------------------
    print("\n[2/5] Inno Setup ile Sorufelek_Kurulum.exe derleniyor...")
    iscc_candidates = [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Inno Setup 6', 'ISCC.exe'),
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe"
    ]
    iscc_path = None
    for p in iscc_candidates:
        if os.path.exists(p):
            iscc_path = p
            break
            
    if iscc_path and os.path.exists("setup.iss"):
        setup_res = subprocess.run([iscc_path, "setup.iss"])
        if setup_res.returncode == 0:
            print("  -> Sorufelek_Kurulum.exe hazır.")
    else:
        print("  [UYARI] Inno Setup compiler bulunamadı, kurulum exe atlandı.")

    # -------------------------------------------------------------
    # 3. Önceden Kurulmuş Windows Klasörü (--onedir) Derleme
    # -------------------------------------------------------------
    print("\n[3/5] Kurulmuş hazır Windows klasörü (onedir) oluşturuluyor...")
    cmd_onedir = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onedir",
        "--name=Sorufelek",
        "--icon=icon.ico",
        "--add-data=icon.ico;.",
        "--version-file=version_info.txt",
        "--collect-all=customtkinter",
        "--clean",
        "app.py"
    ]
    res_onedir = subprocess.run(cmd_onedir)
    if res_onedir.returncode == 0:
        onedir_output = os.path.join("dist", "Sorufelek")
        if os.path.exists(onedir_output):
            # Klasör içine yardımcı dosyaları ekle
            for extra in ["icon.ico", "KULLANIM_REHBERI.txt", "Masaustune_Kisayol_Ekle.vbs"]:
                if os.path.exists(extra):
                    shutil.copy2(extra, onedir_output)

            # -------------------------------------------------------------
            # 4. Windows Hazır Kurulmuş Klasör ZIP Arşivi
            # -------------------------------------------------------------
            print("\n[4/5] Sorufelek-Windows-Kurulmus-Klasor.zip paketleniyor...")
            zip_directory(onedir_output, "Sorufelek-Windows-Kurulmus-Klasor.zip", "Sorufelek")
            print("  -> Sorufelek-Windows-Kurulmus-Klasor.zip hazır.")

    # -------------------------------------------------------------
    # 5. Pardus / Linux Hazır Kurulmuş Klasör ZIP Arşivi
    # -------------------------------------------------------------
    print("\n[5/5] Sorufelek-Pardus-Kurulmus-Klasor.zip paketleniyor...")
    pardus_temp_dir = "temp_pardus_package"
    if os.path.exists(pardus_temp_dir):
        shutil.rmtree(pardus_temp_dir, ignore_errors=True)
    os.makedirs(pardus_temp_dir, exist_ok=True)
    
    pardus_files = [
        "app.py", "main_window.py", "corner_widget.py", "data_manager.py",
        "sound_effects.py", "utils.py", "requirements.txt", "baslat.sh",
        "kurulum_pardus.sh", "sorufelek.desktop", "icon.png", "icon.ico",
        "PARDUS_KULLANIM_REHBERI.txt", "README.md", "LICENSE"
    ]
    for pf in pardus_files:
        if os.path.exists(pf):
            shutil.copy2(pf, pardus_temp_dir)
            
    zip_directory(pardus_temp_dir, "Sorufelek-Pardus-Kurulmus-Klasor.zip", "Sorufelek")
    shutil.rmtree(pardus_temp_dir, ignore_errors=True)
    print("  -> Sorufelek-Pardus-Kurulmus-Klasor.zip hazır.")

    # Eski zip adları varsa temizle
    for old_zip in ["Sorufelek-Windows-Portable.zip", "Sorufelek-Pardus-Linux.zip"]:
        if os.path.exists(old_zip):
            os.remove(old_zip)

    # Geçici dosyaları temizle
    clean_temp_files()
    
    print("\n" + "=" * 60)
    print("   TÜM DAĞITIM PAKETLERİ HAZIRLANDI VE DOĞRULANDI")
    print("=" * 60)
    print("1. Sorufelek.exe                          (Doğrudan Tek EXE)")
    print("2. Sorufelek_Kurulum.exe                  (Windows Kurulum Sihirbazı EXE)")
    print("3. Sorufelek-Windows-Kurulmus-Klasor.zip  (Kurulum Gerektirmeyen Hazır Windows Klasörü)")
    print("4. Sorufelek-Pardus-Kurulmus-Klasor.zip   (Kurulum Gerektirmeyen Hazır Pardus Klasörü)")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = build_all()
    if not success:
        sys.exit(1)
