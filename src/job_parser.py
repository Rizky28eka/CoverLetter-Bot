import requests
from bs4 import BeautifulSoup

def scrape_job_description(url):
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ini adalah contoh sederhana, perlu disesuaikan dengan struktur HTML situs lowongan
        # Cari elemen yang mungkin berisi deskripsi pekerjaan, misalnya div dengan class tertentu
        job_description_element = soup.find('div', class_='job-description') # Ganti dengan class/id yang relevan
        if job_description_element:
            return job_description_element.get_text(separator=' ', strip=True)
        else:
            # Fallback: coba ambil semua teks dari body atau elemen umum lainnya
            return soup.body.get_text(separator=' ', strip=True)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return None
