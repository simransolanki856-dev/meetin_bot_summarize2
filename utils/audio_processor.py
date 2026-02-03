import speech_recognition as sr
from pydub import AudioSegment
import moviepy.editor as mp
import os
import whisper
from typing import Optional

class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.whisper_model = whisper.load_model("base")
    
    def extract_transcript(self, file_path: str) -> str:
        """Extract transcript from audio/video file"""
        # Convert to wav if needed
        if file_path.endswith('.mp4'):
            audio_path = self._convert_video_to_audio(file_path)
        elif file_path.endswith('.mp3'):
            audio_path = self._convert_mp3_to_wav(file_path)
        else:
            audio_path = file_path
        
        # Use Whisper for transcription
        try:
            result = self.whisper_model.transcribe(audio_path)
            return result["text"]
        except Exception as e:
            print(f"Whisper failed: {e}")
            return self._fallback_transcription(audio_path)
    
    def _convert_video_to_audio(self, video_path: str) -> str:
        """Convert video file to audio"""
        audio_path = video_path.replace('.mp4', '.wav')
        video = mp.VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)
        return audio_path
    
    def _convert_mp3_to_wav(self, mp3_path: str) -> str:
        """Convert MP3 to WAV format"""
        wav_path = mp3_path.replace('.mp3', '.wav')
        audio = AudioSegment.from_mp3(mp3_path)
        audio.export(wav_path, format="wav")
        return wav_path
    
    def _fallback_transcription(self, audio_path: str) -> str:
        """Fallback using SpeechRecognition"""
        with sr.AudioFile(audio_path) as source:
            audio_data = self.recognizer.record(source)
            try:
                text = self.recognizer.recognize_google(audio_data)
                return text
            except sr.UnknownValueError:
                return "Could not understand audio"
            except sr.RequestError as e:
                return f"Recognition error: {e}"