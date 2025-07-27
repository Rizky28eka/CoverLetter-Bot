import json
import os
import google.generativeai as genai
import smtplib
import getpass
from email.message import EmailMessage
from dotenv import load_dotenv

# Muat variabel dari file .env
load_dotenv()

# Konfigurasi API Key Gemini dari environment variable
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY tidak ditemukan. Pastikan ada di file .env dan sudah diatur.")
genai.configure(api_key=api_key)

def generate_cover_letter(config, posisi, perusahaan, sumber_lowongan):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Mengubah data keahlian dari list menjadi string yang rapi
    keahlian_teknis = ", ".join(config['keahlian']['teknis'])
    keahlian_non_teknis = ", ".join(config['keahlian']['non_teknis'])

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

    **Instruksi Tambahan:**
    * Tulis surat dengan gaya bahasa yang formal, profesional, dan percaya diri.
    * Hubungkan pengalaman magang di Funcom dengan kualifikasi yang dibutuhkan untuk posisi yang dilamar.
    * Jelaskan bagaimana kombinasi keahlian teknis (desain grafis) dan non-teknis (komunikasi, kerja tim) menjadikan pelamar kandidat yang kuat.
    * Pastikan surat lamaran ini menyoroti semangat pelamar untuk belajar dan berkontribusi secara nyata di lingkungan kerja.

    **Output yang Diharapkan:**
    Sebuah surat lamaran kerja lengkap dalam format teks yang siap untuk dikirim, di mana semua bagian telah diisi secara cerdas dan relevan berdasarkan konteks yang diberikan.
    """
    response = model.generate_content(prompt)
    return response.text

def send_email(subject, body, to_email, from_email):
    password = getpass.getpass(f"Masukkan password untuk {from_email}: ")

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(from_email, password)
            smtp.send_message(msg)
        print("Email berhasil terkirim!")
    except smtplib.SMTPAuthenticationError:
        print("Gagal mengirim email: Autentikasi gagal. Pastikan Anda menggunakan 'App Password' jika 2FA aktif.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

def main():
    # Membaca data dari config.json
    with open('config.json', 'r') as f:
        config = json.load(f)

    # Meminta input dari pengguna
    posisi = input("Masukkan posisi yang dilamar: ")
    perusahaan = input("Masukkan nama perusahaan: ")
    sumber_lowongan = input("Masukkan sumber lowongan: ")

    # Membuat surat lamaran dengan Gemini
    print("\nMembuat surat lamaran dengan AI... (ini mungkin butuh beberapa detik)")
    surat_lamaran = generate_cover_letter(
        config,
        posisi,
        perusahaan,
        sumber_lowongan
    )

    # Menyimpan surat lamaran ke file
    nama_file = f"output/surat_lamaran_{perusahaan.replace(' ', '_')}_{posisi.replace(' ', '_')}.txt"
    with open(nama_file, 'w') as f:
        f.write(surat_lamaran)

    print(f"\nSurat lamaran berhasil dibuat dan disimpan di: {nama_file}")
    print("-" * 50)
    print(surat_lamaran)
    print("-" * 50)

    # Tanyakan apakah pengguna ingin mengirim email
    kirim = input("Apakah Anda ingin langsung mengirimkan surat lamaran ini via email? (y/n): ").lower()
    if kirim == 'y':
        email_tujuan = input("Masukkan alamat email tujuan: ")
        subjek = f"Lamaran Kerja - {posisi} - {config['nama']}"
        send_email(subjek, surat_lamaran, email_tujuan, config['email'])

if __name__ == "__main__":
    main()