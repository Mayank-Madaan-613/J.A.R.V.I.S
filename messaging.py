import pywhatkit
import datetime
class What_message:
    contacts={"mayank":"+919211168123"}
    def __init__(self,contact,message):
        self.date=datetime.datetime.now()
        self.current_time=(str((self.date).time())).split(':')
        if contact.lower() in What_message.contacts:
            pywhatkit.sendwhatmsg(self.contacts[contact],message,int(self.current_time[0]),int(self.current_time[1])+2)
if __name__=="__main__":
    What_message("mayank","hey there")