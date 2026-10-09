# ⚙️ NASA IMS Bearing - Kestirimci Bakım & RUL Tahmini Projesi

Bu proje, **NASA / Intelligent Maintenance Systems (IMS)** Rulman Veri Setini kullanarak endüstriyel rulmanların titreşim sinyalleri üzerinden kestirimci bakım (predictive maintenance), anomali tespiti (anomaly detection), arıza teşhisi (fault diagnosis) ve kalan faydalı ömür (Remaining Useful Life - RUL) tahmini gerçekleştiren uçtan uca bir sistem sunar.

---

## 🚀 Proje Özellikleri

- 📁 **Modüler Dizin Yapısı:** `src/`, `data/`, `models/`, `dashboard/`, `results/`
- ⚡ **Sinyal İşleme & Özellik Çıkarımı:**
  - **Zaman Alanı:** RMS, Kurtosis, Skewness, Peak-to-Peak, Crest Factor, Shape Factor, Impulse Factor, Margin Factor.
  - **Frekans Alanı:** FFT spektrumu, spektral enerji, santroid, BPFO (236.4 Hz), BPFI (296.9 Hz), BSF (139.9 Hz), FTF (14.7 Hz) arıza frekansları.
- 📉 **Sağlık İndeksi (Health Index - HI):** PCA ve Mahalanobis mesafesi ile 1.0 (Sağlıklı) -> 0.0 (Kritik) arası sürekli sağlık metriği hesabı.
- 🤖 **Makine Öğrenmesi & Anomali Tespiti:**
  - Erken anomali tespiti için **Isolation Forest** & **One-Class SVM**.
  - RUL tahmini için **Random Forest Regressor** & **XGBoost**.
- 💻 **İnteraktif Web Dashboard (Streamlit):** Zaman akış simülatörü, canlı titreşim grafikleri, FFT frekans spektrumu ve anlık RUL tahmin ekranı.

---

## 📂 Dizin Yapısı

```
imsbearing/
│
├── data/
│   ├── raw/                  # NASA IMS ham ivmeölçer verileri (.txt)
│   └── processed/            # Çıkarılmış özellik matrisleri (.csv)
│
├── src/
│   ├── config.py             # Rulman geometrisi & frekans parametreleri
│   ├── data_loader.py        # İvmeölçer zaman serisi okuma modülü
│   ├── download_data.py      # Veri seti indirme / sentetik demo üretimi
│   ├── feature_extraction.py # Sinyal işleme & zaman/frekans alan özellikleri
│   ├── health_index.py       # HI & RUL etiketleme hesabı
│   └── models/
│       ├── anomaly_detector.py # Isolation Forest & OC-SVM modelleri
│       └── rul_predictor.py    # RUL tahmin modelleri
│
├── dashboard/
│   └── app.py                # Streamlit interaktif web uygulaması
│
├── models/                   # Eğitilmiş model ikili dosyaları (.joblib)
├── results/                  # Performans metrikleri (evaluation_metrics.csv)
├── requirements.txt          # Gerekli Python kütüphaneleri
└── TODO.md                   # Proje iş takibi ve yapılacaklar listesi
```

---

## 🛠️ Kurulum ve Çalıştırma

### 1. Bağımlılıkların Yüklenmesi
```bash
pip install -r requirements.txt
```

### 2. Veri İşleme ve Model Eğitimi Pipeline'ının Çalıştırılması
```bash
# 1. Gösterim verisini oluşturun veya ham veriyi aktarın
python -m src.download_data

# 2. Zaman ve frekans alanı özelliklerini çıkarın
python -m src.feature_extraction

# 3. Sağlık İndeksi ve RUL hedeflerini hesaplayın
python -m src.health_index

# 4. Anomali tespit modellerini eğitin
python -m src.models.anomaly_detector

# 5. RUL tahmin modellerini eğitin
python -m src.models.rul_predictor
```

### 3. İnteraktif Dashboard'un Başlatılması
```bash
streamlit run dashboard/app.py
```

---

## 📊 Rulman Karakteristik Arıza Frekansları (Rexnord ZA-2115)
- **BPFO (Dış Bilezik Arızası):** `236.4 Hz`
- **BPFI (İç Bilezik Arızası):** `296.9 Hz`
- **BSF (Bilya / Yuvarlanma Elemanı Arızası):** `139.9 Hz`
- **FTF (Kafes Arızası):** `14.7 Hz`
