import json
import os
import re
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime

RSS_URL = "https://dzen.ru/endo_dok/rss"
OUTPUT_FILE = "dzen-articles.json"
MAX_ARTICLES = 6

def fetch_rss():
    """Скачивает RSS-ленту Дзена."""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; DzenRSSBot/1.0)"
    }
    req = urllib.request.Request(RSS_URL, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()

def parse_rss(xml_data):
    """Парсит XML и извлекает статьи."""
    root = ET.fromstring(xml_data)
    articles = []
    
    for item in root.iter("item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        pub_date = item.findtext("pubDate", "").strip()
        description = item.findtext("description", "").strip()
        
        # Ищем картинку: сначала в enclosure, потом в description
        image_url = ""
        enclosure = item.find("enclosure")
        if enclosure is not None:
            image_url = enclosure.get("url", "")
        
        if not image_url:
            img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', description)
            if img_match:
                image_url = img_match.group(1)
        
        # Очищаем описание от HTML для короткого анонса
        clean_desc = re.sub(r'<[^>]+>', ' ', description)
        clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
        if len(clean_desc) > 200:
            clean_desc = clean_desc[:200] + "..."
        
        if title and link:
            articles.append({
                "title": title,
                "link": link,
                "pubDate": pub_date,
                "description": clean_desc,
                "image": image_url
            })
        
        if len(articles) >= MAX_ARTICLES:
            break
    
    return articles

def main():
    # Если файл уже существует, загружаем старые данные как резерв
    old_data = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                old_data = json.load(f)
        except Exception:
            old_data = []
    
    try:
        xml_data = fetch_rss()
        articles = parse_rss(xml_data)
        
        if not articles:
            print("⚠️ RSS пуст, оставляем старые данные")
            articles = old_data
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Сохранено {len(articles)} статей")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        # При ошибке оставляем старые данные
        if old_data:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(old_data, f, ensure_ascii=False, indent=2)
            print("📦 Использованы старые данные")

if __name__ == "__main__":
    main()
