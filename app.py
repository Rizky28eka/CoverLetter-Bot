import json
import os
import streamlit as st
from dotenv import load_dotenv

# Muat variabel dari file .env
load_dotenv()

# Impor fungsi dari modul yang direfaktorisasi
from src.ai_service import generate_cover_letter
from src.email_sender import send_email_with_attachments
from src.cv_parser import extract_text_from_pdf
from src.job_parser import scrape_job_description
from src.history_manager import add_to_history, load_history

def main_gui():
    st.set_page_config(page_title="Cover Letter Bot", layout="centered")
    st.title("🤖 Cover Letter Bot")
    st.write("Hasilkan surat lamaran kerja profesional secara otomatis!")

    # Muat konfigurasi
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        st.error(f"Error: config.json tidak ditemukan di {config_path}.")
        return
    except json.JSONDecodeError:
        st.error("Error: Format config.json tidak valid. Periksa kembali sintaks JSON.")
        return

    st.sidebar.header("Data Pelamar (dari config.json)")
    st.sidebar.json(config) # Tampilkan data config di sidebar

    # Tampilkan riwayat lamaran di sidebar
    st.sidebar.header("Riwayat Lamaran")
    history = load_history()
    if history:
        for entry in history:
            st.sidebar.write(f"- {entry['company']} ({entry['position']}) - {entry['timestamp'][:10]}")
    else:
        st.sidebar.info("Belum ada riwayat lamaran.")

    # Bagian form untuk input utama
    with st.form("cover_letter_form"):
        st.header("Detail Lowongan")
        posisi = st.text_input("Posisi yang Dilamar", placeholder="Contoh: Software Engineer")
        perusahaan = st.text_input("Nama Perusahaan", placeholder="Contoh: Google")
        sumber_lowongan = st.text_input("Sumber Lowongan", placeholder="Contoh: LinkedIn, Situs Perusahaan")
        job_url = st.text_input("URL Lowongan (Opsional, untuk analisis deskripsi pekerjaan)", placeholder="Contoh: https://example.com/job")
        writing_style = st.selectbox("Pilih Gaya Penulisan", ["Formal", "Kreatif", "Percaya Diri"])

        submitted = st.form_submit_button("Buat Surat Lamaran")

        if submitted:
            if not posisi or not perusahaan:
                st.error("Posisi dan Nama Perusahaan wajib diisi.")
            else:
                st.info("Membuat surat lamaran dengan AI... (ini mungkin butuh beberapa detik)")
                
                cv_path = os.path.join(os.path.dirname(__file__), 'CV Kerja.pdf')
                cv_text = extract_text_from_pdf(cv_path)
                if not cv_text:
                    st.warning("Gagal mengekstrak teks dari CV Kerja.pdf. Surat lamaran mungkin kurang detail.")

                job_desc_text = None
                if job_url:
                    st.info(f"Menganalisis deskripsi pekerjaan dari URL: {job_url}")
                    # Panggil scrape_job_description dan tangani error di UI
                    try:
                        job_desc_text = scrape_job_description(job_url)
                        if not job_desc_text:
                            st.warning("Gagal menganalisis deskripsi pekerjaan dari URL. Pastikan URL valid dan struktur HTML dapat di-scrape.")
                    except Exception as e:
                        st.error(f"Terjadi kesalahan saat scraping URL: {e}")
                        job_desc_text = None

                surat_lamaran = generate_cover_letter(
                    config,
                    posisi,
                    perusahaan,
                    sumber_lowongan,
                    cv_text,
                    job_desc_text,
                    writing_style
                )

                st.session_state['surat_lamaran'] = surat_lamaran # Simpan di session state
                st.session_state['nama_file'] = f"output/surat_lamaran_{perusahaan.replace(' ', '_')}_{posisi.replace(' ', '_')}.txt"
                st.session_state['perusahaan'] = perusahaan
                st.session_state['posisi'] = posisi

    # Bagian output dan pengiriman email (di luar form)
    if 'surat_lamaran' in st.session_state and st.session_state['surat_lamaran']:
        surat_lamaran = st.session_state['surat_lamaran']
        nama_file = st.session_state['nama_file']
        perusahaan = st.session_state['perusahaan']
        posisi = st.session_state['posisi']

        st.subheader("Surat Lamaran Anda:")
        st.text_area("Hasil", surat_lamaran, height=400)

        # Simpan surat lamaran ke file
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)
        full_file_path = os.path.join(output_dir, os.path.basename(nama_file))
        try:
            with open(full_file_path, 'w') as f:
                f.write(surat_lamaran)
            st.success(f"Surat lamaran berhasil dibuat dan disimpan di: {full_file_path}")
            add_to_history(perusahaan, posisi, full_file_path) # Tambahkan ke riwayat
        except Exception as e:
            st.error(f"Gagal menyimpan surat lamaran: {e}")

        st.subheader("Kirim Surat Lamaran via Email")
        email_tujuan = st.text_input("Masukkan alamat email tujuan:", key="email_input")
        if st.button("Kirim Email Sekarang", key="send_email_button"):
            if email_tujuan:
                subjek = f"Lamaran Kerja - {posisi} - {config['nama']}"
                cv_path_for_attachment = os.path.join(os.path.dirname(__file__), 'CV Kerja.pdf')
                attachments_list = [full_file_path, cv_path_for_attachment]
                
                # Panggil fungsi send_email_with_attachments dari modul
                send_email_with_attachments(subjek, surat_lamaran, email_tujuan, config['email'], attachments_list)
            else:
                st.warning("Alamat email tujuan tidak boleh kosong.")

if __name__ == "__main__":
    main_gui()