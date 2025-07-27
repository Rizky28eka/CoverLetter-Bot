from email.message import EmailMessage
import smtplib
import getpass
import os

def send_email_with_attachments(subject, body, to_email, from_email, attachments=None):
    password = getpass.getpass(f"Masukkan password untuk {from_email}: ")

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    if attachments:
        for attachment_path in attachments:
            if os.path.exists(attachment_path):
                try:
                    with open(attachment_path, 'rb') as f:
                        file_data = f.read()
                        file_name = os.path.basename(attachment_path)
                        msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
                except Exception as e:
                    print(f"Gagal melampirkan file {file_name}: {e}")
            else:
                print(f"Peringatan: File lampiran tidak ditemukan: {attachment_path}")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(from_email, password)
            smtp.send_message(msg)
        print("Email berhasil terkirim!")
    except smtplib.SMTPAuthenticationError:
        print("Gagal mengirim email: Autentikasi gagal. Pastikan Anda menggunakan 'App Password' jika 2FA aktif.")
    except Exception as e:
        print(f"Terjadi kesalahan saat mengirim email: {e}")

