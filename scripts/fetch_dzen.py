import json
import urllib.request
import os
import re

# Используем сервис-посредник, который Дзен не блокирует
API_URL = "https://api.rss2json.com/v1/api.json?rss_url=https://dzen.ru/endo_dok/rss&count=6"
OUTPUT_FILE = "dzen-articles.json"

def main():
    # Загружаем старые данные на случай ошибки
    old_data = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                old_data = json.load(f)
        except: pass

    try:
        req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
        
        if data.get('status') == 'ok':
            articles = []
            for item in data.get('items', []):
                # Ищем картинку
                img = item.get('thumbnail', '') or item.get('enclosure', {}).get('link', '')
                
                # Очищаем текст от лишних символов
                clean_desc = re.sub(r'<[^>]+>', ' ', item.get('description', ''))
                clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
                if len(clean_desc) > 200: clean_desc = clean_desc[:200] + "..."

                articles.append({
                    "title": item.get('title', ''),
                    "link": item.get('link', ''),
                    "pubDate": item.get('pubDate', ''),
                    "description": clean_desc,
                    "image": img
                })
            
            if articles:
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(articles, f, ensure_ascii=False, indent=2)
                print(f"✅ Скачано статей: {len(articles)}")
            else:
                print("⚠️ Статьи не найдены, оставляем старые")
        else:
            print("⚠️ Сервис вернул ошибку, оставляем старые данные")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
