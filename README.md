# 🎯 Sorufelek - Ders İçi Soru ve Kura Sistemi

[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Pardus%20%28Linux%29-blue.svg)](https://github.com/EfeSacli/sorufelek)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE)
[![Geliştirici](https://img.shields.io/badge/Geliştirici-Efe%20Saçlı-purple.svg)](https://github.com/EfeSacli)

**Sorufelek**, öğretmenlerin ders esnasında öğrencilerine adil, sistematik ve dikkat dağıtmayan bir şekilde soru yöneltmelerini sağlayan modern, kurumsal bir masaüstü uygulamasıdır. 

Hem **Windows (10 / 11)** hem de **Pardus (MEB Fatih Akıllı Tahtaları)** sistemlerinde sorunsuz çalışacak şekilde tasarlanmıştır.

---

## ✨ Temel Özellikler

- 🏫 **Esnek Sınıf Yönetimi:** e-Okul veya Excel listelerinden tek tıkla toplu öğrenci ekleme.
- 🎲 **Adil Kura Motoru:** Bir öğrenciye soru sorulduğunda, liste yenilenene kadar aynı öğrenci tekrar gelmez. Son öğrenci ekranda kalır ve tur bitiminde liste yenileme önerilir.
- 📌 **Ders İçi HUD (Köşe) Modu:** Sunum yaparken veya PDF/soru çözerken ekranı kapatmaz. Sağ üst köşede şık, minimalist bir widget olarak kalır.
- 🔒 **Kalıcı Öncelik (Always-on-Top):** PDF okuyucular veya tam ekran sunumlar arkasına düşmez; her zaman en üstte görünür.
- ⌨️ **Klavye Kısayolları:** 
  - `BOŞLUK (Space)` veya `ENTER`: Yeni öğrenci seç / Kura başlat
  - `CTRL + Z`: Son seçimi geri al
  - `ESC`: Tam yönetim paneline geri dön
- 📝 **3 Kademeli Durum:** `Sırada`, `Soru Yöneltildi` veya devamsızlar için `Muaf`.
- 📴 **%100 Çevrimdışı ve Güvenli:** Hiçbir internet bağlantısı gerektirmez, veriler yerel bilgisayarınızda saklanır.

---

## 🚀 İndirme ve Kullanım Seçenekleri (Sürüm 1.0)

Tüm resmi sürümleri sağ taraftaki **[Releases](https://github.com/EfeSacli/sorufelek/releases)** sekmesinden indirebilirsiniz:

### 🪟 1. Windows Sürümleri
* **Kurulumlu Sürüm (`Sorufelek-Windows-Kurulumlu-v1.0.exe`):**
  - Dosyaları `C:\Program Files\Sorufelek` konumuna kurar.
  - Masaüstünüze ve Başlat menünüze otomatik kısayol ekler.
  - İsteğe bağlı görev çubuğuna sabitleme ve Denetim Masası kaldırma (uninstaller) desteği sunar.
* **Kurulumsuz Taşınabilir Tek EXE (`Sorufelek-Windows-Kurulumsuz-v1.0.exe`):**
  - Kurulum yapmadan doğrudan USB bellekten veya masaüstünden tek tıkla çalıştırmak isteyenler için tek dosyadır.
* **Kurulumsuz Hazır Klasör ZIP (`Sorufelek-Windows-Kurulumsuz-v1.0.zip`):**
  - Kurulum izinleri engellenen veya kısıtlı okul bilgisayarları için en güvenli ve en hızlı çözümdür.
  - Zipten çıkarıp `Sorufelek.exe`ye basarak anında (0.2 sn) açabilirsiniz.
  - Klasördeki `Masaustune_Kisayol_Ekle.vbs` dosyasına çift tıklayarak tek tıkla masaüstünüze logolu kısayol ekleyebilirsiniz.

### 🐧 2. Pardus ve Linux Sürümleri (MEB Fatih Akıllı Tahtalar)
* **Kurulumlu Sürüm (`Sorufelek-Pardus-Kurulumlu-v1.0.deb`):**
  - Pardus / Debian sistemler için resmi `.deb` paketidir.
  - İndirip çift tıklayarak **Pardus Paket Kurucu** ile tek tıkla kurulur.
  - Pardus Başlat Menüsü > Eğitim kategorisine ve Masaüstüne otomatik eklenir.
* **Kurulumsuz Sürüm (`Sorufelek-Pardus-Kurulumsuz-v1.0.zip`):**
  - Zipten çıkartıp klasör içindeki `baslat.sh` dosyasına çift tıklayarak hiçbir kurulum yapmadan doğrudan çalıştırabilirsiniz.

---

## 🔒 Güvenlik ve Gizlilik

- **%100 Yerel Veri Saklama:** Sorufelek hiçbir veriyi internete göndermez veya depolamaz. Tüm sınıf ve öğrenci verileri yalnızca kendi bilgisayarınızda şifrelenmiş/güvenli olarak saklanır.
- **Çevrimdışı Çalışma:** Program hiçbir internet bağlantısına ihtiyaç duymaz, akıllı tahtalarda ve kişisel bilgisayarlarda tam performansla çalışır.

---

## 📄 Lisans ve Telif Hakkı

Geliştirici: **Efe Saçlı**  
Telif Hakkı © 2026 Efe Saçlı. Tüm hakları saklıdır.  
Sorufelek, öğretmenler ve eğitim kurumları için ücretsiz bir masaüstü yazılımıdır.

