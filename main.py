import time
import base64
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os
from mimetypes import guess_type
import hashlib
import asyncio
import aiohttp
import aiofiles
from itertools import count
import queue
import signal
import simpleaudio as sa
import azure.cognitiveservices.speech as speechsdk

from prompts import COMMENTATOR_SYSTEM_PROMPT, COMMENTATOR_USER_PROMPT

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(override=True)

# Azure OpenAI Configuration
OPENAI_API_BASE_URL = os.getenv('OPENAI_API_BASE_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Deployment name for Vision model
VISION_MODEL_DEPLOYMENT_NAME = os.getenv('VISION_MODEL_DEPLOYMENT_NAME')

CHESS_URL = os.getenv('CHESS_STREAM_URL')
CHESS_USERNAME = os.getenv('CHESS_USERNAME')
CHESS_PASSWORD = os.getenv('CHESS_PASSWORD')

AZURE_SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')
AZURE_SPEECH_REGION = os.getenv('AZURE_SPEECH_REGION')

# Thread-safe counter for sequential naming
counter = count()

# Queue to store audio paths
audio_queue = queue.Queue()

# Signal handler to manage Ctrl+C interruptions
stop_event = asyncio.Event()

def signal_handler(sig, frame):
    print("Signal received. Stopping the process after the current task...")
    stop_event.set()

signal.signal(signal.SIGINT, signal_handler)

async def get_page_hash(driver):
    page_source = driver.page_source
    return hashlib.sha256(page_source.encode()).hexdigest()

async def take_screenshot(driver, ctr):
    screenshot = driver.get_screenshot_as_png()
    image = Image.open(BytesIO(screenshot))
    current_dir = os.path.dirname(os.path.abspath(__file__))
    screenshots_dir = os.path.join(current_dir, 'screenshots')
    os.makedirs(screenshots_dir, exist_ok=True)
    
    image_path = os.path.join(screenshots_dir, f'screenshot_{ctr}.png')
    image.save(image_path, format="PNG")
    
    return image_path

async def local_image_to_data_url(image_path):
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'

    async with aiofiles.open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(await image_file.read()).decode('utf-8')

    return f"data:{mime_type};base64,{base64_encoded_data}"

async def send_to_vision_api(image_data_url, previous_commentary=""):
    url = f"{OPENAI_API_BASE_URL}/openai/deployments/{VISION_MODEL_DEPLOYMENT_NAME}/chat/completions?api-version=2024-02-15-preview"
    headers = {
        'api-key': OPENAI_API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        "messages": [
            {
                "role": "system",
                "content": COMMENTATOR_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": COMMENTATOR_USER_PROMPT.format(previous_commentary=previous_commentary)
            },
            {
                "role": "user",
                "content": {
                    "type": "image_url",
                    "image_url": {
                        "url": image_data_url
                    }
                }
            }
        ],
        "temperature": 0.7,
        "max_tokens": 4096
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            response.raise_for_status()
            result = await response.json()
            return result["choices"][0]["message"]["content"].strip()

def generate_tts(text, ctr):
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
    speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

    current_dir = os.path.dirname(os.path.abspath(__file__))
    audio_dir = os.path.join(current_dir, 'audio')
    os.makedirs(audio_dir, exist_ok=True)
    audio_path = os.path.join(audio_dir, f'output_{ctr}.wav')
    audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_path)

    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Speech synthesized to {audio_path}")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")

    return audio_path

async def process_screenshot(driver, ctr, previous_commentary):
    image_path = await take_screenshot(driver, ctr)
    image_data_url = await local_image_to_data_url(image_path)
    commentary = await send_to_vision_api(image_data_url, previous_commentary)
    print(f"Generated Commentary: {commentary}")

    # Queue the TTS processing
    await asyncio.create_task(process_tts(commentary, ctr))
    return commentary

async def process_tts(commentary, ctr):
    audio_path = generate_tts(commentary, ctr)
    audio_queue.put(audio_path)

async def monitor_chess_game(driver):
    prev_hash = await get_page_hash(driver)
    previous_commentary = ""
    while not stop_event.is_set():
        await asyncio.sleep(1)  # Adjust polling frequency for faster response
        curr_hash = await get_page_hash(driver)
        if curr_hash != prev_hash:
            ctr = next(counter)
            previous_commentary = await process_screenshot(driver, ctr, previous_commentary)
            prev_hash = curr_hash
        else:
            # No change in the image, create a conversational piece
            previous_commentary = await process_screenshot(driver, ctr, previous_commentary)

async def play_audio_queue():
    while True:
        audio_path = await asyncio.to_thread(audio_queue.get)
        if audio_path is None:
            break
        try:
            wave_obj = sa.WaveObject.from_wave_file(audio_path)
            play_obj = wave_obj.play()
            play_obj.wait_done()  # Wait until playback is finished
        except Exception as e:
            print(f"Error playing audio: {e}")

async def main():
    # Set up WebDriver
    chrome_driver_path = os.getenv('CHROME_DRIVER_PATH')
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service)

    driver.get(CHESS_URL)

    time.sleep(1)

    # Log in to the Chess URL if required
    if CHESS_USERNAME and CHESS_PASSWORD:
        username_field = driver.find_element(By.CSS_SELECTOR, "input.cc-input-component[aria-label='Username or Email']")
        username_field.send_keys(CHESS_USERNAME)
        password_field = driver.find_element(By.CSS_SELECTOR, "input.cc-input-component[aria-label='Password']")
        password_field.send_keys(CHESS_PASSWORD)
        login_button = driver.find_element(By.ID, 'login')
        login_button.click()
        
        # Wait for login to complete
        await asyncio.sleep(5)

    # Wait for user input to start taking screenshots
    input("Press Enter to start taking screenshots...")

    # Start monitoring chess game in the background
    monitor_task = asyncio.create_task(monitor_chess_game(driver))

    # Start audio playback in a separate async task
    audio_task = asyncio.create_task(play_audio_queue())

    # Wait for the monitor task to finish
    await monitor_task

    # Clean up
    audio_queue.put(None)
    await audio_task

if __name__ == "__main__":
    asyncio.run(main())
