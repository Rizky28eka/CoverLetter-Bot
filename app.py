import json
import google.generativeai as genai
import smtplib
import getpass
from email.message import EmailMessage

# Konfigurasi API Key Gemini
genai.configure(api_key="AIzaSyDMZ1OQfckLdSesiVGvIlRNFIIw7pT1Me4")

def generate_cover_letter(nama, posisi, perusahaan, sumber_lowongan, keahlian):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Buatkan surat lamaran kerja untuk posisi {posisi} di perusahaan {perusahaan}.

    Berikut adalah informasi pelamar:
    Nama: {nama}
    Keahlian: {keahlian}

    Surat lamaran harus ditulis dengan gaya profesional dan menyoroti keahlian yang relevan dengan posisi yang dilamar.
    """
    response = model.generate_content(prompt)
    return response.text

def send_email(subject, body, to_email):
    from_email = "dina.agustin31806@gmail.com"
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
        print("Gagal mengirim email: Autentikasi gagal. Periksa kembali password Anda.")
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
    keahlian = input("Masukkan keahlian yang relevan (pisahkan dengan koma): ")

    # Membuat surat lamaran dengan Gemini
    print("\nMembuat surat lamaran...")
    surat_lamaran = generate_cover_letter(
        config['nama'],
        posisi,
        perusahaan,
        sumber_lowongan,
        keahlian
    )

    # Menyimpan surat lamaran ke file
    nama_file = f"output/surat_lamaran_{perusahaan}_{posisi}.txt"
    with open(nama_file, 'w') as f:
        f.write(surat_lamaran)

    print(f"Surat lamaran berhasil dibuat dan disimpan di: {nama_file}")
    print("-" * 20)
    print(surat_lamaran)
    print("-" * 20)

    # Tanyakan apakah pengguna ingin mengirim email
    kirim = input("Apakah Anda ingin langsung mengirimkan surat lamaran ini via email? (y/n): ").lower()
    if kirim == 'y':
        email_tujuan = input("Masukkan alamat email tujuan: ")
        subjek = f"Lamaran Kerja - {posisi} - {config['nama']}"
        send_email(subjek, surat_lamaran, email_tujuan)

if __name__ == "__main__":
    main()
