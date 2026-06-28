import sounddevice as sd
import numpy as np
from piper.voice import PiperVoice

# fs=24000
# sd.default.samplerate = 44100
# sd.default.channels = 1
# audio=sd.rec(3*fs)
# sd.wait()
# print("playing recording:")
# sd.play(audio,fs)
# sd.wait()

# for gs,ps,audio in generator:
#     print(audio.shape)
#     print(audio.dtype)

# try:
#     result = next(generator)
#     print("Success!")
#     print(result)
# except StopIteration:
#     print("Generator produced nothing.")
# except Exception as e:
#     print(type(e).__name__, e)
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

