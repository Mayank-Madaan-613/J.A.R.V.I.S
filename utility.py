from geminiapi import AI_search
import webbrowser as wb
import customtkinter as ct
import win32com.client as wc
import speech_recognition as sr
import os
import sys
import pywhatkit
import datetime
from google import genai
speaker=wc.Dispatch('SAPI.SpVoice')
def typein():
    a=input('Enter')
    return a
def voice():
    try:
        r=sr.Recognizer()
        with sr.Microphone() as source:
            speaker.speak('listening..............')
            # r.adjust_for_ambient_noise(source)
            r.pause_threshold=1
            audio=r.listen(source,timeout=5,phrase_time_limit=7)
            userspeech=r.recognize_google(audio,language='en-in')
            print(f'u said:{userspeech}')
            return userspeech
    except :
        print("oops! i coulden't get it....please repeat")
        return voice()
def action(query):
    tpsites=[['youtube','https://www.youtube.com/?authuser=0'],['instagram','https://www.instagram.com/']]
    for i in tpsites:
        if i[0] in query.lower():
            wb.open(i[1])
def playmusic():
    djo='"C:/Users/Mayank madan/Downloads/End of Beginning - Djo.mp3"'
    os.startfile(djo)
def calling():
    r2=sr.Recognizer()
    with sr.Microphone() as source:
        r2.pause_threshold=1
        audio2=r2.listen(source,timeout=100,phrase_time_limit=10)
        calling=r2.recognize_google(audio2,language='en-in')
        return(calling)
def sendmsg():
    speaker.speak('may i know the contact name')
    contact=voice()
    if 'type' in contact:
        contact=typein()
    print(contact)
    speaker.speak('kindly tell the message')
    msg=voice()
    if 'type' in msg:
        msg=typein()
    savedcontacts={'jayant':'+917983060701','mayank':'+919211168123','vartul':'+919509574204','rohan':'+919953111446'}
    current_time=(str((datetime.datetime.now()).time())).split(':')
    for i in savedcontacts:
        if i in contact.lower():
            pywhatkit.sendwhatmsg(savedcontacts[contact.lower()],msg,int(current_time[0]),int(current_time[1])+1)
            speaker.speak('processing......the msg will be delivered soon....')
            return
        else: 
            speaker.speak('sorry i cant\'t find the contact')
            return
class gemini:
    def __init__(self):
        speaker.speak("turning on search mode...........")
        speaker.speak("what is your query sir?")
        hearingobj=voice()
        response=AI_search(hearingobj)
        speaker.speak(response)
def main():
    speaker.speak('starting.............')
    speaker.speak('greetings')
    while True:
        try:
            q=calling()
        except:
            continue
        if (q.lower()).startswith('hello'):
            a=voice()
            if (a.lower()).startswith('play'):
                playmusic()
                continue
            elif (a.lower()).startswith('open'):#include pattern matching 
                action(a.lower())
                continue
            elif (a.lower()).startswith('send a message'):
                sendmsg()
                continue
            elif "ai mode" in a.lower():
                a=gemini()

            elif "that's all" in a.lower():
                speaker.speak('Signing off')
                sys.exit()
            else:
                speaker.speak("I'am afraid that i cant't do that...")
                continue

main()
