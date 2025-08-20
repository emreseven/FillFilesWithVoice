# 🎯 Sesli Belge Doldurma Sistemi (Birleşik Versiyon)

Bu proje, **voice.py** ve **app2.py** projelerinin en iyi özelliklerini birleştirerek oluşturulmuş gelişmiş bir sesli belge doldurma sistemidir.

## ✨ Özellikler

### 🔥 Birleşik Güçlü Özellikler

- **🎤 Çoklu Mikrofon Desteği**: Hem `streamlit-mic-recorder` hem de `st-audiorec` desteklenir
- **🧠 AI Destekli Analiz**: OpenAI Whisper + GPT ile akıllı bilgi çıkarma
- **📁 Güçlü Session Yönetimi**: Öğrenci bilgilerini otomatik kaydetme ve arama
- **🔍 Akıllı Placeholder Sistemi**: Word şablonlarındaki tüm alanları otomatik bulma
- **👁️ Canlı Önizleme**: Değişiklikleri anında görme
- **📝 Çoklu Şablon Desteği**: Birden fazla Word şablonunu aynı anda işleme
- **🔄 Çakışma Tespiti**: Yeni veriler eskilerle çakıştığında uyarı
- **📊 Otomatik İsimlendirme**: Session'ları öğrenci bilgilerine göre adlandırma

### 🎯 Voice.py'den Alınan Özellikler

- Gelişmiş session yönetimi
- Placeholder bağlam analizi
- Canlı önizleme sistemi
- Öğrenci arama ve filtreleme
- Çakışma tespiti ve veri birleştirme

### 🧩 App2.py'den Alınan Özellikler

- Sağlam tarih işleme sistemi
- st_audiorec mikrofon desteği
- Belge özelinde alan kontrolleri
- İşbu tarih/saat yönetimi
- Türkçe tarih formatları desteği

## 🚀 Kurulum

### 1. Gereksinimleri Kurun

```bash
pip install -r unified_requirements.txt
```

### 2. Şablon Klasörünü Oluşturun

```bash
mkdir templates
```

Word şablon dosyalarınızı `templates/` klasörüne koyun. Şablonlarda `{placeholder_adi}` formatında alanlar kullanın.

### 3. Uygulamayı Çalıştırın

```bash
streamlit run unified_app.py
```

## 📋 Kullanım

### 1. Session Yönetimi
- Ana sayfada **"Yeni Session Başlat"** ile yeni öğrenci session'ı oluşturun
- Mevcut session'ları arayın ve düzenleyin
- Öğrenci bilgilerine göre otomatik isimlendirme

### 2. Şablon Seçimi
- `templates/` klasöründeki Word şablonlarını seçin
- Sistem otomatik olarak placeholder'ları tespit eder

### 3. Ses Kaydı ve Analiz
- **OpenAI API Key** girin
- Mikrofon ile ses kaydı yapın
- **"Analiz Et"** butonu ile AI analizi başlatın

### 4. Bilgi Düzenleme
- AI'ın çıkardığı bilgileri kontrol edin ve düzenleyin
- Eksik alanları manuel olarak doldurun
- Session'a otomatik kayıt

### 5. Belge Oluşturma
- **"Tüm Belgeleri Oluştur"** ile Word dosyalarını hazırlayın
- Hazır belgeleri indirin

## 🔧 Teknik Detaylar

### Dosya Yapısı

```
unified_app.py              # Ana uygulama
local_session_manager.py    # Session yönetimi
unified_requirements.txt    # Gereksinimler
templates/                  # Word şablonları
  ├── sablon1.docx
  └── sablon2.docx
sessions/                   # Session verileri (otomatik oluşur)
  ├── sessions_index.json
  ├── sess_12345678.json
  └── ...
```

### API Gereksinimleri

- **OpenAI API Key**: Whisper (ses-metin) ve GPT (analiz) için gerekli
- İnternet bağlantısı: API çağrıları için

### Desteklenen Dosya Formatları

- **Giriş**: WAV, MP3, M4A ses dosyaları
- **Şablon**: DOCX Word belgeleri
- **Çıkış**: DOCX Word belgeleri

## 🔒 Veri Güvenliği

- Tüm session verileri yerel olarak `sessions/` klasöründe saklanır
- Ses dosyaları geçici olarak oluşturulur ve işlem sonrası silinir
- API anahtarları session boyunca bellekte tutulur (kalıcı depolanmaz)

## 🛠️ Sorun Giderme

### Mikrofon Sorunları

Eğer mikrofon kütüphaneleri kurulamazsa:

```bash
# Sadece birini kurun
pip install streamlit-mic-recorder
# VEYA
pip install st-audiorec
```

### Python Sürüm Uyumluluğu

- **Python 3.9+**: Tüm özellikler desteklenir
- **Python 3.8**: `backports.zoneinfo` paketi gerekir

### Şablon Sorunları

- Placeholder'lar `{alan_adi}` formatında olmalı
- Türkçe karakter kullanımı desteklenir
- Boşluk yerine alt çizgi (`_`) kullanın

## 🎨 Arayüz Özellikleri

### Basit ve Kullanıcı Dostu
- **Temiz tasarım**: Karmaşık menüler yerine sade arayüz
- **Adım adım rehber**: Her işlem için açık talimatlar
- **Görsel geri bildirim**: İşlem durumu ve sonuçları net gösterim
- **Hızlı erişim**: En çok kullanılan özellikler ön planda

### Responsive Tasarım
- **Kolon düzeni**: Ekran boyutuna göre uyum
- **Mobil uyumluluk**: Tablet ve mobil cihazlarda çalışır
- **Hızlı yükleme**: Optimize edilmiş bileşenler

## 📈 Gelecek Özellikler

- [ ] Toplu belge işleme
- [ ] Excel şablon desteği
- [ ] Ses dosyası yükleme
- [ ] Çoklu dil desteği
- [ ] Bulut session senkronizasyonu

## 🤝 Katkıda Bulunma

Bu proje, voice.py ve app2.py projelerinin birleşimi olarak oluşturulmuştur. Geliştirmeler ve öneriler için issue açabilirsiniz.

## 📄 Lisans

Bu proje, orijinal projelerin lisanslarına uygun olarak geliştirilmiştir.

---

**🎯 Sesli Belge Doldurma Sistemi** - AI destekli, kullanıcı dostu, güçlü belge otomasyonu!
