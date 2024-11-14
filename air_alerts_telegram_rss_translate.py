import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import xml.etree.ElementTree as ET
from datetime import datetime

# Telegram channel URL
TELEGRAM_URL = "https://t.me/s/air_alert_ua"

def scrape_telegram():
    response = requests.get(TELEGRAM_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    posts = soup.find_all("div", class_="tgme_widget_message_text")
    posts = list(reversed(posts))  # Reverse the order to ensure newest messages are processed first

    items = []
    for post in posts[:20]:  # Limit to the latest 20 messages
        original_text = post.get_text()
        translated_text = GoogleTranslator(source='uk', target='en').translate(original_text)
        items.append((original_text, translated_text))

    return items

def generate_rss(items):
    rss = ET.Element("rss")
    rss.set("version", "2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Translated Air Alert UA"
    ET.SubElement(channel, "link").text = TELEGRAM_URL
    ET.SubElement(channel, "description").text = "Translated Alerts from Air Alert UA"

    for original, translated in items:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = translated[:5000]  # Truncate title to 5000 chars
        ET.SubElement(item, "link").text = TELEGRAM_URL
        ET.SubElement(item, "description").text = translated
        ET.SubElement(item, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

    tree = ET.ElementTree(rss)
    tree.write("air_alerts_telegram_feed.xml", encoding="utf-8", xml_declaration=True)

# Run the scraping and RSS generation
items = scrape_telegram()
generate_rss(items)

# Run the scraping and RSS generation
items = scrape_telegram()
generate_rss(items)

# Verify file creation
import os
print("File exists:", os.path.exists("air_alerts_telegram_feed.xml"))
