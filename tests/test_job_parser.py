import pytest
from unittest.mock import patch, MagicMock
from src.job_parser import scrape_job_description


@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock_get:
        yield mock_get


def test_scrape_job_description_success(mock_requests_get):
    mock_response = MagicMock()
    mock_response.text = '<html><body><div class="job-description">Test job description</div></body></html>'
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    result = scrape_job_description("http://example.com")

    assert result == "Test job description"


def test_scrape_job_description_fallback(mock_requests_get):
    mock_response = MagicMock()
    mock_response.text = '<html><body><p>This is the body</p></body></html>'
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    result = scrape_job_description("http://example.com")

    assert result == "This is the body"


def test_scrape_job_description_request_exception(mock_requests_get):
    mock_requests_get.side_effect = Exception("Test error")

    result = scrape_job_description("http://example.com")

    assert result is None
