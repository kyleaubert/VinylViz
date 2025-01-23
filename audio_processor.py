import sounddevice as sd
from scipy.io.wavfile import write
from pydub import AudioSegment
from PIL import Image
import asyncio
import requests
import os
import subprocess
import time
from shazamio import Shazam

# Configuration
SAMPLE_RATE = 48000.0
DURATION = 10
OUTPUT_FOLDER = "/home/kyle/VinylViz/shazam_output"
OUTPUT_WAV = os.path.join(OUTPUT_FOLDER, "recording.wav")
OUTPUT_OGG = os.path.join(OUTPUT_FOLDER, "recording.ogg")
RESULT_FILE = os.path.join(OUTPUT_FOLDER, "result.txt")
ALBUM_ART_FILE = os.path.join(OUTPUT_FOLDER, "album_art_32x32.png")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def record_audio(duration, sample_rate, output_wav):
    print("Recording audio...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()
    print("Recording finished.")
    write(output_wav, int(sample_rate), audio)
    print(f"Audio saved to {output_wav}")

def convert_to_ogg(input_wav, output_ogg):
    audio = AudioSegment.from_wav(input_wav)
    audio.export(output_ogg, format="ogg")
    print(f"Audio converted to {output_ogg}")

def download_and_resize_image(url, output_file, size=(32, 32)):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        image = Image.open(response.raw)
        image = image.resize(size, Image.Resampling.LANCZOS)
        image.save(output_file)
        print(f"Album art saved and resized to {output_file}")
    else:
        print(f"Failed to download album art from {url}")

async def recognize_and_save(file_path, result_file):
    print(f"Recognizing song in {file_path}...")
    shazam = Shazam()
    result = await shazam.recognize(file_path)
    if "track" in result:
        song = result["track"]["title"]
        album = result["track"]["sections"][0].get("metadata", [{}])[0].get("text", "Unknown")
        artist = result["track"]["subtitle"]
        album_art_url = result["track"]["images"]["coverart"]

        with open(result_file, "w") as f:
            f.write(f"{song}\n{album}\n{artist}")
        print(f"Results saved: {song}, {album}, {artist}")

        # Download and resize album art
        download_and_resize_image(album_art_url, ALBUM_ART_FILE)
        return song, album, artist
    else:
        print("Could not recognize the song.")
        return None, None, None

def main():
    display_process = None
    last_song = None

    # Initial audio processing
    record_audio(DURATION, SAMPLE_RATE, OUTPUT_WAV)
    convert_to_ogg(OUTPUT_WAV, OUTPUT_OGG)
    
    # Get initial song result
    song, album, artist = asyncio.run(recognize_and_save(OUTPUT_OGG, RESULT_FILE))

    if song:
        print(f"Initial song: {song}, {album}, {artist}")
        display_process = subprocess.Popen(["python3", "shazam_display.py"])

    last_song = song
    while True:
        time.sleep(10)  # Wait 10 seconds this could be changed
        print("Re-recording and recognizing new song...")
        record_audio(DURATION, SAMPLE_RATE, OUTPUT_WAV)
        convert_to_ogg(OUTPUT_WAV, OUTPUT_OGG)

        # Get new song result
        song, album, artist = asyncio.run(recognize_and_save(OUTPUT_OGG, RESULT_FILE))

        if song:
            print(f"Recognized new song: {song}")
        else:
            print("No song recognized. Skipping update.")
        
        # Check if the song has changed
        if song != last_song:
            print(f"New song detected: {song}. Restarting display.")
            last_song = song

            # Terminate the old display process if it exists
            if display_process and display_process.poll() is None:  # Check if the process is still running
                print("Terminating old display process...")
                display_process.terminate()
                display_process.wait()  
            
            # Start a new display process
            display_process = subprocess.Popen(["python3", "shazam_display.py"])

if __name__ == "__main__":
    main()

