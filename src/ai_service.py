import json
import os
from typing import Any, Dict, Optional

import google.generativeai as genai

# Konfigurasi API Key Gemini dari environment variable
api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError(
        "GEMINI_API_KEY tidak ditemukan. Pastikan ada di file .env dan sudah diatur."
    )
genai.configure(api_key=api_key)


def generate_cover_letter(
    config: Dict[str, Any],
    posisi: str,
    perusahaan: str,
    sumber_lowongan: str,
    cv_text: Optional[str] = None,
    job_desc_text: Optional[str] = None,
    writing_style: str = "Formal",
) -> Dict[str, Any]:
    model = genai.GenerativeModel("gemini-1.5-flash")

    keahlian_teknis: str = ", ".join(config["keahlian"]["teknis"])
    keahlian_non_teknis: str = ", ".join(config["keahlian"]["non_teknis"])

    cv_info: str = f"Berikut adalah ringkasan CV pelamar:\n{cv_text}\n" if cv_text else ""
    job_info: str = (
        f"Berikut adalah deskripsi pekerjaan yang dianalisis:\n{job_desc_text}\n"
        if job_desc_text
        else ""
    )

    prompt: str = f"""
    **Peran:** Anda adalah seorang asisten karier profesional yang bertugas untuk membuat surat lamaran kerja yang personal, relevan, dan persuasif.

    **Tugas:** Buatkan sebuah surat lamaran kerja yang ditujukan kepada pimpinan HRD di perusahaan **{perusahaan}** untuk posisi **{posisi}**. Lowongan ini ditemukan melalui **{sumber_lowongan}**. Selain surat lamaran, berikan juga skor kecocokan numerik (dari 1 hingga 100) antara profil pelamar dengan deskripsi pekerjaan.

    Gunakan informasi dari data pelamar berikut untuk menyusun surat lamaran yang paling efektif:

    * **Nama Lengkap:** {config['nama']}
    * **Profil Singkat:** Lulusan baru SMK yang berorientasi pada keterampilan kerja, komunikatif, dan kolaboratif.
    * **Pendidikan:** SMK Ma'arif 3 Wates, Jurusan Multimedia.
    * **Pengalaman Relevan:** Magang sebagai Desain Grafis di Funcom (Desember 2023 - Juli 2024), bertanggung jawab membuat desain visual (poster, feed Instagram, banner), berkolaborasi dengan tim untuk revisi, dan mengoperasikan Adobe Photoshop, Illustrator, serta Canva.
    * **Keahlian Teknis:** {keahlian_teknis}
    * **Keahlian Non-Teknis:** {keahlian_non_teknis}

    {cv_info}
    {job_info}

    **Instruksi Tambahan:**
    * Tulis surat dengan gaya bahasa yang **{writing_style}**, profesional, dan percaya diri.
    * **Sangat Penting:** Bandingkan keahlian pelamar dengan persyaratan yang ada di deskripsi pekerjaan. Sorot dan tekankan keahlian yang paling relevan dan cocok dengan posisi yang dilamar.
    * Jelaskan bagaimana kombinasi keahlian teknis (desain grafis) dan non-teknis (komunikasi, kerja tim) menjadikan pelamar kandidat yang kuat.
    * Pastikan surat lamaran ini menyoroti semangat pelamar untuk belajar dan berkontribusi secara nyata di lingkungan kerja.

    **Format Output:** Berikan respons dalam format JSON dengan dua kunci: "cover_letter" (berisi teks surat lamaran) dan "match_score" (berisi skor numerik dari 1-100).

    **Contoh Output JSON:**
    ```json
    {{
        "cover_letter": "Yth. Bapak/Ibu Pimpinan HRD...",
        "match_score": 85
    }}
    ```
    """
    try:
        response = model.generate_content(prompt)
        response_text: str = response.text.strip()
        if response_text.startswith("```json") and response_text.endswith("```"):
            response_text = response_text[7:-3].strip()

        parsed_response: Dict[str, Any] = json.loads(response_text)
        return parsed_response
    except Exception as e:
        print(f"Error saat memanggil Gemini API atau parsing respons: {e}")
        return {
            "cover_letter": "Gagal membuat surat lamaran. Silakan coba lagi.",
            "match_score": 0,
        }


def generate_cv_suggestions(
    cv_text: str, job_desc_text: str, config: Dict[str, Any]
) -> str:
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt: str = f"""
    **Peran:** Anda adalah seorang konsultan karier yang ahli dalam mengoptimalkan CV.

    **Tugas:** Analisis CV berikut dan deskripsi pekerjaan yang diberikan. Berikan saran konkret dan actionable (poin-poin) tentang bagaimana CV pelamar dapat diperbaiki atau disesuaikan agar lebih menonjol dan relevan untuk posisi yang dilamar. Fokus pada penyesuaian kata kunci, penyorotan pengalaman relevan, dan penambahan detail yang mungkin terlewat.

    **Data CV Pelamar:**
    {cv_text}

    **Deskripsi Pekerjaan:**
    {job_desc_text}

    **Instruksi Tambahan:**
    * Berikan saran dalam bentuk daftar poin-poin yang jelas dan ringkas.
    * Jangan membuat surat lamaran atau ringkasan. Hanya berikan saran perbaikan CV.
    * Jika CV sudah sangat cocok, berikan pujian dan saran minimal.
    * Contoh format saran:
        - "Tambahkan detail kuantitatif pada pengalaman magang di Funcom, misalnya 'meningkatkan engagement Instagram sebesar X%'"
        - "Sertakan kata kunci 'Manajemen Proyek' jika relevan dengan pengalaman Anda."
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error saat memanggil Gemini API untuk saran CV: {e}")
        return "Gagal mendapatkan saran perbaikan CV."


def generate_thank_you_email(
    config: Dict[str, Any], posisi: str, perusahaan: str, tanggal_wawancara: Optional[str] = None
) -> str:
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt: str = f"""
    **Peran:** Anda adalah seorang asisten karier yang membantu membuat email profesional.

    **Tugas:** Buatkan email ucapan terima kasih setelah wawancara untuk posisi {posisi} di perusahaan {perusahaan}.

    **Data Pelamar:**
    Nama: {config['nama']}
    Email: {config['email']}
    Telepon: {config['telepon']}

    **Instruksi Tambahan:**
    * Tulis dengan nada profesional dan antusias.
    * Ucapkan terima kasih atas waktu dan kesempatan wawancara.
    * Tegaskan kembali minat pada posisi dan perusahaan.
    * Singgung secara singkat poin kunci yang dibahas dalam wawancara (jika memungkinkan, AI bisa menggeneralisasi).
    * Sertakan tanggal wawancara jika disediakan.
    * Format output adalah teks email lengkap.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error saat memanggil Gemini API untuk email terima kasih: {e}")
        return "Gagal membuat email ucapan terima kasih."


def generate_follow_up_email(
    config: Dict[str, Any], posisi: str, perusahaan: str, tanggal_lamar: Optional[str] = None
) -> str:
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt: str = f"""
    **Peran:** Anda adalah seorang asisten karier yang membantu membuat email profesional.

    **Tugas:** Buatkan email tindak lanjut (follow-up) untuk menanyakan status lamaran kerja untuk posisi {posisi} di perusahaan {perusahaan}.

    **Data Pelamar:**
    Nama: {config['nama']}
    Email: {config['email']}
    Telepon: {config['telepon']}

    **Instruksi Tambahan:**
    * Tulis dengan nada sopan dan profesional.
    * Ingatkan tentang lamaran yang diajukan.
    * Tanyakan dengan hormat mengenai status lamaran.
    * Tegaskan kembali minat pada posisi.
    * Format output adalah teks email lengkap.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error saat memanggil Gemini API untuk email tindak lanjut: {e}")
        return "Gagal membuat email tindak lanjut."
