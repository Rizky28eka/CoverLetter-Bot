import getpass
import os
import smtplib
from email.message import EmailMessage
from typing import List, Optional


def send_email_with_attachments(
    subject: str,
    body: str,
    to_email: str,
    from_email: str,
    attachments: Optional[List[str]] = None,
) -> None:
    # TODO: Consider using environment variables or a more secure way to handle passwords
    password = os.getenv("EMAIL_PASSWORD")
    if not password:
        password = getpass.getpass(f"Masukkan password untuk {from_email}: ")

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    if attachments:
        for attachment_path in attachments:
            if os.path.exists(attachment_path):
                try:
                    with open(attachment_path, "rb") as f:
                        file_data = f.read()
                        file_name = os.path.basename(attachment_path)
                        msg.add_attachment(
                            file_data,
                            maintype="application",
                            subtype="octet-stream",
                            filename=file_name,
                        )
                except Exception as e:
                    print(f"Gagal melampirkan file {file_name}: {e}")
            else:
                print(f"Peringatan: File lampiran tidak ditemukan: {attachment_path}")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(from_email, password)
            smtp.send_message(msg)
        print("Email berhasil terkirim!")
    except smtplib.SMTPAuthenticationError:
        print(
            "Gagal mengirim email: Autentikasi gagal. Pastikan Anda menggunakan 'App Password' jika 2FA aktif."
        )
    except Exception as e:
        print(f"Terjadi kesalahan saat mengirim email: {e}")
