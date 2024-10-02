import customtkinter
from tkinter import ttk
from mouth.kiss import kiss
from mouth.smile import smile
from mouth.mouth_closed_open import mouth_closed_open
from mouth.tongue.tongue import tongue
from display import app, pressed_button, font_details, camera_canvas, scrollable_frame
from speech.GUI import record, stop, play, check

def main(exception=None):
    global pressed_button
    pressed_button = exception

button_frame = customtkinter.CTkFrame(master=scrollable_frame)
button_frame.pack(pady=20, expand=True, fill="both")

mouth_closed_open_button = customtkinter.CTkButton(
    master=button_frame,
    text="Mouth open",
    command=lambda: [main(mouth_closed_open_button), mouth_closed_open()],
    font=font_details)
mouth_closed_open_button.pack(pady=10)

smile_button = customtkinter.CTkButton(
    master=button_frame,
    text="Smile",
    command=lambda: [main(smile_button), smile()],
    font=font_details)
smile_button.pack(pady=10)

kiss_button = customtkinter.CTkButton(
    master=button_frame,
    text="Kiss",
    command=lambda: [main(kiss_button), kiss()],
    font=font_details)
kiss_button.pack(pady=10)

tongue_button = customtkinter.CTkButton(
    master=button_frame,
    text="Tongue",
    command=lambda: [main(tongue_button), tongue()],
    font=font_details)
tongue_button.pack(pady=10)

def toggle_menu(button, sound_type):
    if not hasattr(button, 'frame') or not button.frame.winfo_ismapped():
        for btn in [lip_roll_button, munching_button, kneeling_button]:
            if hasattr(btn, 'frame') and btn.frame.winfo_ismapped():
                btn.frame.pack_forget()

        if not hasattr(button, 'frame'):
            button.frame = customtkinter.CTkFrame(master=button_frame)
            button.frame.pack(after=button, pady=10, fill="x")
            create_shared_buttons(button.frame, sound_type)
        else:
            button.frame.pack(after=button, pady=10, fill="x")
    else:
        button.frame.pack_forget()

def create_shared_buttons(frame, sound_type):
    progressbar = ttk.Progressbar(master=frame, mode="indeterminate", length=300)
    progressbar.pack(pady=10)

    record_button = customtkinter.CTkButton(
        master=frame,
        text="Record",
        command=lambda: record(record_button, stop_button, play_button, check_button, progressbar),
        font=font_details,
        width=100)
    record_button.pack(pady=5)

    stop_button = customtkinter.CTkButton(
        master=frame,
        text="Stop",
        command=stop,
        font=font_details,
        width=100)
    stop_button.pack(pady=5)

    play_button = customtkinter.CTkButton(
        master=frame,
        text="Play",
        command=lambda: play(play_button, stop_button, progressbar),
        font=font_details,
        width=100)
    play_button.pack(pady=5)

    check_button = customtkinter.CTkButton(
        master=frame,
        text="Check",
        command=lambda: check(progressbar, sound_type),
        font=font_details,
        width=100)
    check_button.pack(pady=5)

lip_roll_button = customtkinter.CTkButton(
    master=button_frame,
    text="Lip roll",
    command=lambda: toggle_menu(lip_roll_button, "Lip roll"),
    font=font_details)
lip_roll_button.pack(pady=10)

munching_button = customtkinter.CTkButton(
    master=button_frame,
    text="Munching",
    command=lambda: toggle_menu(munching_button, "Munching"),
    font=font_details)
munching_button.pack(pady=10)

kneeling_button = customtkinter.CTkButton(
    master=button_frame,
    text="Kneeling",
    command=lambda: toggle_menu(kneeling_button, "Kneeling"),
    font=font_details)
kneeling_button.pack(pady=10)

app.mainloop()
