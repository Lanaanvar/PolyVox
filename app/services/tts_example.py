import torch
import torchaudio as ta
from TTS.api import TTS

# Initialize TTS model (using Coqui TTS instead of chatterbox)
device = "cuda" if torch.cuda.is_available() else "cpu"
model = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True).to(device)

text = "Ezreal and Jinx teamed up with Ahri, Yasuo, and Teemo to take down the enemy's Nexus in an epic late-game pentakill."

# Generate speech without reference audio (regular TTS)
wav = model.tts(text=text)
ta.save("test-1.wav", torch.tensor(wav).unsqueeze(0), 22050)

# If you want to synthesize with a different voice, specify the audio prompt
AUDIO_PROMPT_PATH = "reference_audio.wav"
if torch.cuda.is_available():
    wav = model.tts(text=text, speaker_wav=AUDIO_PROMPT_PATH, language="en")
else:
    # Fallback for CPU
    wav = model.tts(text=text, speaker_wav=AUDIO_PROMPT_PATH, language="en")
    
ta.save("test-2.wav", torch.tensor(wav).unsqueeze(0), 22050)