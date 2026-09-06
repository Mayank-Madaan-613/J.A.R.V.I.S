import os
import sys
import time
import datetime
from stt import STT
from websearch import Browser
from geminiapi import gemini
import sounddevice as sd
import soundfile as sf
from tts import TTS 
from clock import Clock
from intent_predict import Predict 
from app_open import app_open
from messaging import What_message
import asyncio 
import numpy as np

class Main:
    def __init__(self):
        self.speaker=TTS()
        self.speech=STT()
        self.browser=Browser()
        self.ai_result=gemini()
        self.predict=Predict()
        self.time=Clock()
        self.app_open=app_open()
        self.what_msg=What_message()
        self.func_dict={"web_search":self.browser.search,"open_app":self.app_open.open,"what_msg":self.what_msg.message,"timer":self.time.timer,"time_rn":self.time.time_rn}
        # data,fs=sf.read("sounds/startup.wav",dtype="float32")
        # loud_data=data*4
        # loud_data=np.clip(loud_data,-1.0,1.0)
        # sd.play(loud_data,fs*0.75)
        sd.wait()
    def type_inp(self,inp):
        intent=self.predict.predict(inp)
        print(intent)
        match intent:
            case "web_search":
                self.browser.search(inp)
            case "open_app":
                self.app_open.open(inp)
            case "what_msg":
                self.what_msg.message(inp)
            case "timer":
                self.speaker.speak("timmer started")
                asyncio.create_task(self.time.start_timer(inp))
            case "time_rn":
                res=self.time.time_rn()
                self.speaker.speak(res)
            case _ :
                self.speaker.speak("ohh! sorry this feature is unavailable at the moment")
        # func_exe=self.func_dict.get(intent)
        # a=func_exe()
        # self.speaker.speak(a)
        return

obj=Main()
while True:
    a=input("test Jarvis: ")
    obj.type_inp(a)










      
# def typein():
#     a=input('Enter')
#     return a
# def voice():
#     try:
#         r=sr.Recognizer()
#         with sr.Microphone() as source:
#             speaker.speak('listening..............')
#             # r.adjust_for_ambient_noise(source)
#             r.pause_threshold=1
#             audio=r.listen(source,timeout=5,phrase_time_limit=7)
#             userspeech=r.recognize_google(audio,language='en-in')
#             print(f'u said:{userspeech}')
#             return userspeech
#     except :
#         print("oops! i coulden't get it....please repeat")
#         voice()
# def action(query):
#     tpsites=[['youtube','https://www.youtube.com/?authuser=0'],['instagram','https://www.instagram.com/']]
#     for i in tpsites:
#         if i[0] in query:
#             wb.open(i[1])
# def playmusic():
#     djo='"C:/Users/Mayank madan/Downloads/End of Beginning - Djo.mp3"'
#     os.startfile(djo)
# def calling():
#     r2=sr.Recognizer()
#     with sr.Microphone() as source:
#         r2.pause_threshold=1
#         audio2=r2.listen(source,timeout=100,phrase_time_limit=10)
#         calling=r2.recognize_google(audio2,language='en-in')
#         return calling

# def main():
#     speaker.speak('starting.............')
#     speaker.speak('greetings')
#     while True:
#         try:
#             q=calling()
#         except:
#             continue
#         if (q.lower()).startswith('jarvis'):
#             a=voice()
#             if (a.lower()).startswith('play'):
#                 playmusic()
#                 continue
#             elif (a.lower()).startswith('open'):#include pattern matching 
#                 action(a.lower())
#                 continue
#             elif (a.lower()).startswith('send a message'):
#                 sendmsg()
#                 continue
#             elif "ai mode" in a.lower():
#                 a=gemini()
#             elif "that's all" in a.lower():
#                 speaker.speak('Signing off')
#                 sys.exit()
#             else:
#                 speaker.speak("I'am afraid that i cant't do that...")
#                 continue
