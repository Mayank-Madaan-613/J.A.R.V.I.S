"""
listener.py - 100% local, sequential 3-stage listening pipeline.

  IDLE        : OpenWakeWord only. VAD / Whisper are not touched.
  RECORDING   : Silero VAD (ONNX) on every 32 ms frame. A pre-roll ring buffer
                guarantees the first soft consonant is never clipped.
  PROCESSING  : after 2.0 s of silence -> trim tail -> faster-whisper (on demand).

pip install sounddevice numpy onnxruntime openwakeword
(STT comes from your own stt.py - see _transcribe)
"""
import math
import queue
import time
import urllib.request
from collections import deque
from enum import Enum, auto
from pathlib import Path
import soundfile as sf
import numpy as np
import onnxruntime as ort
import openwakeword
import sounddevice as sd
from openwakeword.model import Model

SR = 16000
FRAME = 512          # 32 ms @ 16 kHz - the only chunk size Silero v5 accepts at 16 kHz
FRAME_MS = 32
WAKE_CHUNK = 1280    # 80 ms - the chunk size OpenWakeWord is built around

SILERO_URL = ("https://github.com/snakers4/silero-vad/raw/master/"
              "src/silero_vad/data/silero_vad.onnx")


class State(Enum):
    IDLE = auto()
    RECORDING = auto()
    PROCESSING = auto()


class SileroVAD:
    """Thin ONNX Runtime wrapper (no torch). Silero VAD v5: 512-sample frames + 64-sample context."""

    def __init__(self, model_path: Path):
        
        model_path = Path(model_path)
        if not model_path.exists():
            model_path.parent.mkdir(parents=True, exist_ok=True)
            print("[vad] downloading silero_vad.onnx ...")
            urllib.request.urlretrieve(SILERO_URL, model_path)
        opts = ort.SessionOptions()
        opts.inter_op_num_threads = 1
        opts.intra_op_num_threads = 1
        self.sess = ort.InferenceSession(str(model_path), sess_options=opts,
                                         providers=["CPUExecutionProvider"])
        self._sr = np.array(SR, dtype=np.int64)
        self.reset()

    def reset(self):
        self.state = np.zeros((2, 1, 128), dtype=np.float32)
        self.context = np.zeros((1, 64), dtype=np.float32)

    def __call__(self, frame_i16: np.ndarray) -> float:
        x = frame_i16.astype(np.float32) / 32768.0
        x = np.concatenate([self.context, x[None, :]], axis=1)   # (1, 576)
        out, self.state = self.sess.run(
            None, {"input": x, "state": self.state, "sr": self._sr})
        self.context = x[:, -64:]
        return float(out[0, 0])


class VoiceListener:
    def __init__(
        self,
        wake_word="hey_jarvis",
        wake_threshold=0.3,
        stt=None,                      # your STT instance from stt.py (created here if None)
        silence_end_s=1.5,             # silence after speech that ends the turn
        preroll_ms=500,
        no_speech_timeout_s=6.0,       # woke up but user said nothing -> back to IDLE
        max_record_s=30.0,
        vad_on=0.5,                    # prob to count as speech
        vad_off=0.35,                  # prob below which a frame counts as silence (hysteresis)
        min_speech_frames=3,           # ~96 ms of voiced frames before we call it "speech started"
        tail_pad_ms=300,               # keep a little silence after the last word
        min_utterance_s=0.3,
        vad_model_path="models/silero_vad.onnx",
        on_wake=None,                  # callback, e.g. play the listening chime
    ):
        openwakeword.utils.download_models(model_names=[wake_word])
        self.wake = Model(wakeword_models=[wake_word], inference_framework="onnx")
        self.wake_threshold = wake_threshold

        self.vad = SileroVAD(vad_model_path)
        self.vad_on, self.vad_off = vad_on, vad_off
        self.min_speech_frames = min_speech_frames

        self.silence_frames = math.ceil(silence_end_s * 1000 / FRAME_MS)       # 2.0 s -> 63 frames
        self.preroll_frames = math.ceil(preroll_ms / FRAME_MS)                 # 500 ms -> 16 frames
        self.tail_pad_frames = math.ceil(tail_pad_ms / FRAME_MS)
        self.no_speech_timeout_s = no_speech_timeout_s
        self.max_record_s = max_record_s
        self.min_utterance_s = min_utterance_s
        self.on_wake = on_wake

        self.data,self.fs=sf.read("sounds/listening.wav",dtype='float32')

        # Your STT model is loaded once (RAM only) but only *executed* at end-of-turn.
        if stt is None:
            from stt import STT
            stt = STT()
        self.stt = stt

        self.state = State.IDLE
        self._q: "queue.Queue[bytes]" = queue.Queue(maxsize=600)   # ~19 s of audio
        self._stream = None

    # ------------------------------------------------------------------ audio
    def _callback(self, indata, frames, t, status):
        try:
            self._q.put_nowait(bytes(indata))
        except queue.Full:
            pass  # never block the audio thread

    def start(self):
        if self._stream is None:
            self._stream = sd.RawInputStream(
                samplerate=SR, channels=1, dtype="int16",
                blocksize=FRAME, callback=self._callback)
            self._stream.start()

    def stop(self):
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def _read(self) -> np.ndarray:
        return np.frombuffer(self._q.get(timeout=2.0), dtype=np.int16)

    def _drain(self):
        try:
            while True:
                self._q.get_nowait()
        except queue.Empty:
            pass

    # ----------------------------------------------------------------- stage 1
    def _wait_for_wake(self):
        self.state = State.IDLE
        self._drain()            # throw away anything captured while we were speaking / thinking
        self.wake.reset()
        print("\n[IDLE] Waiting for wake word 'Hey Jarvis'...")
        buf = np.empty(0, dtype=np.int16)
        while True:
            buf = np.concatenate([buf, self._read()])
            while len(buf) >= WAKE_CHUNK:
                chunk, buf = buf[:WAKE_CHUNK], buf[WAKE_CHUNK:]
                scores = self.wake.predict(chunk)
                score = max(scores.values())
                if score >= self.wake_threshold:
                    print(f"[WAKE] Wake word detected (confidence {score:.2f})")
                    return

    # ----------------------------------------------------------------- stage 2
    def _record(self):
        """Returns int16 audio of the utterance (pre-roll + speech + small tail), or None."""
        self.state = State.RECORDING
        self.vad.reset()
        sd.play(self.data,self.fs)
        print("[LISTENING] Speak now...")

        # Pre-roll is the rolling window of the last ~500 ms *before speech onset*.
        # +min_speech_frames because the onset frames themselves are already in it.
        preroll = deque(maxlen=self.preroll_frames + self.min_speech_frames)
        frames = []
        started = False
        voiced_run = 0
        silence_run = 0
        t0 = time.monotonic()

        while True:
            frame = self._read()
            p = self.vad(frame)

            if not started:
                preroll.append(frame)
                voiced_run = voiced_run + 1 if p >= self.vad_on else 0
                if voiced_run >= self.min_speech_frames:
                    started = True
                    print("[LISTENING] Speech detected, recording...")
                    frames = list(preroll)      # prepend the history
                    silence_run = 0
                elif time.monotonic() - t0 > self.no_speech_timeout_s:
                    print("[TIMEOUT] No speech heard, going back to sleep")
                    return None
                continue

            frames.append(frame)
            silence_run = silence_run + 1 if p < self.vad_off else 0

            if silence_run >= self.silence_frames:
                print(f"[LISTENING] {self.silence_frames * FRAME_MS / 1000:.1f}s of silence, end of turn")
                break
            if len(frames) * FRAME / SR > self.max_record_s:
                break

        # ------------------------------------------------------------- stage 3 prep
        # Freeze + trim trailing silence (keep a short pad so the last word isn't cut).
        trim = max(0, silence_run - self.tail_pad_frames)
        frames = frames[: len(frames) - trim]
        audio = np.concatenate(frames)
        if len(audio) / SR < self.min_utterance_s:
            print("[SKIP] Too short, ignoring")
            return None
        print(f"[RECORDED] Captured {len(audio) / SR:.1f}s of audio")
        return audio

    # ----------------------------------------------------------------- stage 3
    def _transcribe(self, audio_i16: np.ndarray) -> str:
        """Hands the utterance to your STT class.

        ADAPTER: edit the one marked line to match your stt.py method.
        It receives a mono 16 kHz float32 numpy array in [-1, 1].
        """
        self.state = State.PROCESSING
        print("[PROCESSING] Transcribing...")
        t0 = time.monotonic()
        audio = audio_i16.astype(np.float32) / 32768.0

        result = self.stt.transcribe(audio)          # <-- change method name here if needed
        print(f"[PROCESSING] Done in {time.monotonic() - t0:.2f}s")

        # Normalise whatever your STT returns into a plain string.
        if isinstance(result, tuple):                # e.g. faster-whisper (segments, info)
            result = result[0]
        if isinstance(result, str):
            return result.strip()
        return " ".join(getattr(s, "text", str(s)).strip() for s in result).strip()

    # -------------------------------------------------------------------- API
    def next_utterance(self) -> str:
        """Blocks until: wake word -> speech -> 2 s silence -> transcript. Returns the text."""
        self.start()
        while True:
            self._wait_for_wake()
            if self.on_wake:
                self.on_wake()          # e.g. chime; blocking is fine
            self._drain()               # don't record our own chime
            audio = self._record()
            if audio is None:           # timeout / too short -> back to IDLE
                continue
            text = self._transcribe(audio)
            if text:
                print(f"[HEARD] \"{text}\"")
                return text
            print("[SKIP] Nothing intelligible heard")

    def listen_forever(self):
        while True:
            yield self.next_utterance()


_listener = None


def get_user_speech(stt=None, on_wake=None) -> str:
    """Blocks through wake word -> recording -> transcription and returns ONLY the text.

    Hand the result to your router, e.g. router(get_user_speech()).
    The VoiceListener is created once on first call and reused afterwards.
    """
    global _listener
    if _listener is None:
        _listener = VoiceListener(stt=stt, on_wake=on_wake)
    return _listener.next_utterance()


if __name__ == "__main__":
    while True:
        print("You said:", get_user_speech())