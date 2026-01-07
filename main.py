import feedparser
import requests
import time
from newspaper import Article
from nltk.tokenize import sent_tokenize
import nltk
import os

# Télécharger punkt pour résumé
nltk.download('punkt')

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("8501088953:AAG-zXQRokaJ7sK3nFXkiTJN7v6aRgmAHwk")
CHAT_ID = os.getenv("@spotnews_world_ar")
MAX_SUMMARY_SENTENCES = 3
# ============================================

RSS_FEEDS = [
    "https://www.aljazeera.net/aljazeerarss",
    "https://feeds.bbci.co.uk/arabic/rss.xml",
    "https://news.google.com/rss?hl=ar&gl=US&ceid=US:ar"
]

posted_links = set()

def summarize_arabic(text, max_sentences=3):
    sentences = sent_tokenize(text)
    return " ".join(sentences[:max_sentences])

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": False
    }
    requests.post(url, data=payload)

def process_feed(feed_url):
    feed = feedparser.parse(feed_url)

    for entry in feed.entries[:3]:
        if entry.link in posted_links:
            continue

        try:
            article = Article(entry.link, language='ar')
            article.download()
            article.parse()

            if len(article.text) < 300:
                continue

            summary = summarize_arabic(article.text, MAX_SUMMARY_SENTENCES)

            message = (
                "🌍 خبر دولي\n\n"
                f"📰 {entry.title}\n\n"
                f"📝 الملخص:\n{summary}\n\n"
                f"🔗 المصدر:\n{entry.link}"
            )

            send_to_telegram(message)
            posted_links.add(entry.link)

            time.sleep(10)

        except Exception:
            continue

def run_bot():
    for rss in RSS_FEEDS:
        process_feed(rss)

# Boucle infinie toutes les 20 minutes
while True:
    run_bot()
    time.sleep(1200)  # 20 minutes

