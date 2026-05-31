import sys
import os
import requests

# Set URL of the running FastAPI server
BASE_URL = "http://localhost:8000"

def check_server_running():
    try:
        response = requests.get(f"{BASE_URL}/")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def run_audio_test():
    print("--- Voice Recruitment Agent: Audio Integration Test ---")
    
    # 1. Check if the server is running
    if not check_server_running():
        print(f"Error: FastAPI server is not running on {BASE_URL}.")
        print("Please start the server first using: python -m uvicorn backend.app.main:app --reload")
        sys.exit(1)
    print("[✔] FastAPI Server is active.")

    # 2. Check if OpenAI API key is configured
    from backend.app.core.config import settings
    api_key = settings.openai_api_key
    if not api_key or api_key == "test":
        print("\n[!] WARNING: OpenAI API Key is not set in backend/.env or .env file.")
        print("Please add your key: OPENAI_API_KEY=your_real_key_here")
        print("Without a real key, OpenAI API requests will fail.\n")
        # Proceed anyway to let them see the error from the backend
    else:
        print("[✔] OpenAI API Key is configured.")

    # 3. Test Text-to-Speech (TTS)
    test_text = "Hello Candidate. Welcome to our automated screening call."
    print(f"\n1. Requesting TTS generation for: \"{test_text}\"")
    
    tts_url = f"{BASE_URL}/api/calls/1/tts"
    try:
        response = requests.get(tts_url, params={"text": test_text})
        if response.status_code != 200:
            print(f"[-] TTS Request failed (HTTP {response.status_code}): {response.text}")
            sys.exit(1)
        
        audio_filename = "test_tts.mp3"
        with open(audio_filename, "wb") as f:
            f.write(response.content)
        print(f"[✔] TTS file generated successfully and saved as: '{audio_filename}'")
        
    except Exception as e:
        print(f"[-] TTS Request encountered an error: {e}")
        sys.exit(1)

    # 4. Test Speech-to-Text (STT Transcription)
    print(f"\n2. Uploading '{audio_filename}' to transcription endpoint...")
    transcribe_url = f"{BASE_URL}/api/calls/1/transcribe"
    
    try:
        with open(audio_filename, "rb") as audio_file:
            files = {"upload_file": (audio_filename, audio_file, "audio/mpeg")}
            response = requests.post(transcribe_url, files=files)
            
        if response.status_code != 200:
            print(f"[-] Transcription failed (HTTP {response.status_code}): {response.text}")
            sys.exit(1)
            
        result = response.json()
        transcription = result.get("transcript", "")
        print(f"[✔] Transcription successful!")
        print(f"    Transcribed Text: \"{transcription}\"")
        
    except Exception as e:
        print(f"[-] Transcription Request encountered an error: {e}")
        sys.exit(1)

    # 5. Clean up
    if os.path.exists(audio_filename):
        os.remove(audio_filename)
        print("\n[✔] Cleaned up temporary test audio file.")

    print("\n--- Audio Integration Test Complete! ---")

if __name__ == "__main__":
    run_audio_test()
