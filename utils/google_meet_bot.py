import time
import speech_recognition as sr
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import threading
from config import Config

class GoogleMeetBot:
    def __init__(self):
        self.config = Config()
        self.driver = None
        self.transcript_text = ""
        self.recording = False
    
    def join_and_record(self, meet_url: str) -> str:
        """Join Google Meet and capture transcript"""
        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--use-fake-ui-for-media-stream")
            chrome_options.add_argument("--use-fake-device-for-media-stream")
            chrome_options.add_argument("--start-maximized")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Login to Google (simplified - in production use OAuth)
            self.driver.get("https://accounts.google.com")
            time.sleep(3)
            
            # For demo purposes, we'll skip actual login
            # In production, implement proper OAuth2 flow
            
            # Join the meeting
            self.driver.get(meet_url)
            time.sleep(5)
            
            # Try to join meeting
            try:
                # Turn off camera and mic
                camera_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Turn off camera']"))
                )
                camera_btn.click()
                
                mic_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Turn off microphone']"))
                )
                mic_btn.click()
                
                # Ask to join
                join_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ask to join') or contains(text(), 'Join now')]"))
                )
                join_btn.click()
                
            except:
                pass
            
            # Wait and capture closed captions
            transcript = self._captive_captions(30)  # Record for 30 seconds
            
            return transcript
            
        except Exception as e:
            print(f"Google Meet error: {e}")
            return f"Error joining meeting: {str(e)}"
        finally:
            if self.driver:
                self.driver.quit()
    
    def _captive_captions(self, duration: int) -> str:
        """Capture closed captions from Google Meet"""
        transcript = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                # Try to find caption elements
                captions = self.driver.find_elements(By.CSS_SELECTOR, "div[jsname='TbnRzc']")
                for caption in captions:
                    text = caption.text.strip()
                    if text and text not in transcript:
                        transcript.append(text)
                
                time.sleep(2)
                
            except Exception as e:
                print(f"Caption error: {e}")
                time.sleep(1)
        
        return " ".join(transcript)
    
    def _record_audio(self, duration: int):
        """Record audio from meeting (alternative method)"""
        recognizer = sr.Recognizer()
        
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            
            print("Recording started...")
            audio_data = recognizer.record(source, duration=duration)
            
            try:
                text = recognizer.recognize_google(audio_data)
                self.transcript_text += " " + text
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print(f"Recognition error: {e}")