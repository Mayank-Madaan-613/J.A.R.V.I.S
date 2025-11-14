import webbrowser as wb
import customtkinter as ct
import win32com.client as wc
import speech_recognition as sr
import os
import sys
import pywhatkit
import datetime
speaker=wc.Dispatch('SAPI.SpVoice')
def voice():
    try:
        r=sr.Recognizer()
        with sr.Microphone() as source:
            speaker.speak('listening..............')
            r.adjust_for_ambient_noise(source)
            r.pause_threshold=1
            audio=r.listen(source,timeout=5,phrase_time_limit=7)
            userspeech=r.recognize_google(audio,language='en-in')
            print(f'u said:{userspeech}')
            return userspeech
    except :
        print("oops! i coulden't get it....please repeat")
        voice()
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
        calling=r2.recognize_google(audio2)
        return(calling)
def sendmsg():
    speaker.speak('may i know the contact name')
    contact=voice()
    speaker.speak('kindly tell the message')
    msg=voice()
    savedcontacts={'Ananya':'+919811768123','Mayank':'+919211168123','Papa':'+919811168123'}
    current_time=(str((datetime.datetime.now()).time())).split(':')

    if contact in savedcontacts:
        pywhatkit.sendwhatmsg(savedcontacts[contact],msg,int(current_time[0],int(current_time[1])+1))
        speaker.speak('processing......the msg will be delivered soon....')
    else: 
        speaker.speak('sorrt i cant\'t find the contact')
        return
def main():
    speaker.speak('starting.............')
    speaker.speak('welcome')
    while True:
        try:
            q=calling()
        except:
            continue
        if (q.lower()).startswith('hey jarvis'):
    
            a=voice()
            if (a.lower()).startswith('play'):
                playmusic()
            elif (a.lower()).startswith('open'):
                action(a.lower())
            elif (a.lower()).startswith('send a message'):
                sendmsg()
            elif "that's all" in a.lower():
                speaker.speak('Signing off')
                sys.exit()
            
            else:
                speaker.speak("I'am afraid that i cant't do that...")
                continue
            
        # except:
        #     print('some error occured......')
        #     main()
sendmsg()
# main()
# voice()