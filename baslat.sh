#!/bin/bash
# ========================================================================
# Sorufelek - Ders İçi Soru ve Kura Sistemi (Pardus / Linux Başlatıcı)
# Geliştirici: Efe Saçlı
# ========================================================================

# Scriptin bulunduğu dizine geç
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=== Sorufelek Başlatılıyor (Pardus / Linux) ==="

# Python 3 kontrolü
if ! command -v python3 &> /dev/null; then
    echo "[HATA] Python 3 sisteminizde bulunamadı!"
    echo "Lütfen Pardus Yazılım Merkezi'nden veya terminalden yükleyin:"
    echo "sudo apt update && sudo apt install -y python3 python3-pip python3-tk"
    exit 1
fi

# Tkinter kontrolü (Pardus/Debian'da python3-tk ayrı paket olabilir)
python3 -c "import tkinter" &> /dev/null
if [ $? -ne 0 ]; then
    echo "[BİLGİ] Tkinter grafik kütüphanesi eksik, otomatik kuruluyor..."
    if command -v pkexec &> /dev/null; then
        pkexec apt install -y python3-tk
    elif command -v sudo &> /dev/null; then
        sudo apt install -y python3-tk
    else
        echo "Lütfen şu komutu çalıştırınız: sudo apt install -y python3-tk"
    fi
fi

# CustomTkinter ve Pillow kütüphane kontrolü
python3 -c "import customtkinter; import PIL" &> /dev/null
if [ $? -ne 0 ]; then
    echo "[BİLGİ] Gerekli Python kütüphaneleri (customtkinter, Pillow) kuruluyor..."
    python3 -m pip install -r requirements.txt --user --break-system-packages 2>/dev/null || \
    python3 -m pip install -r requirements.txt --user 2>/dev/null || \
    python3 -m pip install -r requirements.txt
fi

# Uygulamayı başlat
python3 app.py "$@"
