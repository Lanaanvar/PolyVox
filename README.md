# PolyVox - Redefining Voice in Media

PolyVox is an innovative voice cloning and multilingual speech synthesis system developed by Code Red. It aims to revolutionize how dubbing is done by preserving the original actor’s voice and emotional delivery, even when translated into different languages.

**Track** - Entertainment


## 📌 Problem Statement
In traditional dubbing, actors' voices are replaced by different voice artists for each language. This leads to a loss of vocal identity, emotional disconnect, and a reduction in viewer immersion. As content becomes more global, these limitations hinder the reach and impact of films, shows, and digital media.

## Solution
PolyVox solves this by using AI-powered voice cloning and cross-lingual TTS, allowing actors to speak naturally in multiple languages while preserving their unique vocal characteristics and performance nuances.

It produces emotionally aligned, natural-sounding speech in a translated language using only a short sample of the actor’s original voice.


## 🔄 Workflow
🎧 Audio Extraction
Extract clean speech audio from source video using FFmpeg.

🧠 Speech-to-Text (STT)
Transcribe the original dialogue using OpenAI's Whisper.

🌍 Translation
Translate the transcribed text to the target language using Google Translate.

🗣️ Voice Cloning & TTS
Use models like Xtts-v2, Tortoise-v2, or ChatterBox to synthesize the translated speech in the actor’s original voice.

## Tech Stack
| Component           | Technology Used                  |
| ------------------- | -------------------------------- |
| Audio Processing    | FFmpeg                           |
| Speech-to-Text      | OpenAI Whisper                   |
| Translation         | Google Translate API             |
| Voice Cloning & TTS | Xtts-v2, Tortoise-v2, ChatterBox |
| Backend API         | Python, FastAPI                  |
| Frontend            | React.js                         |


##  Implementation

1. **Translation**: Translates your text to any target language
2. **Voice Cloning**: Clones the voice from your reference audio
3. **Speech Generation**: Creates speech in the cloned voice with translated text

[Check out PolyVox here!](https://drive.google.com/file/d/1AbF7BfDKr3_6RkX81cPw-SIGOCNgA1tD/view?usp=drive_link)

## Installation
Step 1: Clone the Repository

```
git clone https://github.com/yourusername/voice-cloning.git
cd voice-cloning
```

Step 2: Install FFmpeg
  1. Download FFmpeg 
  2. Extract and add to system PATH

Step 3: Create Virtual Environment
```
python -m venv .venv
.venv\Scripts\activate
```
Step 4: Install Dependencies
```
pip install -r requirements.txt
```

Strp 5: Run
```
run_fastapi.bat
```

## 🔭 Future Scope
PolyVox can evolve into a fully automated multilingual dubbing solution by integrating advanced lip-syncing technologies, enabling synchronized visuals alongside voice cloning. Future improvements may include emotional tone and prosody control for more expressive and natural-sounding speech, support for low-resource languages to increase inclusivity, and real-time or on-device deployment for interactive applications like gaming and AR/VR. Additionally, offering PolyVox as a cloud-based API or SaaS platform can streamline adoption across film, OTT, and media production pipelines.

## Code Red
[Lana Anvar](https://github.com/Lanaanvar)
<br>
[Sutharya](https://github.com/ssutharya)
<br>
[Ganga](https://github.com/gangakailas)
<br>
[Lakshmikha Rejith](https://github.com/Lakshmikha)



