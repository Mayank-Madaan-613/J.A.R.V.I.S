import pywhatkit
import datetime
import re 
import asyncio

class What_message:
    def __init__(self):
        self.contacts={"me":"+919211168123"}
    def extract_info(self, text):
        clean_text = text.strip()

        patterns = [
            r"(?:send\s+a\s+)?(?:whatsapp|whatapp|what's\s+app|msg|message)?\s*(?:message|msg)?\s*to\s+(?P<contact>[\w\s]+?)\s+(?:that\s+says|saying)\s+(?P<message>.+)",
            
            r"(?:tell|text|message|whatsapp)\s+(?P<contact>[\w\s]+?)\s+(?:on\s+(?:whatsapp|whatapp|what's\s+app)\s+)?(?:that|saying)\s+(?P<message>.+)",
            
            r"(?:whatsapp|whatapp)\s+(?:message|msg)?\s*to\s+(?P<contact>[\w\s]+?)\s+(?:that\s+says|that|saying)\s+(?P<message>.+)",
            
            r"to\s+(?P<contact>\w+)\s+(?P<message>.+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                contact = match.group("contact").strip()
                message = match.group("message").strip()
                contact = re.sub(r"\b(on|via|using)\s+(whatsapp|whatapp|what's\s+app)\b", "", contact, flags=re.IGNORECASE).strip()
                
                return {
                    "contact": contact,
                    "message": message
                }

        return {"contact": None, "message": None}
           
        
    def message(self, input):
        main_dict=self.extract_info(input)
        self.contact=main_dict.get("contact")
        self.message=main_dict.get("message")
        print(self.contact,"--",self.message)
        if self.contact.lower() in self.contacts:
            date=datetime.datetime.now()
            current_time=(str((date).time())).split(':')
            pywhatkit.sendwhatmsg_instantly(self.contacts[self.contact],self.message)
            print("message sent")

if __name__=="__main__":
    a=What_message()
    a.message("send a message to me saying good morning")
    