import tkinter as tk
from gtts import gTTS
import os
import random
import threading
import speech_recognition as sr
import openai

# OpenAI API Key
openai.api_key = "YOUR_OPENAI_API_KEY"

# Initialize Recognizer and Globals
recognizer = sr.Recognizer()
questions_index = 0
timer_running = False

# Load Questions
def read_questions(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return [line.strip() for line in lines if line.strip()]

file_path = "Speaking_Formatted_Final.txt"
questions = read_questions(file_path)
random.shuffle(questions)

# Countdown Timer
def countdown(duration):
    def run_timer():
        nonlocal duration
        if duration >= 0:
            minutes, seconds = divmod(duration, 60)
            timer_label.config(text=f"Time left: {minutes:02d}:{seconds:02d}")
            duration -= 1
            root.after(1000, run_timer)  
        else:
            timer_label.config(text="Time's up!")
            next_question_button.config(state=tk.NORMAL)
    run_timer()

# Text-to-Speech
def speak_text(text):
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save("speak.mp3")
    os.system("open speak.mp3" if os.name == "posix" else "start speak.mp3")

# Listen to User Answer
def listen_to_answer():
    try:
        speaking_label.config(text="Listening... Speak now!")
        root.update()
        with sr.Microphone() as input_device:
            recognizer.adjust_for_ambient_noise(input_device)
            audio_data = recognizer.listen(input_device, timeout=45)
            answer_text = recognizer.recognize_google(audio_data)
            speaking_label.config(text="Listening complete.")
            return answer_text
    except Exception as e:
        print(f"Speech Recognition Error: {e}")
        return "Could not understand the answer."

# Evaluate Answer using OpenAI
def evaluate_answer(answer_text):
    try:
        prompt = f"Rate this speaking answer: '{answer_text}'. Respond in this format: Band Score (1-9) - Short feedback (2 sentences)."
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return "Feedback not available."

# Process User Answer
def process_answer():
    answer_text = listen_to_answer()
    answer_label.config(text=f"Your answer: {answer_text}")
    feedback = evaluate_answer(answer_text)
    answer_label.config(text=f"Your answer: {answer_text}\nEvaluation: {feedback}")
    next_question_button.config(state=tk.NORMAL)

# Start the Test
def start_assistant():
    start_button.pack_forget()
    speak_text("Welcome to the Speaking Practice Test.")
    root.after(3000, next_question)

# Display Next Question
def next_question():
    global questions_index
    next_question_button.config(state=tk.DISABLED)
    
    if questions_index < len(questions):
        question = questions[questions_index]
        question_label.config(text=f"Question {questions_index + 1}: {question}")
        speak_text(question)
        questions_index += 1
        countdown(45) 
        threading.Thread(target=process_answer).start()
    else:
        question_label.config(text="You have completed the test!")
        next_question_button.config(state=tk.DISABLED)
        
# GUI Setup
root = tk.Tk()
root.title("Practice Speaking Test")

frame = tk.Frame(root)
frame.pack(pady=20)

# Labels
title_label = tk.Label(frame, text="Speaking Test", font=("Helvetica", 18))
title_label.pack(pady=10)

question_label = tk.Label(frame, text="", font=("Helvetica", 14), wraplength=500)
question_label.pack(pady=5)

answer_label = tk.Label(frame, text="", font=("Helvetica", 12), wraplength=500, fg="blue")
answer_label.pack(pady=5)

timer_label = tk.Label(frame, text="", font=("Helvetica", 12), fg="red")
timer_label.pack(pady=5)

speaking_label = tk.Label(frame, text="", font=("Helvetica", 12), fg="green")
speaking_label.pack(pady=5)

# Buttons
start_button = tk.Button(frame, text="Start", font=("Helvetica", 14), command=start_assistant)
start_button.pack(pady=20)

next_question_button = tk.Button(frame, text="Next Question", font=("Helvetica", 14), command=next_question)
next_question_button.pack(pady=20)
next_question_button.config(state=tk.DISABLED)

# Start GUI
root.mainloop()
