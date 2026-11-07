import os
import sys
import time
import datetime
import openwakeword
from openwakeword.model import Model
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
import threading
import pyaudio
import listener as ls
import calculate as clc
from guesture import gesture
pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1280)
speaker=TTS()
speech=STT()
listen_aud,fs=sf.read("sounds/listening.wav",dtype="float32")
rm_aud=fs*0.5
listen_aud=listen_aud[:-int(rm_aud)]
class Main:
    def __init__(self):
        print("initializing")
        self.browser=Browser()
        self.ai_result=gemini()
        self.predict=Predict()
        self.time=Clock()
        self.ges_obj=gesture()
        self.app_open=app_open()
        self.what_msg=What_message()
        data,fs=sf.read("sounds/startup.wav",dtype="float32")
        loud_data=data*4
        loud_data=np.clip(loud_data,-1.0,1.0)
        sd.play(loud_data,fs*0.75)
        sd.wait()
  
    def executor(self,inp):
        intent=self.predict.predict(inp)
        print(intent)
        match intent:
            case "web_search":
                self.browser.search(inp)
            case "open_app":
                self.app_open.open(inp)
            case "what_msg":
                print("sending message")
                self.what_msg.message(inp)
                speaker
            case "timer":
                speaker.speak("timer started")
                self.time.timer_call(inp)
            case "calculate":
                result=clc.extract_math_components(inp)
                res=result.get("res")
                speaker.speak(f"It comes out to be {res}")
            case "gesture_mode":
                print(self.ges_obj)
                self.ges_obj.run_tracking()
            case "time_rn":
                res=self.time.time_rn()
                speaker.speak(res)
            case _ :
                speaker.speak("ohh! sorry this feature is unavailable at the moment")
        return

obj=Main()
while True:
     command=ls.get_user_speech()
     obj.executor(command)

