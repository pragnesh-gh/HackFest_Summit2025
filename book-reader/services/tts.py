# services/tts.py
import threading
import sounddevice as sd
from kokoro import KPipeline

class TTSPlayer:
    """
    Text-to-Speech player using Kokoro's KPipeline and sounddevice for audio playback.
    """
    def __init__(self, voice: str = 'af_heart', speed: float = 1.0, split_pattern: str = r"\s+"):
        self.pipeline = KPipeline(lang_code='a')
        self.voice = voice
        self.speed = speed
        self.split_pattern = split_pattern
        self._thread = None
        self._stop_event = threading.Event()

    def speak(self, text: str):
        """
        Speak the given text asynchronously. Stops any ongoing speech.
        """
        # Stop any current speech
        self.stop()

        def run_tts():
            self._stop_event.clear()
            for _gs, _ps, audio in self.pipeline(
                text,
                voice=self.voice,
                speed=self.speed,
                split_pattern=self.split_pattern
            ):
                if self._stop_event.is_set():
                    break
                sd.play(audio, samplerate=24000)
                sd.wait()

        self._thread = threading.Thread(target=run_tts, daemon=True)
        self._thread.start()

    def stop(self):
        """
        Stop any ongoing speech immediately.
        """
        self._stop_event.set()
        sd.stop()
        if self._thread and self._thread.is_alive():
            self._thread.join()

    def is_speaking(self) -> bool:
        """
        Return True if currently speaking.
        """
        return self._thread is not None and self._thread.is_alive() and not self._stop_event.is_set()
