from typing import Optional

import PyPDF2


def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                if page.extract_text():
                    text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
