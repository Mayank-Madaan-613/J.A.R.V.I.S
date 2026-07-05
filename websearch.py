import webbrowser as wb
import re
from stt import STT
class Browser:
    listed_sites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "github": "https://github.com",
        "gmail": "https://mail.google.com",
        "chatgpt": "https://chat.openai.com",
        "leetcode": "https://leetcode.com",
        "linkedin": "https://www.linkedin.com",
    }
    def search(self,query):
        wb.open(query+" ")
    def open_site(self,query):
        query=query.lower()
        pattern_website=( r'\b(?:open|launch|visit|go\s+to)?\s*' r'[\s,.:;-]*'r'(?:the\s+)?'r'(?:website\s+)?'r'([a-zA-Z0-9.-]+)'r'(?:\s+website)?\b')
        site=re.search(pattern_website,query,re.IGNORECASE)
        print(site)
        if site and site.group(1) in self.listed_sites:
            wb.open(self.listed_sites[site.group(1)])
        elif site:
            self.search(site.group(1))

