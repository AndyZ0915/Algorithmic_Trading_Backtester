"""Free RSS news ingestion using only the Python standard library plus requests."""
import re
import requests
import pandas as pd
from urllib.parse import quote_plus
from xml.etree import ElementTree as ET

class NewsFetcher:
    def search(self, query, limit=20):
        url=f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
        response=requests.get(url,timeout=15,headers={"User-Agent":"QuantResearchPlatform/3.0"})
        response.raise_for_status()
        root=ET.fromstring(response.content)
        rows=[]
        for item in root.findall(".//item")[:limit]:
            def text(tag):
                node=item.find(tag)
                return node.text.strip() if node is not None and node.text else ""
            rows.append({"title":text("title"),"link":text("link"),"published":text("pubDate"),"summary":re.sub(r"<[^>]+>"," ",text("description"))})
        return pd.DataFrame(rows)
