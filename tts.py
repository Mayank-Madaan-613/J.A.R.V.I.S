# import os
# import sys
# import openvino

# # Explicitly register OpenVINO's C++ DLL folder on Windows before importing onnxruntime
# print(os.path)
# ov_libs = os.path.join(os.path.dirname(openvino.__file__), "libs")
# if os.path.isdir(ov_libs):
#     os.add_dll_directory(ov_libs)
#     os.environ["PATH"] = ov_libs + os.pathsep + os.environ.get("PATH", "")

import sounddevice as sd
import numpy as np
import onnxruntime as ort
from kokoro_onnx import Kokoro

class TTS:
    def __init__(self):
        self.tts=Kokoro("voices/kokoro-v1.0.onnx","voices/voices-v1.0.bin")
        self.tts.sess = ort.InferenceSession("voices/kokoro-v1.0.onnx")
    def speak(self,inp:str):
        self.samples, self.sample_rate = self.tts.create(
            inp,
            voice="af_heart",
            speed=1.0,
            lang="en-us"
        )
        sd.play(self.samples, self.sample_rate)
        sd.wait()

if __name__=="__main__":
    obj=TTS()
    obj.speak("hello ther how are you, this is being run on CPU and it's kind of better than piper.")
    obj.speak("this is the testing for the new upgrade in JARVIS")