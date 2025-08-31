# experiment.py
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import time
import os
from playsound import playsound
from PIL import Image, ImageTk
import config

class Experiment:
    def __init__(self, root):
        self.root = root
        self.root.title('LENA Mobile EEG - Developmental Neurolinguistic Lab')
        self.root.attributes('-fullscreen', True)
        self.participant_id = ""
        self.trial_count = -1
        self.step = 0
        self.response_data = []
        self.start_time = 0
        try:
            self.stimuli_info = pd.read_excel(config.STIMULI_INFO_FILE)
            self.number_of_stimuli = len(self.stimuli_info)
        except FileNotFoundError:
            messagebox.showerror("Error", f"Could not find stimuli info file:\n{config.STIMULI_INFO_FILE}")
            self.root.destroy()
            return
        self.canvas = tk.Canvas(self.root, bg='white', highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.correct_img_path = os.path.join(config.STIMULI_FOLDER, self.stimuli_info.iloc[0]['CorrectImage'])
        self.wrong_img_path = os.path.join(config.STIMULI_FOLDER, self.stimuli_info.iloc[0]['Wrongimage'])
        self.correct_photo = ImageTk.PhotoImage(Image.open(self.correct_img_path))
        self.wrong_photo = ImageTk.PhotoImage(Image.open(self.wrong_img_path))
        self.root.after(100, self._next_step)

    def _display_welcome_screen(self):
        self.canvas.create_text(750, 200, text="Welcome to the Experiment", font=('Helvetica', 40, 'bold'), fill="dark green")
        self.id_label = tk.Label(self.root, text="Enter Participant ID:", font=('Helvetica', 16), bg='white')
        self.id_label.place(relx=0.5, rely=0.4, anchor='center')
        self.id_var = tk.StringVar()
        self.id_entry = tk.Entry(self.root, textvariable=self.id_var, font=('Helvetica', 16), width=20)
        self.id_entry.place(relx=0.5, rely=0.45, anchor='center')
        self.start_button = tk.Button(self.root, text="START EXPERIMENT", font=('Helvetica', 20, 'bold'), command=self._start_experiment)
        self.start_button.place(relx=0.5, rely=0.55, anchor='center')

    def _start_experiment(self):
        self.participant_id = self.id_var.get().strip()
        if not self.participant_id:
            messagebox.showwarning("Input Required", "Please enter a valid Participant ID.")
            return
        self.id_label.destroy()
        self.id_entry.destroy()
        self.start_button.destroy()
        self.trial_count = 0
        self.step = 0
        self._next_step()

    def _handle_response(self, given_answer):
        response_time = time.time() - self.start_time
        trial_info = self.stimuli_info.iloc[self.trial_count]
        correct_answer = trial_info['CorrectResponse']
        trial_data = {'Participant_ID': self.participant_id, 'Trial_Number': self.trial_count + 1, 'Stimuli_Name': trial_info['NFW'], 'Correct_Answer': correct_answer, 'Given_Answer': given_answer, 'Is_Correct': 1 if given_answer == correct_answer else 0, 'Response_Time_sec': round(response_time, 4), 'HL_Index': trial_info['HLMarker']}
        self.response_data.append(trial_data)
        self.left_button.destroy()
        self.right_button.destroy()
        feedback_image = self.correct_photo if given_answer == correct_answer else self.wrong_photo
        self.canvas.delete("all")
        self.canvas.create_image(self.root.winfo_width()/2, self.root.winfo_height()/2, image=feedback_image, anchor='center')
        feedback_sound_file = trial_info['CorrectAudio'] if given_answer == correct_answer else trial_info['Wrongaudio']
        playsound(os.path.join(config.STIMULI_FOLDER, feedback_sound_file), block=False)
        self.trial_count += 1
        self.step = 0
        self.root.after(2000, self._next_step)

    def _finish_experiment(self):
        self.canvas.delete("all")
        self.canvas.create_text(750, 400, text="End of the Experiment\nThank you!", font=('Helvetica', 50, 'bold'), justify='center')
        if self.response_data:
            df = pd.DataFrame(self.response_data)
            if not os.path.exists(config.DATA_SAVE_FOLDER): os.makedirs(config.DATA_SAVE_FOLDER)
            save_path = os.path.join(config.DATA_SAVE_FOLDER, f"participant_{self.participant_id}_data.csv")
            df.to_csv(save_path, index=False)
            print(f"Data saved to {save_path}")
        self.root.after(3000, self.root.destroy)

    def _next_step(self):
        self.canvas.delete("all")
        if self.trial_count == -1: self._display_welcome_screen(); return
        if self.trial_count >= self.number_of_stimuli: self._finish_experiment(); return
        if self.step == 0:
            self.canvas.create_text(750, 400, text="+", font=('Helvetica', 200, 'bold'), fill="black")
            self.step = 1
            self.root.after(1000, self._next_step)
        elif self.step == 1:
            trial_info = self.stimuli_info.iloc[self.trial_count]
            playsound(os.path.join(config.STIMULI_FOLDER, trial_info['NFW']))
            time.sleep(0.5)
            playsound(os.path.join(config.STIMULI_FOLDER, trial_info['FinalWord']))
            self.step = 2
            self.root.after(100, self._next_step)
        elif self.step == 2:
            trial_info = self.stimuli_info.iloc[self.trial_count]
            left_img_path = os.path.join(config.STIMULI_FOLDER, trial_info['LeftResponse'])
            self.left_photo = ImageTk.PhotoImage(Image.open(left_img_path))
            self.canvas.create_image(400, 400, image=self.left_photo, anchor='center')
            self.left_button = tk.Button(self.root, text="Select Left", font=('Helvetica', 16), command=lambda: self._handle_response("Left"))
            self.left_button.place(relx=0.27, rely=0.8, anchor='center')
            right_img_path = os.path.join(config.STIMULI_FOLDER, trial_info['RightResponse'])
            self.right_photo = ImageTk.PhotoImage(Image.open(right_img_path))
            self.canvas.create_image(1100, 400, image=self.right_photo, anchor='center')
            self.right_button = tk.Button(self.root, text="Select Right", font=('Helvetica', 16), command=lambda: self._handle_response("Right"))
            self.right_button.place(relx=0.73, rely=0.8, anchor='center')
            self.start_time = time.time()
