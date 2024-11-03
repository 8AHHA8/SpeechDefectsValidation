import os
import wave
import json
import sounddevice as sd
import soundfile as sf
import threading
from tkinter import messagebox, StringVar
from tkinter import ttk
from vosk import Model, KaldiRecognizer

model_path = "vosk-model-small-pl-0.22"
model = Model(model_path)

if not os.path.exists('words/word'):
    os.makedirs('words/word')

def record_word(progressbar):
    duration = 3
    fs = 44100
    thread = threading.Thread(target=record_audio, args=(duration, fs, progressbar))
    thread.start()

def record_audio(duration, fs, progressbar):
    progressbar.start()
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    progressbar.stop()

    filename = "words/word/word.wav"
    sf.write(filename, recording, fs)
    return filename

def play_word(progressbar):
    try:
        audio_file = "words/word/word.wav"
        if not os.path.exists(audio_file):
            messagebox.showerror("Error", "No recorded audio to play.")
            return

        thread = threading.Thread(target=play_audio, args=(audio_file, progressbar))
        thread.start()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def play_audio(filename, progressbar):
    try:
        progressbar.start()
        data, fs = sf.read(filename)
        sd.play(data, samplerate=fs)
        sd.wait()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while playing the audio: {str(e)}")
    finally:
        progressbar.stop()

def check_word(progressbar, expected_word):
    try:
        progressbar.start()

        audio_file = "words/word.wav"
        wf_test = wave.open(audio_file, "rb")
        
        rec = KaldiRecognizer(model, wf_test.getframerate())
        recognized_text = ""

        while True:
            data = wf_test.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = rec.Result()
                recognized_text = json.loads(result)["text"]

        final_result = rec.FinalResult()
        recognized_text += json.loads(final_result)["text"]

        print(f"Recognized Text: {recognized_text}")
        
        if recognized_text.lower() == expected_word.lower():
            messagebox.showinfo("Sound Validation", f"Word pronounced correctly: {recognized_text}")
        else:
            messagebox.showwarning("Sound Validation", f"Expected: {expected_word}, but recognized: {recognized_text}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

    finally:
        progressbar.stop()


