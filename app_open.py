from AppOpener import open
import re
class app_open:
    def __init__(self,query):
        pattern_website=( r'\b(?:open|fireup|launch|visit|go\s+to)?\s*' r'[\s,.:;-]*'r'(?:the\s+)?'r'(?:website\s+)?'r'([a-zA-Z0-9.-]+)'r'(?:\s+website)?\b')
        self.app=re.search(pattern_website,query,re.IGNORECASE)
        if self.app:
            open(self.app.group(1), match_closest=True)
            self.msg=""
        else:
            self.msg="Sorry i could not find the App."


