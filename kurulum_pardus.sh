#!/bin/bash
# ========================================================================
# Sorufelek - Pardus / Linux Kolay Kurulum Betiği
# Geliştirici: Efe Saçlı
# ========================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "      SORUFELEK PARDUS / LINUX KURULUM SİHİRBAZI         "
echo "=========================================================="

INSTALL_DIR="$HOME/.local/share/sorufelek"
APP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
DESKTOP_DIR="$HOME/Masaüstü"

# Eğer Masaüstü klasörü yoksa Desktop dene
if [ ! -d "$DESKTOP_DIR" ]; then
    DESKTOP_DIR="$HOME/Desktop"
fi

echo "1. Dosyalar kopyalanıyor ($INSTALL_DIR)..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$APP_DIR"
mkdir -p "$ICON_DIR"

cp -r *.py *.png *.ico requirements.txt baslat.sh "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/baslat.sh"

echo "2. Uygulama ikonu yükleniyor..."
cp icon.png "$ICON_DIR/sorufelek.png"

echo "3. Menü kısayolu oluşturuluyor..."
cat << 'EOF' > "$APP_DIR/sorufelek.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Sorufelek
GenericName=Ders İçi Soru ve Kura Sistemi
Comment=Öğretmenler için adil, kompakt ve modern kura ve soru yöneltme sistemi
Exec=bash -c "$HOME/.local/share/sorufelek/baslat.sh"
Icon=sorufelek
Terminal=false
Categories=Education;Teaching;Utility;
StartupNotify=true
EOF

chmod +x "$APP_DIR/sorufelek.desktop"

# Masaüstüne kısayol oluştur
if [ -d "$DESKTOP_DIR" ]; then
    cp "$APP_DIR/sorufelek.desktop" "$DESKTOP_DIR/sorufelek.desktop"
    chmod +x "$DESKTOP_DIR/sorufelek.desktop"
    # GNOME / XFCE masaüstü güvenli işaretleme
    if command -v gio &> /dev/null; then
        gio set "$DESKTOP_DIR/sorufelek.desktop" metadata::trusted true 2>/dev/null || true
    fi
    echo "4. Masaüstü kısayolu eklendi ($DESKTOP_DIR)."
fi

echo ""
echo "=========================================================="
echo "  KURULUM BAŞARIYLA TAMAMLANDI!"
echo "  - Sorufelek artık Pardus Başlat Menüsü > Eğitim altında."
echo "  - Masaüstünüze Sorufelek kısayolu eklendi."
echo "=========================================================="
