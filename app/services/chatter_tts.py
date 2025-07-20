import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
from translate import TranslationResult

model = ChatterboxTTS.from_pretrained(device="cuda")

text = TranslationResult()
wav = model.generate(text)
ta.save("reference_audio-[AudioTrimmer.com].wav", wav, model.sr)

# If you want to synthesize with a different voice, specify the audio prompt
AUDIO_PROMPT_PATH = "reference_audio.wav"
wav = model.generate(text, audio_prompt_path=AUDIO_PROMPT_PATH)
ta.save("cloned_audio.wav", wav, model.sr)