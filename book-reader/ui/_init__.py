from pathlib import Path
self.tts = TTSPlayer(rate=180)      # adjust speaking rate if you like
self.is_playing = False

model = str(Path(__file__).parent.parent / "assets/voices/en_US-libritts-high.onnx")
self.tts = PiperPlayer(model)
self.is_playing = False
