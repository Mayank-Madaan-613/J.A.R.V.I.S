from faster_whisper import WhisperModel
import sounddevice as sd
import numpy as np
import queue
class STT:
    def __init__(self,model_size:str="base",device:str="cpu",compute_type:str="int8"):
        self.model_size=model_size
        self.device=device  
        self.compute_type=compute_type
        self.model = WhisperModel(self.model_size, device=self.device,compute_type=self.compute_type)
    def transcribe(self,audio_array):
        segments,info= self.model.transcribe(audio_array,language="en",beam_size=1,condition_on_previous_text=False)#for better accuracy change beam size to 5
        return "".join(segment.text for segment in segments )
if __name__=="__main__":
    obj=STT()
    print("listening")
    aud=obj.listen()
    say=obj.transcribe(aud)
    print(say)

