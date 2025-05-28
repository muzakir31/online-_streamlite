import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# Setup awal
factory = StopWordRemoverFactory()
stop_words = set(factory.get_stop_words())

manual_stopwords = {
    'cara', 'tips', 'intip', 'paling', 'kenali', 'sih', 'loh', 'bikin',
    'jadi', 'begini', 'benarkah', 'inilah', 'apa', 'tak', 'yang', 'dan', 'dengan',
    'untuk', 'dari', 'sejak', 'lagi', 'oleh', 'hingga', 'satu', 'lainnya',
    'lebih', 'dapat', 'tidak', 'tersebut', 'baik', 'berikut', 'menjadi',
    'perlu', 'dengan', 'dalam', 'sudah', 'belum', 'karena', 'jika', 'karena',
    'merupakan', 'memiliki', 'sangat', 'bahkan', 'sering', 'berbagai', 'beberapa',
    'sebuah', 'biasanya', 'memang', 'mungkin'
}
stop_words.update(manual_stopwords)

# Streamlit config
st.set_page_config(page_title="Visualisasi Scraping", layout="wide")
st.title("📊 Dashboard Visualisasi - HaloSehat")

MONGO_URI = "mongodb+srv://muhamadmuzakir31:Zakir12345@cluster0.qu8iqhv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client['Capston']
collection = db['Fruitcare']

# Ambil data
data = list(collection.find({}, {"_id": 0, "title": 1, "summary": 1, "url": 1}))
df = pd.DataFrame(data)

#Filter
st.sidebar.header("🔍 Filter")
keyword_filter = st.sidebar.text_input("Masukkan kata kunci", '')

if keyword_filter:
    df = df[df['title'].str.contains(keyword_filter, case=False, na=False) | 
            df['summary'].str.contains(keyword_filter, case=False, na=False)]

# -------------------------------
# 1. Tabel Data dari MongoDB
# -------------------------------
st.subheader("📋 Data Artikel dari MongoDB")
st.dataframe(df[['title', 'summary', 'url']], use_container_width=True)

# -------------------------------
# 2. Word Cloud dari Judul
# -------------------------------
st.subheader("Word Cloud dari Judul Artikel")
titles = ' '.join(df['title'].dropna().tolist())
titles_clean = re.sub(r'[^a-zA-Z\s]', '', titles.lower())
tokens = titles_clean.split()
filtered_tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
word_freq_title = Counter(filtered_tokens)
wordcloud_title = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq_title)
fig2, ax2 = plt.subplots(figsize=(10, 5))
ax2.imshow(wordcloud_title, interpolation='bilinear')
ax2.axis('off')
st.pyplot(fig2)

# -------------------------------
# 3. Word Cloud dari Summary
# -------------------------------
st.subheader("Word Cloud dari Summary Artikel")
summaries = ' '.join(df['summary'].dropna().tolist())
summaries_clean = re.sub(r'[^a-zA-Z\s]', '', summaries.lower())
tokens = summaries_clean.split()
filtered_tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
word_freq_summary = Counter(filtered_tokens)
wordcloud_summary = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq_summary)
fig3, ax3 = plt.subplots(figsize=(10, 5))
ax3.imshow(wordcloud_summary, interpolation='bilinear')
ax3.axis('off')
st.pyplot(fig3)

# -------------------------------
# 4. Bar Chart Jumlah Artikel per Kata Kunci
# -------------------------------
st.subheader("Jumlah Artikel per Kata Kunci")
queries = ['diabetes', 'kadar gula', 'buah rendah gula', 'diet', 'obesitas']
keyword_counts = {
    keyword: sum(
        1 for _, row in df.iterrows()
        if keyword.lower() in row['title'].lower() or keyword.lower() in row['url'].lower()
    )
    for keyword in queries
}
fig4, ax4 = plt.subplots(figsize=(10, 6))
ax4.bar(keyword_counts.keys(), keyword_counts.values(), color='skyblue')
ax4.set_title('Jumlah Artikel per Kata Kunci')
ax4.set_xlabel('Kata Kunci')
ax4.set_ylabel('Jumlah Artikel')
st.pyplot(fig4)

st.markdown(f"**Jumlah artikel yang ditampilkan: {len(df)}**")