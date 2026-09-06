import pywhatkit
import datetime
class What_message:
    def __init__(self):
        self.contacts={"mayank":"+919211168123","papa":"+919811168123"}
    def message(self, contact,message):
        date=datetime.datetime.now()
        current_time=(str((date).time())).split(':')
        if contact.lower() in self.contacts:
            pywhatkit.sendwhatmsg_instantly(self.contacts[contact],message)
    def schedule_msg(self,contact,message,inp_time):
        #inp_inp_time=[hour,min]
        if contact.lower() in self.contacts:
            date=datetime.datetime.now()
            current_time=str((date).time()).split(":")
            pywhatkit.sendwhatmsg(self.contacts[contact],message,inp_time[0],inp_time[1])

if __name__=="__main__":
    a=What_message()
    a.message("mayank","hello jii")