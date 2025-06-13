<<<<<<< HEAD
# 🩺 Aplikasi Dashboard Kesehatan

Aplikasi web berbasis **Streamlit** yang memungkinkan pengguna untuk **membuat akun**, **login**, dan menggunakan berbagai **alat analisis kesehatan**, seperti prediksi risiko penyakit, rekomendasi kesehatan, dan prediksi kebiasaan merokok atau konsumsi alkohol. Aplikasi juga mencatat **riwayat aktivitas pengguna**.

---

## 📁 Struktur Proyek
```
├── database.py
├── main.py
├── pages/
│ ├── Dashboard.py
│ ├── Disease Risk.py
│ ├── Health Recommendation.py
│ └── Smoking & Alcohol Prediction.py
├── README.md
└── users.db
```

---

## 🚀 Fitur Utama

- 🔐 **Login & Sign Up**
  - Pengguna dapat mendaftar dengan username & password
  - Password di-hash dengan SHA-256 untuk keamanan
- 📜 **Riwayat Aktivitas**
  - Mencatat setiap tindakan pengguna dengan timestamp dan metadata
- 🧠 **Modular & Terstruktur**
  - Setiap fitur berada di file terpisah (dalam folder `pages`)
- 📊 **Fitur Analisis Kesehatan**
  - Prediksi Risiko Penyakit
  - Rekomendasi Kesehatan
  - Prediksi Kebiasaan Merokok & Alkohol
  - Dashboard

---

## 🛠️ Cara Menjalankan Aplikasi

### 1. Clone Repository

```bash
git clone "https://github.com/Fall-Llihc/PASD_KostPutraMR.git"
cd health-dashboard
```

### 2. Install Dependecies

```bash
pip install -r requirement.txt
```

### 3. Run the Application
```bash
streamlit run main.py
```
=======
# PASD_KostPutraMR
Test Branch Falih
>>>>>>> aec55d5e6ccf2c0648045cf98307352f9dddac74
