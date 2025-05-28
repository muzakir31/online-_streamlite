import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient
from selenium.webdriver.chrome.options import Options
import matplotlib.pyplot as plt
from datetime import datetime

# Ganti ini dengan URI MongoDB Atlas kamu
MONGO_URI = "mongodb+srv://muhamadmuzakir31:Zakir12345@cluster0.qu8iqhv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

def save_to_mongo(data):
    if data:
        client = MongoClient(MONGO_URI)
        db = client['Capston']          # nama database sama seperti sebelumnya
        collection = db['Fruitcare']          # nama koleksi juga sama

        documents = []
        current_time = datetime.now()
        for article in data:
            document = {
                "url": article['url'],
                "title": article['title'],
                "summary": article.get('summary', ''),
                "source": "halosehat.com",
                "date": current_time
            }
            documents.append(document)
        collection.insert_many(documents)
        print(f"Berhasil simpan {len(documents)} artikel.")
    else:
        print("Tidak ada data yang cocok.")

def search_articles(query, max_pages=10):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    article_links = []
    page = 1

    while page <= max_pages:
        print(f"Cari halaman {page} untuk keyword: {query}")
        url = f'https://www.halosehat.com/page/{page}/?s={query}'
        driver.get(url)
        time.sleep(3)

        articles = driver.find_elements(By.CSS_SELECTOR, 'article')
        if not articles:
            print(f"Tidak ada artikel di halaman {page}. Berhenti.")
            break

        for article_el in articles:
            try:
                title_link_el = article_el.find_element(By.CSS_SELECTOR, 'h2.entry-title a')
                href = title_link_el.get_attribute('href')
                title = title_link_el.text.strip()

                content_el = article_el.find_element(By.CSS_SELECTOR, '.entry-content p')
                content = content_el.text.strip() if content_el else "Tidak ada konten"

                if href and href not in [a['url'] for a in article_links]:
                    article_links.append({
                        "url": href,
                        "title": title,
                        "summary": content
                    })
            except:
                continue

        # Cek apakah ada tombol "Next"
        try:
            driver.find_element(By.CSS_SELECTOR, 'a.next.page-numbers')
            page += 1
        except:
            print("Tidak ada halaman selanjutnya.")
            break

    driver.quit()
    return article_links

def visualize_data(articles, queries):
    keyword_counts = {}
    for keyword in queries:
        count = sum(1 for article in articles if keyword.lower() in article['url'].lower() or keyword.lower() in article['title'].lower())
        keyword_counts[keyword] = count

    plt.figure(figsize=(10, 6))
    plt.bar(keyword_counts.keys(), keyword_counts.values(), color='skyblue')
    plt.title('Jumlah Artikel per Kata Kunci')
    plt.xlabel('Kata Kunci')
    plt.ylabel('Jumlah Artikel')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main():
    queries = [
        'diabetes', 'kadar gula',
        'buah rendah gula', 'diet', 'obesitas'
    ]

    all_articles = []

    for query in queries:
        print(f"\nMencari artikel untuk kata kunci: '{query}'")
        articles = search_articles(query)
        if articles:
            print(f"Ditemukan {len(articles)} artikel untuk kata kunci '{query}'.")
            all_articles.extend(articles)
        else:
            print(f"Tidak ditemukan artikel untuk kata kunci '{query}'.")

    if all_articles:
        print(f"\nTotal artikel ditemukan: {len(all_articles)}")
        save_to_mongo(all_articles)
        visualize_data(all_articles, queries)
    else:
        print("Tidak ada artikel yang ditemukan untuk semua kata kunci.")

if __name__ == "__main__":
    main()
