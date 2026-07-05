import sounddevice as sd
import numpy as np
from piper.voice import PiperVoice

class TTS:
    def __init__(self):
        self.stream =sd.OutputStream(samplerate=22050,channels=1,dtype=np.int16)
        self.voice = PiperVoice.load("voices/female/en_US-amy-medium.onnx")
        self.stream.start()
    def speak(self,cmd:str):
        for chunk in self.voice.synthesize(cmd):
            self.stream.write(np.frombuffer(chunk.audio_int16_bytes,dtype=np.int16))
    def close(self):
        self.stream.stop()
        self.stream.close()
