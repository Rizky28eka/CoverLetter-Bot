import os
import pytest
from src.cv_parser import extract_text_from_pdf

# Path ke CV Kerja.pdf (asumsi ada di root proyek)
# Sesuaikan path ini jika CV Kerja.pdf berada di lokasi lain
CV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'CV Kerja.pdf')

@pytest.fixture(scope="module")
def sample_cv_pdf():
    """Fixture untuk memastikan CV Kerja.pdf ada dan mengembalikan path-nya."""
    if not os.path.exists(CV_PATH):
        pytest.skip(f"CV Kerja.pdf tidak ditemukan di {CV_PATH}. Lewati tes ini.")
    return CV_PATH

def test_extract_text_from_pdf_success(sample_cv_pdf):
    """Menguji ekstraksi teks yang berhasil dari PDF."""
    extracted_text = extract_text_from_pdf(sample_cv_pdf)
    
    assert extracted_text is not None
    assert isinstance(extracted_text, str)
    assert len(extracted_text) > 100 # Asumsi CV memiliki lebih dari 100 karakter
    assert "Dina Agustin" in extracted_text # Asumsi nama pelamar ada di CV
    assert "Funcom" in extracted_text # Asumsi pengalaman kerja ada di CV

def test_extract_text_from_pdf_non_existent_file():
    """Menguji penanganan file yang tidak ada."""
    non_existent_path = "non_existent_cv.pdf"
    extracted_text = extract_text_from_pdf(non_existent_path)
    assert extracted_text is None

def test_extract_text_from_pdf_invalid_file():
    """Menguji penanganan file yang bukan PDF."""
    invalid_file_path = os.path.join(os.path.dirname(__file__), 'test_invalid.txt')
    with open(invalid_file_path, 'w') as f:
        f.write("Ini bukan PDF")
    
    extracted_text = extract_text_from_pdf(invalid_file_path)
    assert extracted_text is None
    os.remove(invalid_file_path) # Bersihkan file dummy
