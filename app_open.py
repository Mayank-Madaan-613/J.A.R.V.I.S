from AppOpener import open
import re
from websearch import Browser
class app_open:
    def open(self,query):
        self.browser=Browser()
        pattern_website=( r'\b(?:open|fireup|launch|visit|go\s+to)?\s*' r'[\s,.:;-]*'r'(?:the\s+)?'r'(?:website\s+)?'r'([a-zA-Z0-9.-]+)'r'(?:\s+website)?\b')
        self.app=re.search(pattern_website,query,re.IGNORECASE)
        if self.app:
            try:
                open(self.app.group(1), throw_error=True)
                return ""
            except:
                self.browser.open_site(self.app.group(1))
                return ""
        else:
            return "Sorry i could not find the App."


