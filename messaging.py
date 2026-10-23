import pywhatkit
import datetime
import re 
import asyncio

class What_message:
    def __init__(self):
        self.contacts={"mayank":"+919211168123"}
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
        contact=main_dict.get("contact")
        message=main_dict.get("message")
        print(contact," ",message)
        if contact.lower() in self.contacts:
            date=datetime.datetime.now()
            current_time=(str((date).time())).split(':')
            pywhatkit.sendwhatmsg_instantly(self.contacts[contact],message)
            print("message sent")
    def schedule_msg(self,input,inp_time):
        #inp_inp_time=[hour,min]
        contact,message=self.extract_info
        if contact.lower() in self.contacts:
            date=datetime.datetime.now()
            current_time=str((date).time()).split(":")
            pywhatkit.sendwhatmsg(self.contacts[contact],message,inp_time[0],inp_time[1])

if __name__=="__main__":
    a=What_message()
    print(a.extract_info("send a message to rahul saying good morning"))
    