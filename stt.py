from faster_whisper import WhisperModel
import sounddevice as sd
import numpy as np

class STT:
    def __init__(self,model_size:str="base",device:str="cpu",compute_type:str="int8"):
        self.model_size=model_size
        self.device=device  
        self.compute_type=compute_type
        self.model = WhisperModel(self.model_size, device=self.device,compute_type=self.compute_type)
    def transcribe(self,audio_array):
        segments,info= self.model.transcribe(audio_array)
        return "".join(segment.text for segment in segments )
    def listen(self,timeout:int=5):
        self.sample_rate=16000
        audio=sd.rec(timeout*self.sample_rate,samplerate=self.sample_rate,channels=1,dtype="float32")
        sd.wait()
        audio=audio.flatten()#only neccssary for more than 1 audio channel
        return audio
if __name__=="__main__":
    obj=STT()
    print("listening")
    aud=obj.listen(5)
    say=obj.transcribe(aud)
    print(say)

