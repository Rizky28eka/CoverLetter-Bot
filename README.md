# Cover Letter Bot

## Deskripsi

Cover Letter Bot adalah aplikasi web yang membantu Anda membuat surat lamaran kerja, email ucapan terima kasih, dan email tindak lanjut secara otomatis menggunakan kecerdasan buatan (AI). Aplikasi ini dibangun dengan Python dan Streamlit, dan menggunakan model AI generatif dari Google untuk menghasilkan teks yang profesional dan relevan.

## Fitur

- **Pembuatan Dokumen Otomatis:** Buat surat lamaran, email ucapan terima kasih, dan email tindak lanjut yang dipersonalisasi.
- **Analisis Cerdas:** Menganalisis CV dan deskripsi pekerjaan (dari URL atau teks) untuk menghitung skor kecocokan.
- **Saran Peningkatan CV:** Dapatkan saran konkret untuk meningkatkan CV Anda agar lebih sesuai dengan pekerjaan yang Anda lamar.
- **Antarmuka Web Interaktif:** Aplikasi ini menyediakan antarmuka web yang sederhana dan intuitif yang dibangun dengan Streamlit.
- **Personalisasi Mudah:** Edit dan simpan data pribadi Anda (nama, kontak, keahlian, dll.) langsung di dalam aplikasi.
- **Riwayat Lamaran:** Lacak semua surat lamaran yang telah Anda buat melalui database lokal.
- **Pengiriman Email:** Kirim dokumen yang dihasilkan langsung dari aplikasi (memerlukan konfigurasi email).

## Prasyarat

- Python 3.8+
- Akses ke `pip` (Python package installer)

## Instalasi

1.  **Kloning Repositori:**
    ```bash
    git clone https://github.com/Rizky28eka/CoverLetter-Bot.git
    cd CoverLetter-Bot
    ```

2.  **Buat dan Aktifkan Lingkungan Virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Di Windows, gunakan `venv\Scripts\activate`
    ```

3.  **Instal Dependensi:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Konfigurasi Proyek:**

    Aplikasi ini memerlukan dua file konfigurasi utama: `.env` untuk kunci API rahasia dan `config.json` untuk data pribadi Anda.

    a. **Konfigurasi Kunci API (`.env`):**
    - Salin file contoh `.env.example` menjadi file baru bernama `.env`.
      ```bash
      cp .env.example .env
      ```
    - Buka file `.env` dan masukkan Google Gemini API Key Anda.
      ```dotenv
      GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
      ```
    - (Opsional) Jika Anda ingin menggunakan fitur pengiriman email, tambahkan kredensial email Anda.
      ```dotenv
      EMAIL_PASSWORD="YOUR_EMAIL_APP_PASSWORD"
      ```

    b. **Konfigurasi Data Pelamar (`config.json`):**
    - Salin file contoh `config.json.example` menjadi file baru bernama `config.json`.
      ```bash
      cp config.json.example config.json
      ```
    - Buka file `config.json` dan isi dengan data pribadi Anda. Anda juga dapat mengedit data ini nanti melalui antarmuka aplikasi.

## Cara Menjalankan Aplikasi

Setelah dependensi terinstal dan konfigurasi selesai, jalankan aplikasi menggunakan perintah berikut:

```bash
streamlit run app.py
```

Aplikasi akan terbuka secara otomatis di browser Anda pada alamat `http://localhost:8501`.

## Troubleshooting

**Error `Failed to fetch dynamically imported module` atau Masalah Tampilan di Browser**

Terkadang, Streamlit dapat mengalami masalah dengan file cache di browser setelah pembaruan atau pada eksekusi pertama. Error ini biasanya muncul di konsol JavaScript browser.

**Solusi:**
1.  **Hapus Cache Browser:** Lakukan "hard refresh" dan hapus cache browser Anda. (Contoh di Chrome: `Cmd+Shift+R` di Mac, `Ctrl+Shift+R` di Windows).
2.  **Instalasi Ulang Streamlit:** Jika masalah berlanjut, lakukan instalasi ulang Streamlit untuk memastikan tidak ada file yang korup.
    ```bash
    pip uninstall -y streamlit
    pip cache purge
    pip install streamlit
    ```
3.  **Jalankan Ulang Aplikasi:** Hentikan server (`Ctrl+C` di terminal) dan jalankan kembali.

## Struktur Proyek

```
CoverLetter-Bot/
├── .env.example
├── .gitignore
├── app.py
├── config.json
├── config.json.example
├── CV Kerja.pdf
├── pytest.ini
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── ai_service.py
│   ├── cv_parser.py
│   ├── email_sender.py
│   ├── history_manager.py
│   └── job_parser.py
├── templates/
│   └── template_surat_lamaran.txt
└── tests/
    └── ...
```

- **`app.py`**: File utama aplikasi Streamlit.
- **`config.json`**: File konfigurasi untuk data pelamar.
- **`src/`**: Direktori berisi modul-modul utama:
    - `ai_service.py`: Berinteraksi dengan Gemini API.
    - `cv_parser.py`: Mengekstrak teks dari PDF.
    - `email_sender.py`: Mengirim email.
    - `history_manager.py`: Mengelola database riwayat.
    - `job_parser.py`: Mengekstrak deskripsi pekerjaan dari URL.
- **`templates/`**: Berisi templat teks.
- **`tests/`**: Berisi unit tests untuk aplikasi.