import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st
from dotenv import load_dotenv

from src.ai_service import (
    generate_cover_letter,
    generate_cv_suggestions,
    generate_follow_up_email,
    generate_thank_you_email,
)
from src.cv_parser import extract_text_from_pdf
from src.email_sender import send_email_with_attachments
from src.history_manager import init_db, load_history, save_application
from src.job_parser import scrape_job_description

# Muat variabel dari file .env
load_dotenv()


def main_gui() -> None:
    st.set_page_config(page_title="Cover Letter Bot", layout="centered")
    st.title("🤖 Cover Letter Bot")
    st.write("Hasilkan surat lamaran kerja profesional secara otomatis!")

    # Inisialisasi database SQLite
    init_db()

    # Muat konfigurasi
    config_path: str = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path, "r") as f:
            config: Dict[str, Any] = json.load(f)
    except FileNotFoundError:
        st.error(f"Error: config.json tidak ditemukan di {config_path}.")
        return
    except json.JSONDecodeError:
        st.error("Error: Format config.json tidak valid. Periksa kembali sintaks JSON.")
        return

    st.sidebar.header("Data Pelamar (dari config.json)")
    st.sidebar.json(config)  # Tampilkan data config di sidebar

    # Tampilkan riwayat lamaran di sidebar
    st.sidebar.header("Riwayat Lamaran")
    history: List[Dict[str, Any]] = load_history()
    if history:
        for entry in history:
            st.sidebar.write(
                f"- {entry['company']} ({entry['position']}) - {entry['timestamp'][:10]}"
            )
    else:
        st.sidebar.info("Belum ada riwayat lamaran.")

    # Tabs untuk navigasi
    tab1, tab2 = st.tabs(["Buat Output", "Edit Data Pelamar"])

    with tab1:
        st.header("Pilih Jenis Output")
        output_type: Optional[str] = st.selectbox(
            "Saya ingin membuat:",
            ["Surat Lamaran", "Email Ucapan Terima Kasih", "Email Tindak Lanjut"],
            key="output_type_selector",
        )

        if output_type == "Surat Lamaran":
            uploaded_cv = st.file_uploader(
                "Unggah CV Anda (PDF)", type="pdf"
            )
            with st.form("cover_letter_form"):
                st.subheader("Detail Lowongan")
                posisi: str = st.text_input(
                    "Posisi yang Dilamar",
                    placeholder="Contoh: Software Engineer",
                    key="posisi_cl",
                )
                perusahaan: str = st.text_input(
                    "Nama Perusahaan", placeholder="Contoh: Google", key="perusahaan_cl"
                )
                sumber_lowongan: str = st.text_input(
                    "Sumber Lowongan",
                    placeholder="Contoh: LinkedIn, Situs Perusahaan",
                    key="sumber_cl",
                )
                job_url: str = st.text_input(
                    "URL Lowongan (Opsional, untuk analisis deskripsi pekerjaan)",
                    placeholder="Contoh: https://example.com/job",
                    key="job_url_cl",
                )
                writing_style: str = st.selectbox(
                    "Pilih Gaya Penulisan",
                    ["Formal", "Kreatif", "Percaya Diri"],
                    key="style_cl",
                )

                submitted: bool = st.form_submit_button("Buat Surat Lamaran")

                if submitted:
                    if not posisi or not perusahaan:
                        st.error("Posisi dan Nama Perusahaan wajib diisi.")
                    elif not uploaded_cv:
                        st.error("Silakan unggah CV Anda.")
                    else:
                        st.info(
                            "Membuat surat lamaran dengan AI... (ini mungkin butuh beberapa detik)"
                        )

                        # Save the uploaded CV to a temporary file
                        with open("temp_cv.pdf", "wb") as f:
                            f.write(uploaded_cv.getbuffer())

                        cv_text: Optional[str] = extract_text_from_pdf("temp_cv.pdf")
                        if not cv_text:
                            st.warning(
                                "Gagal mengekstrak teks dari CV. Surat lamaran mungkin kurang detail."
                            )

                        job_desc_text: Optional[str] = None
                        if job_url:
                            st.info(
                                f"Menganalisis deskripsi pekerjaan dari URL: {job_url}"
                            )
                            try:
                                job_desc_text = scrape_job_description(job_url)
                                if not job_desc_text or len(job_desc_text.strip()) < 50:
                                    st.warning(
                                        "Gagal menganalisis deskripsi pekerjaan dari URL atau teks terlalu pendek. Silakan masukkan secara manual di bawah."
                                    )
                                    job_desc_text = st.text_area(
                                        "Masukkan Deskripsi Pekerjaan Secara Manual:",
                                        height=200,
                                        key="manual_job_desc_cl",
                                    )
                            except Exception as e:
                                st.error(
                                    f"Terjadi kesalahan saat scraping URL: {e}. Silakan masukkan deskripsi pekerjaan secara manual."
                                )
                                job_desc_text = st.text_area(
                                    "Masukkan Deskripsi Pekerjaan Secara Manual:",
                                    height=200,
                                    key="manual_job_desc_cl_error",
                                )
                        else:
                            job_desc_text = st.text_area(
                                "Masukkan Deskripsi Pekerjaan Secara Manual (Opsional):",
                                height=200,
                                key="manual_job_desc_cl_no_url",
                            )

                        if not job_desc_text or len(job_desc_text.strip()) < 50:
                            st.warning(
                                "Deskripsi pekerjaan kosong atau terlalu pendek. AI mungkin tidak dapat memberikan hasil yang optimal."
                            )

                        surat_lamaran_data: Dict[str, Any] = generate_cover_letter(
                            config,
                            posisi,
                            perusahaan,
                            sumber_lowongan,
                            cv_text,
                            job_desc_text,
                            writing_style,
                        )

                        st.session_state["generated_output"] = surat_lamaran_data.get(
                            "cover_letter", "Gagal membuat surat lamaran."
                        )
                        st.session_state["match_score"] = surat_lamaran_data.get(
                            "match_score", 0
                        )
                        st.session_state["output_type_display"] = "Surat Lamaran"
                        st.session_state["current_posisi"] = posisi
                        st.session_state["current_perusahaan"] = perusahaan
                        st.session_state["current_cv_text"] = cv_text
                        st.session_state["current_job_desc_text"] = job_desc_text
                        st.session_state["email_subject"] = (
                            f"Lamaran Kerja - {posisi} - {config['nama']}"
                        )

        elif output_type == "Email Ucapan Terima Kasih":
            with st.form("thank_you_email_form"):
                st.subheader("Detail Email Ucapan Terima Kasih")
                posisi_email: str = st.text_input(
                    "Posisi yang Diwawancarai", key="posisi_ty"
                )
                perusahaan_email: str = st.text_input("Nama Perusahaan", key="perusahaan_ty")
                tanggal_wawancara: datetime = st.date_input(
                    "Tanggal Wawancara (Opsional)",
                    key="tanggal_ty",
                    value=datetime.now(),
                )
                submitted_ty: bool = st.form_submit_button("Buat Email Ucapan Terima Kasih")

                if submitted_ty:
                    if not posisi_email or not perusahaan_email:
                        st.error("Posisi dan Perusahaan wajib diisi.")
                    else:
                        st.info("Membuat email ucapan terima kasih...")
                        generated_email: str = generate_thank_you_email(
                            config,
                            posisi_email,
                            perusahaan_email,
                            tanggal_wawancara.strftime("%d %B %Y")
                            if tanggal_wawancara
                            else None,
                        )
                        st.session_state["generated_output"] = generated_email
                        st.session_state["output_type_display"] = (
                            "Email Ucapan Terima Kasih"
                        )
                        st.session_state["email_subject"] = (
                            f"Terima Kasih - {posisi_email} - {config['nama']}"
                        )

        elif output_type == "Email Tindak Lanjut":
            with st.form("follow_up_email_form"):
                st.subheader("Detail Email Tindak Lanjut")
                posisi_email = st.text_input("Posisi yang Dilamar", key="posisi_fu")
                perusahaan_email = st.text_input("Nama Perusahaan", key="perusahaan_fu")
                tanggal_lamar: datetime = st.date_input(
                    "Tanggal Melamar (Opsional)", key="tanggal_fu", value=datetime.now()
                )
                submitted_fu: bool = st.form_submit_button("Buat Email Tindak Lanjut")

                if submitted_fu:
                    if not posisi_email or not perusahaan_email:
                        st.error("Posisi dan Perusahaan wajib diisi.")
                    else:
                        st.info("Membuat email tindak lanjut...")
                        generated_email = generate_follow_up_email(
                            config,
                            posisi_email,
                            perusahaan_email,
                            tanggal_lamar.strftime("%d %B %Y")
                            if tanggal_lamar
                            else None,
                        )
                        st.session_state["generated_output"] = generated_email
                        st.session_state["output_type_display"] = "Email Tindak Lanjut"
                        st.session_state["email_subject"] = (
                            f"Tindak Lanjut Lamaran - {posisi_email} - {config['nama']}"
                        )

        # Bagian tampilan output (di luar form, tapi di dalam tab1)
        if (
            "generated_output" in st.session_state
            and st.session_state["generated_output"]
        ):
            st.subheader(f"Hasil {st.session_state['output_type_display']}:")
            st.text_area("Output", st.session_state["generated_output"], height=400)

            if st.session_state["output_type_display"] == "Surat Lamaran":
                st.subheader("Skor Kecocokan:")
                st.metric(
                    label="Kecocokan CV & Pekerjaan",
                    value=f"{st.session_state['match_score']}%",
                    delta_color="normal",
                )

                st.subheader("Saran Perbaikan CV")
                if st.button(
                    "Dapatkan Saran Perbaikan CV", key="get_cv_suggestions_button"
                ):
                    if st.session_state.get("current_cv_text") and st.session_state.get(
                        "current_job_desc_text"
                    ):
                        st.info(
                            "Menganalisis CV dan deskripsi pekerjaan untuk saran..."
                        )
                        suggestions: str = generate_cv_suggestions(
                            st.session_state["current_cv_text"],
                            st.session_state["current_job_desc_text"],
                            config,
                        )
                        st.session_state["cv_suggestions"] = suggestions
                    else:
                        st.warning(
                            "Untuk mendapatkan saran CV, pastikan CV dan Deskripsi Pekerjaan (dari URL atau manual) telah tersedia saat membuat surat lamaran."
                        )

                if (
                    "cv_suggestions" in st.session_state
                    and st.session_state["cv_suggestions"]
                ):
                    with st.expander("Lihat Saran Perbaikan CV untuk Posisi Ini"):
                        st.markdown(st.session_state["cv_suggestions"])

            # Simpan output ke file (hanya untuk Surat Lamaran) dan tambahkan ke riwayat
            if st.session_state["output_type_display"] == "Surat Lamaran":
                output_dir: str = os.path.join(os.path.dirname(__file__), "output")
                os.makedirs(output_dir, exist_ok=True)
                nama_file_output: str = f"surat_lamaran_{st.session_state['current_perusahaan'].replace(' ', '_')}_{st.session_state['current_posisi'].replace(' ', '_')}.txt"
                full_file_path: str = os.path.join(output_dir, nama_file_output)
                try:
                    with open(full_file_path, "w") as f:
                        f.write(st.session_state["generated_output"])
                    st.success(f"Output berhasil disimpan di: {full_file_path}")
                    save_application(
                        st.session_state["current_perusahaan"],
                        st.session_state["current_posisi"],
                        full_file_path,
                    )  # Simpan ke DB
                except Exception as e:
                    st.error(f"Gagal menyimpan output: {e}")

            # Opsi kirim email
            st.subheader("Kirim Output via Email")
            email_tujuan: str = st.text_input(
                "Masukkan alamat email tujuan:", key="email_input_generic"
            )
            if st.button("Kirim Email Sekarang", key="send_email_button_generic"):
                if email_tujuan:
                    subject_to_send: str = st.session_state.get(
                        "email_subject", "Tanpa Subjek"
                    )
                    body_to_send: str = st.session_state["generated_output"]
                    attachments_to_send: List[str] = []

                    if st.session_state["output_type_display"] == "Surat Lamaran":
                        attachments_to_send.append(
                            full_file_path
                        )  # Lampirkan surat lamaran yang baru disimpan
                        if uploaded_cv:
                            attachments_to_send.append("temp_cv.pdf")

                    send_email_with_attachments(
                        subject_to_send,
                        body_to_send,
                        email_tujuan,
                        config["email"],
                        attachments_to_send,
                    )
                else:
                    st.warning("Alamat email tujuan tidak boleh kosong.")

    with tab2:
        st.header("Editor Data Pelamar")
        st.write("Ubah informasi pribadi dan keahlian Anda di sini.")

        # Buat salinan config untuk diedit
        edited_config: Dict[str, Any] = config.copy()

        edited_config["nama"] = st.text_input(
            "Nama Lengkap", edited_config.get("nama", ""), key="edit_nama"
        )
        edited_config["email"] = st.text_input(
            "Email", edited_config.get("email", ""), key="edit_email"
        )
        edited_config["telepon"] = st.text_input(
            "Telepon", edited_config.get("telepon", ""), key="edit_telepon"
        )
        edited_config["alamat"] = st.text_input(
            "Alamat", edited_config.get("alamat", ""), key="edit_alamat"
        )
        edited_config["linkedin"] = st.text_input(
            "LinkedIn", edited_config.get("linkedin", ""), key="edit_linkedin"
        )
        edited_config["github"] = st.text_input(
            "GitHub", edited_config.get("github", ""), key="edit_github"
        )

        st.subheader("Keahlian Teknis")
        # Gunakan st.text_area untuk list, pisahkan dengan koma
        edited_config["keahlian"]["teknis"] = [
            item.strip()
            for item in st.text_area(
                "Keahlian Teknis (pisahkan dengan koma)",
                ", ".join(edited_config["keahlian"].get("teknis", [])),
                key="edit_keahlian_teknis",
            ).split(",")
            if item.strip()
        ]

        st.subheader("Keahlian Non-Teknis")
        edited_config["keahlian"]["non_teknis"] = [
            item.strip()
            for item in st.text_area(
                "Keahlian Non-Teknis (pisahkan dengan koma)",
                ", ".join(edited_config["keahlian"].get("non_teknis", [])),
                key="edit_keahlian_non_teknis",
            ).split(",")
            if item.strip()
        ]

        if st.button("Simpan Perubahan Data Pelamar", key="save_config_button"):
            try:
                with open(config_path, "w") as f:
                    json.dump(edited_config, f, indent=4)
                st.success(
                    "Data pelamar berhasil disimpan! Aplikasi akan dimuat ulang."
                )
                st.session_state["config_updated"] = True  # Trigger reload
            except Exception as e:
                st.error(f"Gagal menyimpan data pelamar: {e}")

        # Jika config_updated, reload aplikasi untuk memuat config baru
        if "config_updated" in st.session_state and st.session_state["config_updated"]:
            st.session_state["config_updated"] = False
            st.experimental_rerun()  # Memaksa Streamlit untuk me-rerun seluruh skrip


if __name__ == "__main__":
    main_gui()
