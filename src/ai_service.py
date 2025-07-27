import google.generativeai as genai
import os

# Konfigurasi API Key Gemini dari environment variable
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY tidak ditemukan. Pastikan ada di file .env dan sudah diatur.")
genai.configure(api_key=api_key)

def generate_cover_letter(config, posisi, perusahaan, sumber_lowongan, cv_text=None, job_desc_text=None, writing_style="Formal"):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    keahlian_teknis = ", ".join(config['keahlian']['teknis'])
    keahlian_non_teknis = ", ".join(config['keahlian']['non_teknis'])

    cv_info = f"Berikut adalah ringkasan CV pelamar:\n{cv_text}\n" if cv_text else ""
    job_info = f"Berikut adalah deskripsi pekerjaan yang dianalisis:\n{job_desc_text}\n" if job_desc_text else ""

    prompt = f"""
    **Peran:** Anda adalah seorang asisten karier profesional yang bertugas untuk membuat surat lamaran kerja yang personal, relevan, dan persuasif.

    **Tugas:** Buatkan sebuah surat lamaran kerja yang ditujukan kepada pimpinan HRD di perusahaan **{perusahaan}** untuk posisi **{posisi}**. Lowongan ini ditemukan melalui **{sumber_lowongan}**.

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
    * Hubungkan pengalaman magang di Funcom dengan kualifikasi yang dibutuhkan untuk posisi yang dilamar.
    * Jelaskan bagaimana kombinasi keahlian teknis (desain grafis) dan non-teknis (komunikasi, kerja tim) menjadikan pelamar kandidat yang kuat.
    * Pastikan surat lamaran ini menyoroti semangat pelamar untuk belajar dan berkontribusi secara nyata di lingkungan kerja.

    **Output yang Diharapkan:**
    Sebuah surat lamaran kerja lengkap dalam format teks yang siap untuk dikirim, di mana semua bagian telah diisi secara cerdas dan relevan berdasarkan konteks yang diberikan.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error saat memanggil Gemini API: {e}")
        return "Gagal membuat surat lamaran. Silakan coba lagi."
