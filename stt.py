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
        segments,info= self.model.transcribe(audio_array)
        return "".join(segment.text for segment in segments )
    def listen(self,timeout:int=15):
        self.sample_rate=16000
        q=queue.Queue

        def callback(indata, frames, status):
            q.put(indata.copy())
        chunk_duration=0.1
        chunk_size=int (chunk_duration*self.sample_rate)
        req_silent_chunks=int(2/chunk_size)
        audio=[]
        silent_count=0
        energy_threshold=0.03
        with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype="float32", 
                                    blocksize=chunk_size, callback=callback):
            while True:
                aud_chunk=q.get()
                audio.append(aud_chunk)
                rms = np.sqrt(np.mean(aud_chunk**2))
                if rms > energy_threshold:
                    speaking=True
                    silent_count=0
                else:
                    silent_count+=1
                if silent_count>=req_silent_chunks:
                    print("silence detected")
                    break
            if len(audio) > req_silent_chunks:
                    trimmed_chunks = audio[:-req_silent_chunks]
            else:
                    trimmed_chunks = audio 
                                                                                
        final_audio_array = np.concatenate(trimmed_chunks, axis=0).flatten()# Flatten into the final array for whisper
        return final_audio_array
if __name__=="__main__":
    obj=STT()
    print("listening")
    aud=obj.listen()
    say=obj.transcribe(aud)
    print(say)

