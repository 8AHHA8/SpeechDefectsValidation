import customtkinter
from tkinter import ttk
from mouth.kiss import kiss
from mouth.smile import smile
from mouth.closed_open import closed_open
from mouth.tongue.tongue_horizontal import tongue_horizontal
from mouth.tongue.tongue_vertical import tongue_vertical
from mouth.cheeks.cheeks import cheeks
from mouth.right_cheek.right_cheek import right_cheek
from mouth.left_cheek.left_cheek import left_cheek
from display import app, pressed_button, font_details, scrollable_frame
from sounds.recognition import record, stop, play, check
from words.words import record_word, check_word, play_word
from words.dropdown import styled_dropdown

def disable_buttons(except_button=None):
    for button in button_frame.winfo_children():
        if button != except_button:
            button.configure(state="disabled", fg_color="gray")

def reset_buttons():
    for button in button_frame.winfo_children():
        button.configure(state="normal", fg_color="#2fa572")

def main(exception=None):
    global pressed_button
    
    if exception == pressed_button:
        reset_buttons()
        pressed_button = None
    else:
        if pressed_button:
            pressed_button.configure(fg_color="darkgreen")
            
        pressed_button = exception
        pressed_button.configure(fg_color="lightgreen")
        disable_buttons(pressed_button)

button_frame = customtkinter.CTkFrame(master=scrollable_frame)
button_frame.pack(pady=20, expand=True, fill="both")

closed_open_button = customtkinter.CTkButton(
    master=button_frame,
    text="Mouth open",
    command=lambda: [main(closed_open_button), closed_open()],
    font=font_details,
    width=200)
closed_open_button.pack(pady=10)

smile_button = customtkinter.CTkButton(
    master=button_frame,
    text="Smile",
    command=lambda: [main(smile_button), smile()],
    font=font_details,
    width=200)
smile_button.pack(pady=10)

kiss_button = customtkinter.CTkButton(
    master=button_frame,
    text="Kiss",
    command=lambda: [main(kiss_button), kiss()],
    font=font_details,
    width=200)
kiss_button.pack(pady=10)

tongue_horizontal_button = customtkinter.CTkButton(
    master=button_frame,
    text="Tongue Horizontal",
    command=lambda: [main(tongue_horizontal_button), tongue_horizontal()],
    font=font_details,
    width=200)
tongue_horizontal_button.pack(pady=10)

tongue_vertical_button = customtkinter.CTkButton(
    master=button_frame,
    text="Tongue Vertical",
    command=lambda: [main(tongue_vertical_button), tongue_vertical()],
    font=font_details,
    width=200)
tongue_vertical_button.pack(pady=10)

cheeks_button = customtkinter.CTkButton(
    master=button_frame,
    text="Cheeks",
    command=lambda: [main(cheeks_button), cheeks()],
    font=font_details,
    width=200)
cheeks_button.pack(pady=10)

right_cheek_button = customtkinter.CTkButton(
    master=button_frame,
    text="Right Cheek",
    command=lambda: [main(right_cheek_button), right_cheek()],
    font=font_details,
    width=200)
right_cheek_button.pack(pady=10)

left_cheek_button = customtkinter.CTkButton(
    master=button_frame,
    text="Left Cheek",
    command=lambda: [main(left_cheek_button), left_cheek()],
    font=font_details,
    width=200)
left_cheek_button.pack(pady=10)

def toggle_menu(button, sound_type, action_type):
    print(f"Toggling menu for action type: {action_type}")
    if not hasattr(button, 'frame') or not button.frame.winfo_ismapped():
        if action_type == "lip_munch_kneel":
            for btn in [words_button]:
                if hasattr(btn, 'frame') and btn.frame.winfo_ismapped():
                    print("Hiding words buttons")
                    btn.frame.pack_forget()

        elif action_type == "words":
            for btn in [lip_roll_button, munching_button, kneeling_button]:
                if hasattr(btn, 'frame') and btn.frame.winfo_ismapped():
                    print("Hiding lip munch kneel buttons")
                    btn.frame.pack_forget()

        if not hasattr(button, 'frame'):
            button.frame = customtkinter.CTkFrame(master=button_frame)
            button.frame.pack(after=button, pady=10, fill="x")
            create_shared_buttons(button.frame, sound_type, action_type)
            print("Created buttons for action type:", action_type)
        else:
            button.frame.pack(after=button, pady=10, fill="x")
    else:
        print("Hiding buttons for action type:", action_type)
        button.frame.pack_forget()

def create_shared_buttons(frame, sound_type, action_type):
    print(f"Creating shared buttons for action type: {action_type}")
    progressbar = ttk.Progressbar(master=frame, mode="indeterminate", length=300)
    progressbar.pack(pady=10)

    if action_type == "lip_munch_kneel":
        record_sound_button = customtkinter.CTkButton(
            master=frame,
            text="Record",
            command=lambda: record(record_sound_button, stop_sound_button, play_sound_button, check_sound_button, progressbar),
            font=font_details,
            width=100)
        record_sound_button.pack(pady=5)

        stop_sound_button = customtkinter.CTkButton(
            master=frame,
            text="Stop",
            command=stop,
            font=font_details,
            width=100)
        stop_sound_button.pack(pady=5)

        play_sound_button = customtkinter.CTkButton(
            master=frame,
            text="Play",
            command=lambda: play(play_sound_button, stop_sound_button, check_sound_button, record_sound_button, progressbar),
            font=font_details,
            width=100)
        play_sound_button.pack(pady=5)

        check_sound_button = customtkinter.CTkButton(
            master=frame,
            text="Check",
            command=lambda: check(progressbar, sound_type),
            font=font_details,
            width=100)
        check_sound_button.pack(pady=5)

    elif action_type == "words":
        word_options = ["słowo", "szczebrzeszyn", "dżem", "rabarbar", "październik"]
        selected_word = styled_dropdown(frame, word_options)

        record_word_button = customtkinter.CTkButton(
            master=frame,
            text="Record",
            command=lambda: record_word(progressbar),
            font=font_details,
            width=100)
        record_word_button.pack(pady=5)
        
        play_word_button = customtkinter.CTkButton(
            master=frame,
            text="Play",
            command=lambda: play_word(progressbar),
            font=font_details,
            width=100)
        play_word_button.pack(pady=5)
        
        check_word_button = customtkinter.CTkButton(
            master=frame,
            text="Check",
            command=lambda: check_word(progressbar, selected_word.get()),
            font=font_details,
            width=100)
        check_word_button.pack(pady=5)

lip_roll_button = customtkinter.CTkButton(
    master=button_frame,
    text="Lip roll",
    command=lambda: toggle_menu(lip_roll_button, "Lip roll", "lip_munch_kneel"),
    font=font_details,
    width=200)
lip_roll_button.pack(pady=10)

munching_button = customtkinter.CTkButton(
    master=button_frame,
    text="Munching",
    command=lambda: toggle_menu(munching_button, "Munching", "lip_munch_kneel"),
    font=font_details,
    width=200)
munching_button.pack(pady=10)

kneeling_button = customtkinter.CTkButton(
    master=button_frame,
    text="Kneeling",
    command=lambda: toggle_menu(kneeling_button, "Kneeling", "lip_munch_kneel"),
    font=font_details,
    width=200)
kneeling_button.pack(pady=10)

words_button = customtkinter.CTkButton(
    master=button_frame,
    text="Words",
    command=lambda: toggle_menu(words_button, "Words", "words"),
    font=font_details,
    width=200)
words_button.pack(pady=10)

app.mainloop()