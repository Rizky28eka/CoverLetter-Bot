import pytest
from unittest.mock import patch, MagicMock
from src.ai_service import (
    generate_cover_letter,
    generate_cv_suggestions,
    generate_thank_you_email,
    generate_follow_up_email,
)


@pytest.fixture
def mock_generative_model():
    with patch("google.generativeai.GenerativeModel") as mock_model:
        yield mock_model


@pytest.fixture
def sample_config():
    return {
        "nama": "John Doe",
        "email": "john.doe@example.com",
        "telepon": "1234567890",
        "keahlian": {
            "teknis": ["Python", "Streamlit"],
            "non_teknis": ["Komunikasi", "Kerja Tim"],
        },
    }


def test_generate_cover_letter(mock_generative_model, sample_config):
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value.text = '{"cover_letter": "Test cover letter", "match_score": 80}'
    mock_generative_model.return_value = mock_model_instance

    result = generate_cover_letter(
        config=sample_config,
        posisi="Software Engineer",
        perusahaan="Test Corp",
        sumber_lowongan="LinkedIn",
        cv_text="My CV",
        job_desc_text="Job description",
        writing_style="Formal",
    )

    assert "cover_letter" in result
    assert "match_score" in result
    assert result["cover_letter"] == "Test cover letter"
    assert result["match_score"] == 80


def test_generate_cv_suggestions(mock_generative_model, sample_config):
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value.text = "Test CV suggestions"
    mock_generative_model.return_value = mock_model_instance

    result = generate_cv_suggestions(
        cv_text="My CV",
        job_desc_text="Job description",
        config=sample_config,
    )

    assert result == "Test CV suggestions"


def test_generate_thank_you_email(mock_generative_model, sample_config):
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value.text = "Test thank you email"
    mock_generative_model.return_value = mock_model_instance

    result = generate_thank_you_email(
        config=sample_config,
        posisi="Software Engineer",
        perusahaan="Test Corp",
        tanggal_wawancara="2025-10-06",
    )

    assert result == "Test thank you email"


def test_generate_follow_up_email(mock_generative_model, sample_config):
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value.text = "Test follow-up email"
    mock_generative_model.return_value = mock_model_instance

    result = generate_follow_up_email(
        config=sample_config,
        posisi="Software Engineer",
        perusahaan="Test Corp",
        tanggal_lamar="2025-09-29",
    )

    assert result == "Test follow-up email"
