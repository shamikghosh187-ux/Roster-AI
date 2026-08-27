import os
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import base64
from groq import Groq
import pyttsx3
import pyautogui
import pywhatkit
import webbrowser

engine = pyttsx3.init()

def speak(text):
    print(f"Roster: {text}")
    engine.say(text)
    engine.runAndWait()

# Initialize Groq client
client = Groq(api_key=os.environ["GROQ_API_KEY"])

def record_and_talk():
    duration = 5
    samplerate = 16000
    filename = "user_input.wav"
    
    print("\n🎤 Listening... Speak your command (or say 'exit' to quit)!")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
    sd.wait()
    
    # --- NOISE GATE (Filters out background silence/noise) ---
    audio_float = audio_data.astype(np.float32)
    volume_level = np.sqrt(np.mean(audio_float**2))
    
    if volume_level < 400: 
        print("🤫 Ignored background noise.")
        return True
    # --------------------------------------------------------
    
    wav.write(filename, samplerate, audio_data)
    print("✅ Transcribing and analyzing command...")
    
    try:
        # Transcribe audio using Groq's Whisper model
        with open(filename, "rb") as file:
            transcript = client.audio.transcriptions.create(
                file=(filename, file.read()),
                model="whisper-large-v3-turbo",
                response_format="text"
            )
        
        user_text = transcript.strip()
        print(f"🗣️ You said: '{user_text}'")
        
        if not user_text:
            return True

        # Send transcription to Groq model for dynamic intent parsing
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Roster, a powerful desktop AI assistant with screen vision. Analyze the user request and decide the action. "
                        "Reply using ONE of these exact formats based on what the user wants:\n"
                        "1. If they want to exit, stop, or goodbye: EXIT\n"
                        "2. If they want you to look at their screen, check their monitor, read an error, or troubleshoot what's on display: SCREEN_VISION\n"
                        "3. If they want to open *any* app or software (like chrome, spotify, calculator, word, notepad, etc.): OPEN_APP: [app name]\n"
                        "4. If they want to search something on Google or ask a web question: SEARCH: [search query]\n"
                        "5. If they want to play a video or song on YouTube: YOUTUBE: [song or video name]\n"
                        "6. If they want to send an instant WhatsApp message: WHATSAPP: [phone number with country code], [message]\n"
                        "7. For anything else (conversational answers, general questions): CHAT: [your short spoken response]"
                    )
                },
                {"role": "user", "content": user_text}
            ]
        )
        
        answer = response.choices[0].message.content.strip()
        print(f"🤖 Result: {answer}")
        
        if "EXIT" in answer or answer.startswith("EXIT"):
            speak("Goodbye!")
            return False
            
        elif answer.startswith("SCREEN_VISION"):
            speak("Taking a screenshot and analyzing your screen.")
            screenshot_path = "screenshot.png"
            pyautogui.screenshot(screenshot_path)
            
            with open(screenshot_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                
            vision_response = client.chat.completions.create(
                model="qwen/qwen3.6-27b",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"The user asked: '{user_text}'. Analyze this desktop screenshot and give a helpful answer or troubleshooting advice."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                        ]
                    }
                ]
            )
            vision_answer = vision_response.choices[0].message.content.strip()
            print(f"👁️ Vision Analysis: {vision_answer}")
            speak(vision_answer)
            
        elif answer.startswith("OPEN_APP:"):
            app_name = answer.replace("OPEN_APP:", "").strip()
            speak(f"Opening {app_name}.")
            pyautogui.press('win')
            pyautogui.write(app_name)
            pyautogui.press('enter')
            
        elif answer.startswith("SEARCH:"):
            query = answer.replace("SEARCH:", "").strip()
            speak(f"Searching for {query}.")
            webbrowser.open(f"https://www.google.com/search?q={query}")
            
        elif answer.startswith("YOUTUBE:"):
            query = answer.replace("YOUTUBE:", "").strip()
            speak(f"Playing {query} on YouTube.")
            pywhatkit.playonyt(query)
            
        elif answer.startswith("WHATSAPP:"):
            details = answer.replace("WHATSAPP:", "").strip()
            if "," in details:
                phone, msg = details.split(",", 1)
                speak("Sending WhatsApp message.")
                pywhatkit.sendwhatmsg_instantly(phone.strip(), msg.strip(), wait_time=10, tab_close=True, close_time=3)
            else:
                speak("Please specify both the phone number and message.")
                
        elif answer.startswith("CHAT:"):
            speak(answer.replace("CHAT:", "").strip())
        else:
            speak(answer)
            
    except Exception as e:
        print(f"Error: {e}")
        
    return True

if __name__ == "__main__":
    speak("Hello, I am Roster. Your assistant is ready.")
    running = True
    while running:
        running = record_and_talk()
