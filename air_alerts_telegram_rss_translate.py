import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import xml.etree.ElementTree as ET
from datetime import datetime

# Telegram channel URL
TELEGRAM_URL = "https://t.me/s/air_alert_ua"

# Scrape the elements from the page    
response = requests.get(TELEGRAM_URL)
soup = BeautifulSoup(response.text, "html.parser")

# Extract relevant elements and limit to 20
posts = [post.get_text() for post in reversed(soup.find_all("div", class_="tgme_widget_message_text"))][:20]
links = [link.get("href") for link in reversed(soup.find_all("a", class_="tgme_widget_message_date"))][:20]
times = [time.get("datetime") for time in reversed(soup.find_all("time", class_="time"))][:20]

# Translate the posts
translated_items = [
    GoogleTranslator(source='uk', target='en').translate(post) for post in posts
]

# Generate RSS feed
rss = ET.Element("rss")
rss.set("version", "2.0")
channel = ET.SubElement(rss, "channel")
ET.SubElement(channel, "title").text = "Translated Air Alert UA"
ET.SubElement(channel, "link").text = TELEGRAM_URL
ET.SubElement(channel, "description").text = "Translated Alerts from Air Alert UA"

for translated, link, time in zip(translated_items, links, times):
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = translated.split('#')[0].strip()
    ET.SubElement(item, "link").text = link
    ET.SubElement(item, "description").text = (
        translated +
        ' This is a warning from the official Ukrainian Air Monitoring System and may indicate a potential or imminent airstrike or other threat.'
    )
    # Parse the ISO 8601 datetime string
    dt = datetime.fromisoformat(time)
    # Format it for RSS (RFC 822/1123)
    rss_datetime = dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
    ET.SubElement(item, "pubDate").text = rss_datetime

# Save RSS feed to file
tree = ET.ElementTree(rss)
tree.write("air_alerts_telegram_feed.xml", encoding="utf-8", xml_declaration=True)
