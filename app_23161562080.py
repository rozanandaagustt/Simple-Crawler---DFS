import requests
from bs4 import BeautifulSoup
import mysql.connector
from urllib.parse import urljoin, urlparse

def web_crawler_dfs(start_url, visited=None, db_connection=None):
    if visited is None:
        visited = set()
    
    if start_url in visited:
        return
    visited.add(start_url)
    
    try:
        response = requests.get(start_url)
        if response.status_code != 200:
            print(f"Gagal mengambil {start_url}, status code: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ambil judul (h1)
        title = soup.find('h1').text.strip() if soup.find('h1') else "Tidak ada judul"
        
        # Ambil paragraf pertama
        paragraph = soup.find('p').text.strip() if soup.find('p') else "Tidak ada paragraf"
        
        if db_connection:
            cursor = db_connection.cursor()
            sql = "INSERT INTO websites (url, judul_artikel, paragraph) VALUES (%s, %s, %s)"
            values = (start_url, title, paragraph)
            cursor.execute(sql, values)
            db_connection.commit()
            print(f"Disimpan ke database: {start_url} - {title}")
        
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                absolute_url = urljoin(start_url, href)
                
                if urlparse(absolute_url).netloc == urlparse(start_url).netloc:
                    web_crawler_dfs(absolute_url, visited, db_connection)
    
    except Exception as e:
        print(f"Error pada {start_url}: {e}")

def create_database_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  
            password="",  
            database="rozananda_web"  
        )
        
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS websites (
                id INT AUTO_INCREMENT PRIMARY KEY,
                url VARCHAR(255),
                judul_artikel VARCHAR(255),
                paragraph TEXT
            )
        """)
        connection.commit()
        
        return connection
    
    except mysql.connector.Error as error:
        print(f"Gagal terhubung ke MySQL: {error}")
        return None

def main():
    start_url = "http://localhost:8000/index.html"  # Sesuaikan port jika diperlukan
    
    db_connection = create_database_connection()
    
    if db_connection:
        web_crawler_dfs(start_url, None, db_connection)
        
        db_connection.close()
        print("Crawling selesai!")
    else:
        print("Tidak dapat melanjutkan tanpa koneksi database")

if __name__ == "__main__":
    main()
