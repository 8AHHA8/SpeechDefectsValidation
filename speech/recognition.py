import tkinter as tk
import sounddevice as sd
import soundfile as sf
import threading
from tkinter import messagebox
import argparse
from speech.predict import make_prediction_sample

def record(record_button, stop_button, play_button, check_button, progressbar):
    record_button.configure(state=tk.DISABLED)
    stop_button.configure(state=tk.NORMAL)
    play_button.configure(state=tk.DISABLED)
    check_button.configure(state=tk.DISABLED)

    progressbar.start()

    recording_thread = threading.Thread(target=record_audio, args=(record_button, stop_button, play_button, check_button, progressbar))
    recording_thread.start()

def record_audio(record_button, stop_button, play_button, check_button, progressbar):
    duration = 10
    fs = 44100
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()

    filename = "speech/audios/sample.wav"
    sf.write(filename, recording, fs)

    progressbar.stop()
    record_button.configure(state=tk.NORMAL)
    stop_button.configure(state=tk.DISABLED)
    play_button.configure(state=tk.NORMAL)
    check_button.configure(state=tk.NORMAL)

def stop():
    sd.stop()

def play(play_button, stop_button, progressbar):
    play_button.configure(state=tk.DISABLED)
    stop_button.configure(state=tk.NORMAL)
    progressbar.start()

    play_thread = threading.Thread(target=play_audio_thread, args=(play_button, stop_button, progressbar))
    play_thread.start()

def play_audio_thread(play_button, stop_button, progressbar):
    filename = "speech/audios/sample.wav"
    try:
        data, fs = sf.read(filename, dtype='int16')
        sd.play(data, fs)
        sd.wait()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while playing audio: {str(e)}")
    finally:
        progressbar.stop()
        stop_button.configure(state=tk.DISABLED)
        play_button.configure(state=tk.NORMAL)

def check(progressbar, sound_type):
    try:
        progressbar.start()

        args = argparse.Namespace(
            model_fn='speech/models/lstm.h5',
            pred_fn='y_pred',
            src_dir='speech/wavfiles',
            dt=1.0,
            sr=16000,
            threshold=20
        )

        results = make_prediction_sample(args)

        if not results:
            messagebox.showinfo("Sound Validation", f"No sound detected for {sound_type}.")
        else:
            detected_sound = results[0][1]

            if detected_sound.lower() == sound_type.lower():
                messagebox.showinfo("Sound Validation", f"{sound_type} sound is correct! Detected: {detected_sound}")
            else:
                messagebox.showwarning("Sound Validation", f"Expected: {sound_type}, but detected: {detected_sound}. This is incorrect.")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

    finally:
        progressbar.stop()
