import tkinter as tk
from tkinter import ttk, messagebox
import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import requests
import json
import os
from faster_whisper import WhisperModel

# =========================================================
# CONFIGURATION
# =========================================================

SAMPLE_RATE = 16000
CHANNELS = 1
AUDIO_FILE = "recording.wav"

WHISPER_MODEL = "tiny.en"
OLLAMA_MODEL = "llama3.2:1b"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

MICROPHONE_DEVICE = 1

audio_frames = []
recording = False
stream = None
whisper_model = None
generating = False
closing = False
last_question = ""

# =========================================================
# COLOR THEME
# =========================================================

BG = "#0B1020"
SIDEBAR = "#10182B"
CARD = "#151F35"
CARD_DARK = "#0F192E"

PURPLE = "#635BFF"
PURPLE_HOVER = "#5148E8"
CYAN = "#25D9D0"

WHITE = "#F7F8FF"
MUTED = "#91A0BD"
BORDER = "#293653"

GREEN = "#25D9A0"
RED = "#FF637D"

# =========================================================
# CANDIDATE PROFILE
# =========================================================

CANDIDATE_PROFILE = """
Name: Sanket Kolhe
Education: B.Tech Computer Engineering, 2026
CGPA: 8.35/10

Skills:
Python, SQL, MySQL, Flask, FastAPI, React, JavaScript.

Knowledge:
Machine Learning, Generative AI and Data Analytics.

Internship Experience:
Python development and AI-related work.

Projects:
1. AI Interview Assistant.
2. AI-Powered Virtual Fashion Designer.
3. AI Smart Surveillance System using YOLOv8.
4. Drone Airflow Prediction System.

Use only the information provided.
Never invent experience or achievements.
"""

# =========================================================
# APPLICATION WINDOW
# =========================================================

root = tk.Tk()
root.title("Parakeet AI | Interview Copilot")
root.geometry("1200x850")
root.minsize(950, 700)
root.configure(bg=BG)

# =========================================================
# BUTTON STYLES
# =========================================================

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Primary.TButton",
    font=("Segoe UI", 10, "bold"),
    padding=(16, 11),
    background=PURPLE,
    foreground=WHITE,
    borderwidth=0
)

style.map(
    "Primary.TButton",
    background=[
        ("active", PURPLE_HOVER),
        ("disabled", "#34365D")
    ],
    foreground=[
        ("disabled", "#A2A5C1")
    ]
)

style.configure(
    "Secondary.TButton",
    font=("Segoe UI", 9, "bold"),
    padding=(13, 9),
    background="#263451",
    foreground=WHITE,
    borderwidth=0
)

style.map(
    "Secondary.TButton",
    background=[
        ("active", "#344668"),
        ("disabled", "#1B2942")
    ]
)

style.configure(
    "Stop.TButton",
    font=("Segoe UI", 10, "bold"),
    padding=(16, 11),
    background="#482438",
    foreground="#FF8296",
    borderwidth=0
)

style.map(
    "Stop.TButton",
    background=[
        ("active", "#613047")
    ]
)

# =========================================================
# MAIN WINDOW LAYOUT
# =========================================================

main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True)

# =========================================================
# SIDEBAR
# =========================================================

sidebar = tk.Frame(
    main,
    bg=SIDEBAR,
    width=205
)

sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

# Logo

brand = tk.Frame(sidebar, bg=SIDEBAR)
brand.pack(fill="x", padx=17, pady=25)

logo = tk.Label(
    brand,
    text="P",
    font=("Segoe UI", 21, "bold"),
    bg=PURPLE,
    fg=WHITE,
    width=2,
    height=1
)
logo.pack(side="left", padx=(0, 10))

brand_text = tk.Frame(brand, bg=SIDEBAR)
brand_text.pack(side="left")

tk.Label(
    brand_text,
    text="PARAKEET",
    font=("Segoe UI", 12, "bold"),
    bg=SIDEBAR,
    fg=WHITE
).pack(anchor="w")

tk.Label(
    brand_text,
    text="AI COPILOT",
    font=("Segoe UI", 8, "bold"),
    bg=SIDEBAR,
    fg=CYAN
).pack(anchor="w")

# Sidebar navigation

tk.Label(
    sidebar,
    text="WORKSPACE",
    font=("Segoe UI", 8, "bold"),
    bg=SIDEBAR,
    fg="#71809D"
).pack(anchor="w", padx=20, pady=(35, 12))


def sidebar_item(text, active=False):
    color = "#292858" if active else SIDEBAR
    fg = "#AFAAFF" if active else MUTED

    item = tk.Frame(sidebar, bg=color)
    item.pack(fill="x", padx=11, pady=4)

    tk.Label(
        item,
        text=text,
        font=("Segoe UI", 10, "bold"),
        bg=color,
        fg=fg,
        anchor="w",
        padx=12,
        pady=12
    ).pack(fill="x")


sidebar_item("▣   Interview Studio", True)
sidebar_item("◉   Voice Recording")
sidebar_item("✦   AI Assistant")
sidebar_item("▤   Candidate Profile")

# Sidebar bottom

bottom = tk.Frame(sidebar, bg=SIDEBAR)
bottom.pack(side="bottom", fill="x", padx=17, pady=20)

tk.Frame(
    bottom,
    bg=BORDER,
    height=1
).pack(fill="x", pady=(0, 15))

tk.Label(
    bottom,
    text="LOCAL AI ENGINE",
    font=("Segoe UI", 8, "bold"),
    bg=SIDEBAR,
    fg=MUTED
).pack(anchor="w")

tk.Label(
    bottom,
    text="● Whisper + Ollama",
    font=("Segoe UI", 9),
    bg=SIDEBAR,
    fg=GREEN
).pack(anchor="w", pady=7)

tk.Label(
    bottom,
    text="Version 1.0.0",
    font=("Segoe UI", 8),
    bg=SIDEBAR,
    fg="#71809D"
).pack(anchor="w")

# =========================================================
# MAIN WORKSPACE
# =========================================================

workspace = tk.Frame(main, bg=BG)
workspace.pack(side="left", fill="both", expand=True)

# Top bar

topbar = tk.Frame(
    workspace,
    bg=BG,
    height=65
)
topbar.pack(fill="x", padx=28, pady=(12, 0))

tk.Label(
    topbar,
    text="Interview Studio",
    font=("Segoe UI", 18, "bold"),
    bg=BG,
    fg=WHITE
).pack(side="left", pady=12)

online_label = tk.Label(
    topbar,
    text="● SYSTEM ONLINE",
    font=("Segoe UI", 8, "bold"),
    bg="#15382F",
    fg=GREEN,
    padx=12,
    pady=7
)
online_label.pack(side="right", pady=12)

# =========================================================
# SCROLLABLE CONTENT AREA
# =========================================================

canvas = tk.Canvas(
    workspace,
    bg=BG,
    highlightthickness=0
)

scrollbar = ttk.Scrollbar(
    workspace,
    orient="vertical",
    command=canvas.yview
)

canvas.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(15, 0)
)

scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)

content = tk.Frame(canvas, bg=BG)

window_id = canvas.create_window(
    (0, 0),
    window=content,
    anchor="nw"
)


def update_scroll_region(event=None):
    canvas.configure(
        scrollregion=canvas.bbox("all")
    )


def resize_content(event):
    canvas.itemconfigure(
        window_id,
        width=event.width
    )


content.bind(
    "<Configure>",
    update_scroll_region
)

canvas.bind(
    "<Configure>",
    resize_content
)


def mousewheel(event):
    canvas.yview_scroll(
        int(-1 * (event.delta / 120)),
        "units"
    )


canvas.bind_all("<MouseWheel>", mousewheel)

# =========================================================
# HERO SECTION
# =========================================================

hero = tk.Frame(
    content,
    bg="#171D3B",
    highlightbackground="#38366F",
    highlightthickness=1
)

hero.pack(
    fill="x",
    padx=15,
    pady=(15, 20)
)

hero_inner = tk.Frame(hero, bg="#171D3B")
hero_inner.pack(fill="x", padx=24, pady=23)

tk.Label(
    hero_inner,
    text="YOUR PERSONAL INTERVIEW ASSISTANT",
    font=("Segoe UI", 8, "bold"),
    bg="#171D3B",
    fg=CYAN
).pack(anchor="w")

tk.Label(
    hero_inner,
    text="Ace your next interview.",
    font=("Segoe UI", 24, "bold"),
    bg="#171D3B",
    fg=WHITE
).pack(anchor="w", pady=(8, 4))

tk.Label(
    hero_inner,
    text="Listen. Understand. Answer with confidence.",
    font=("Segoe UI", 10),
    bg="#171D3B",
    fg="#B4BBD5"
).pack(anchor="w")

# =========================================================
# RECORDING CARD
# =========================================================

record_card = tk.Frame(
    content,
    bg=CARD,
    highlightbackground=BORDER,
    highlightthickness=1
)

record_card.pack(
    fill="x",
    padx=15,
    pady=(0, 17)
)

record_inner = tk.Frame(record_card, bg=CARD)
record_inner.pack(fill="x", padx=20, pady=17)

record_info = tk.Frame(record_inner, bg=CARD)
record_info.pack(side="left", fill="y")

tk.Label(
    record_info,
    text="VOICE CAPTURE",
    font=("Segoe UI", 9, "bold"),
    bg=CARD,
    fg=CYAN
).pack(anchor="w")

tk.Label(
    record_info,
    text="Record the interviewer's question",
    font=("Segoe UI", 10),
    bg=CARD,
    fg=WHITE
).pack(anchor="w", pady=(5, 0))

record_buttons = tk.Frame(record_inner, bg=CARD)
record_buttons.pack(side="right")

# =========================================================
# STATUS CARD
# =========================================================

status_card = tk.Frame(
    content,
    bg="#122B2A",
    highlightbackground="#20534B",
    highlightthickness=1
)

status_card.pack(
    fill="x",
    padx=15,
    pady=(0, 17)
)

status_label = tk.Label(
    status_card,
    text="● Ready to record",
    font=("Segoe UI", 9, "bold"),
    bg="#122B2A",
    fg=GREEN,
    anchor="w",
    padx=16,
    pady=12
)

status_label.pack(fill="x")

# =========================================================
# QUESTION CARD
# =========================================================

transcript_card = tk.Frame(
    content,
    bg=CARD,
    highlightbackground=BORDER,
    highlightthickness=1
)

transcript_card.pack(
    fill="x",
    padx=15,
    pady=(0, 17)
)

transcript_header = tk.Frame(transcript_card, bg=CARD)
transcript_header.pack(fill="x", padx=17, pady=(15, 10))

tk.Label(
    transcript_header,
    text="01  |  Interview Question",
    font=("Segoe UI", 12, "bold"),
    bg=CARD,
    fg=WHITE
).pack(anchor="w")

tk.Label(
    transcript_header,
    text="Your recognized speech appears below. You can edit it.",
    font=("Segoe UI", 8),
    bg=CARD,
    fg=MUTED
).pack(anchor="w", pady=(4, 0))

transcript_area = tk.Frame(transcript_card, bg=CARD)
transcript_area.pack(
    fill="both",
    expand=True,
    padx=17,
    pady=(0, 13)
)

transcript_box = tk.Text(
    transcript_area,
    height=6,
    font=("Segoe UI", 10),
    wrap="word",
    bg=CARD_DARK,
    fg=WHITE,
    insertbackground=CYAN,
    selectbackground="#343D73",
    relief="flat",
    padx=14,
    pady=13,
    undo=True
)

transcript_box.pack(fill="both", expand=True)

transcript_box.configure(
    highlightthickness=1,
    highlightbackground=BORDER,
    highlightcolor=PURPLE
)

# =========================================================
# AI ANSWER CARD
# =========================================================

answer_card = tk.Frame(
    content,
    bg=CARD,
    highlightbackground=BORDER,
    highlightthickness=1
)

answer_card.pack(
    fill="x",
    padx=15,
    pady=(0, 17)
)

answer_header = tk.Frame(answer_card, bg=CARD)
answer_header.pack(fill="x", padx=17, pady=(15, 10))

tk.Label(
    answer_header,
    text="02  |  AI Generated Answer",
    font=("Segoe UI", 12, "bold"),
    bg=CARD,
    fg=WHITE
).pack(anchor="w")

tk.Label(
    answer_header,
    text="Your personalized interview response, generated locally.",
    font=("Segoe UI", 8),
    bg=CARD,
    fg=MUTED
).pack(anchor="w", pady=(4, 0))

answer_area = tk.Frame(answer_card, bg=CARD)
answer_area.pack(
    fill="both",
    expand=True,
    padx=17,
    pady=(0, 13)
)

answer_box = tk.Text(
    answer_area,
    height=10,
    font=("Segoe UI", 10),
    wrap="word",
    bg=CARD_DARK,
    fg=WHITE,
    insertbackground=CYAN,
    selectbackground="#343D73",
    relief="flat",
    padx=14,
    pady=13
)

answer_box.pack(fill="both", expand=True)

answer_box.configure(
    highlightthickness=1,
    highlightbackground=BORDER,
    highlightcolor=CYAN
)

# =========================================================
# ANSWER BUTTONS
# =========================================================

answer_controls = tk.Frame(answer_card, bg=CARD)
answer_controls.pack(
    fill="x",
    padx=17,
    pady=(0, 17)
)

# =========================================================
# FOOTER
# =========================================================

footer = tk.Frame(content, bg=BG)
footer.pack(fill="x", padx=15, pady=(5, 20))

tk.Label(
    footer,
    text="FASTER-WHISPER  •  OLLAMA  •  LOCAL AI",
    font=("Segoe UI", 8, "bold"),
    bg=BG,
    fg=MUTED
).pack(anchor="center")

# =========================================================
# STATUS AND ERROR HELPERS
# =========================================================

def update_status(text, color=GREEN):
    if closing:
        return

    def update():
        if not closing:
            status_label.config(text="● " + text, fg=color)

    root.after(0, update)


def show_error(error):
    if closing:
        return

    def display():
        if closing:
            return

        update_status("An error occurred", RED)
        messagebox.showerror(
            "Application Error",
            error
        )

    root.after(0, display)

# =========================================================
# MICROPHONE CALLBACK
# =========================================================

def audio_callback(indata, frames, time_info, status):
    if status:
        print("Audio status:", status)

    if recording:
        audio_frames.append(indata.copy())

# =========================================================
# START RECORDING
# =========================================================

def start_recording():
    global recording, stream, audio_frames

    if recording or generating:
        return

    audio_frames = []

    try:
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32",
            callback=audio_callback,
            device=MICROPHONE_DEVICE
        )

        stream.start()
        recording = True

        start_button.config(state="disabled")
        stop_button.config(state="normal")
        suggest_button.config(state="disabled")

        transcript_box.delete("1.0", tk.END)
        answer_box.delete("1.0", tk.END)

        copy_button.config(state="disabled")
        regenerate_button.config(state="disabled")

        update_status(
            "Recording... Speak now",
            GREEN
        )

    except Exception as e:
        recording = False
        show_error("Microphone error: " + str(e))

# =========================================================
# STOP RECORDING
# =========================================================

def stop_recording():
    global recording, stream

    if not recording:
        return

    recording = False

    try:
        if stream:
            stream.stop()
            stream.close()
            stream = None

        if not audio_frames:
            update_status("No audio detected", RED)
            start_button.config(state="normal")
            stop_button.config(state="disabled")
            return

        audio = np.concatenate(audio_frames, axis=0)

        sf.write(
            AUDIO_FILE,
            audio,
            SAMPLE_RATE
        )

        start_button.config(state="normal")
        stop_button.config(state="disabled")

        update_status(
            "Transcribing your speech...",
            PURPLE
        )

        threading.Thread(
            target=transcribe_audio,
            daemon=True
        ).start()

    except Exception as e:
        show_error("Recording error: " + str(e))

# =========================================================
# WHISPER MODEL
# =========================================================

def load_whisper_model():
    global whisper_model

    if whisper_model is None:
        update_status(
            "Loading Whisper model...",
            PURPLE
        )

        whisper_model = WhisperModel(
            WHISPER_MODEL,
            device="cpu",
            compute_type="int8",
            cpu_threads=2,
            num_workers=1
        )

    return whisper_model

# =========================================================
# TRANSCRIPTION
# =========================================================

def transcribe_audio():
    try:
        model = load_whisper_model()

        update_status(
            "Transcribing your speech...",
            PURPLE
        )

        segments, info = model.transcribe(
            AUDIO_FILE,
            beam_size=3
        )

        transcription = " ".join(
            segment.text.strip()
            for segment in segments
        ).strip()

        root.after(
            0,
            lambda: show_transcription(transcription)
        )

    except Exception as e:
        show_error("Transcription error: " + str(e))


def show_transcription(text):
    transcript_box.delete("1.0", tk.END)
    transcript_box.insert(tk.END, text)

    if text:
        update_status(
            "Transcription completed successfully!",
            GREEN
        )
        suggest_button.config(state="normal")
    else:
        update_status(
            "No speech detected. Try again.",
            RED
        )
        suggest_button.config(state="disabled")

# =========================================================
# INTERVIEW PROMPT
# =========================================================

def build_prompt(question):
    return f"""
You are a professional technical interview assistant.

CANDIDATE PROFILE:
{CANDIDATE_PROFILE}

INTERVIEW QUESTION:
{question}

INSTRUCTIONS:
1. The candidate's name is Sanket Kolhe.
2. Never use placeholders.
3. For introduction questions, start with:
   Hello, my name is Sanket Kolhe.
4. Answer directly as the candidate.
5. Use first-person language for personal questions.
6. Use simple, confident and professional English.
7. Keep HR answers around 70-120 words.
8. Explain technical concepts accurately.
9. Mention relevant skills and projects when useful.
10. Never invent employment history or achievements.
11. Output only the final interview answer.

FINAL ANSWER:
"""

# =========================================================
# GENERATE ANSWER
# =========================================================

def suggest_answer():
    global last_question

    if generating:
        return

    question = transcript_box.get(
        "1.0",
        tk.END
    ).strip()

    if not question:
        messagebox.showwarning(
            "Missing Question",
            "Please record or enter an interview question first."
        )
        return

    last_question = question
    start_ai_generation(question)


def start_ai_generation(question):
    global generating

    if generating:
        return

    generating = True

    suggest_button.config(state="disabled")
    regenerate_button.config(state="disabled")
    copy_button.config(state="disabled")

    answer_box.delete("1.0", tk.END)

    update_status(
        "AI is preparing your answer...",
        PURPLE
    )

    threading.Thread(
        target=generate_ai_answer,
        args=(question,),
        daemon=True
    ).start()

# =========================================================
# OLLAMA STREAMING
# =========================================================

def generate_ai_answer(question):
    error_message = None

    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": build_prompt(question),
            "stream": True,
            "options": {
                "temperature": 0.3,
                "num_ctx": 2048,
                "num_predict": 180
            }
        }

        with requests.post(
            OLLAMA_URL,
            json=payload,
            stream=True,
            timeout=(10, 300)
        ) as response:

            response.raise_for_status()

            for line in response.iter_lines():
                if closing:
                    break

                if not line:
                    continue

                data = json.loads(
                    line.decode("utf-8")
                )

                token = data.get("response", "")

                if token:
                    root.after(
                        0,
                        lambda t=token: append_answer(t)
                    )

                if data.get("done"):
                    break

    except requests.exceptions.ConnectionError:
        error_message = (
            "Cannot connect to Ollama.\n\n"
            "Start the Ollama CPU server and try again."
        )

    except requests.exceptions.Timeout:
        error_message = (
            "AI response timed out. Please try again."
        )

    except requests.exceptions.HTTPError as e:
        details = (
            e.response.text
            if e.response is not None
            else ""
        )

        error_message = (
            "Ollama server error:\n"
            + str(e)
            + "\n"
            + details
        )

    except Exception as e:
        error_message = "AI generation error: " + str(e)

    finally:
        if not closing:
            root.after(
                0,
                lambda err=error_message: finish_generation(err)
            )


def append_answer(token):
    if closing:
        return

    answer_box.insert(tk.END, token)
    answer_box.see(tk.END)


def finish_generation(error_message):
    global generating

    generating = False

    if error_message:
        update_status(
            "AI generation failed",
            RED
        )

        suggest_button.config(state="normal")

        messagebox.showerror(
            "AI Error",
            error_message
        )
        return

    answer = answer_box.get(
        "1.0",
        tk.END
    ).strip()

    if answer:
        update_status(
            "AI answer generated successfully!",
            GREEN
        )

        copy_button.config(state="normal")
        regenerate_button.config(state="normal")
    else:
        update_status(
            "AI returned an empty answer.",
            RED
        )

    suggest_button.config(state="normal")

# =========================================================
# COPY ANSWER
# =========================================================

def copy_answer():
    answer = answer_box.get(
        "1.0",
        tk.END
    ).strip()

    if not answer:
        messagebox.showwarning(
            "No Answer",
            "Generate an answer before copying."
        )
        return

    try:
        root.clipboard_clear()
        root.clipboard_append(answer)
        root.update()

        update_status(
            "Answer copied to clipboard!",
            GREEN
        )

    except Exception as e:
        show_error("Copy failed: " + str(e))

# =========================================================
# REGENERATE
# =========================================================

def regenerate_answer():
    if generating:
        return

    if not last_question:
        messagebox.showwarning(
            "No Question",
            "Please generate an answer first."
        )
        return

    start_ai_generation(last_question)

# =========================================================
# CLEAR ALL
# =========================================================

def clear_all():
    global last_question

    if recording or generating:
        return

    last_question = ""

    transcript_box.delete("1.0", tk.END)
    answer_box.delete("1.0", tk.END)

    suggest_button.config(state="disabled")
    copy_button.config(state="disabled")
    regenerate_button.config(state="disabled")

    update_status(
        "Ready to record",
        GREEN
    )

# =========================================================
# CLOSE APPLICATION
# =========================================================

def close_app():
    global recording, stream, closing

    closing = True
    recording = False

    if stream is not None:
        try:
            stream.stop()
            stream.close()
        except Exception:
            pass

    root.destroy()

# =========================================================
# CREATE BUTTONS
# =========================================================

start_button = ttk.Button(
    record_buttons,
    text="●  Start Listening",
    command=start_recording,
    style="Primary.TButton"
)
start_button.pack(side="left", padx=4)

stop_button = ttk.Button(
    record_buttons,
    text="■  Stop",
    command=stop_recording,
    style="Stop.TButton",
    state="disabled"
)
stop_button.pack(side="left", padx=4)

clear_button = ttk.Button(
    record_buttons,
    text="Clear",
    command=clear_all,
    style="Secondary.TButton"
)
clear_button.pack(side="left", padx=4)

suggest_button = ttk.Button(
    transcript_card,
    text="✦  Generate AI Answer",
    command=suggest_answer,
    style="Primary.TButton",
    state="disabled"
)
suggest_button.pack(
    anchor="w",
    padx=17,
    pady=(0, 17)
)

copy_button = ttk.Button(
    answer_controls,
    text="▣  Copy Answer",
    command=copy_answer,
    style="Secondary.TButton",
    state="disabled"
)
copy_button.pack(side="left", padx=(0, 8))

regenerate_button = ttk.Button(
    answer_controls,
    text="↻  Regenerate",
    command=regenerate_answer,
    style="Secondary.TButton",
    state="disabled"
)
regenerate_button.pack(side="left")

# =========================================================
# START APPLICATION
# =========================================================

root.protocol(
    "WM_DELETE_WINDOW",
    close_app
)

root.mainloop()