import pywhatkit
import datetime
import re 
import asyncio

class What_message:
    def __init__(self):
        self.contacts={"mayank":"+919211168123","papa":"+919811168123"}
    def extract_info(self, query):
        pattern = r"(?:send|text|message)\s+(?:a\s+)?(?:message\s+)?(?:to\s+)?(?P<contact>.+?)\s+(?:saying|that\s+says|:)\s*(?P<message>.+)"
        match=re.search(pattern,query,re.IGNORECASE)
        if match:
            return match.groupdict()
           
        
    def message(self, input):
        main_dict=self.extract_info(input)
        contact=main_dict.get("contact")
        message=main_dict.get("message")
        print(contact," ",message)
        print("req rcvd")
        if contact.lower() in self.contacts:
            date=datetime.datetime.now()
            current_time=(str((date).time())).split(':')
            print("req rcvd")
            pywhatkit.sendwhatmsg_instantly(self.contacts[contact],message)
            print("sent")
    def schedule_msg(self,input,inp_time):
        #inp_inp_time=[hour,min]
        contact,message=self.extract_info
        if contact.lower() in self.contacts:
            date=datetime.datetime.now()
            current_time=str((date).time()).split(":")
            pywhatkit.sendwhatmsg(self.contacts[contact],message,inp_time[0],inp_time[1])

if __name__=="__main__":
    a=What_message()
    a.message("mayank","hello jii")