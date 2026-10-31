# Parakeet AI – Desktop Interview Assistant

## Project Overview

Parakeet AI is a desktop-based AI interview assistant that converts spoken interview questions into text and generates personalized interview answers using locally running AI models.

The application uses speech recognition and a local Large Language Model (LLM) to provide interview assistance without depending on cloud-based AI APIs.

## Features

- Real-time microphone audio recording
- Speech-to-text transcription using Faster-Whisper
- Local AI answer generation using Ollama
- Progressive streaming of AI-generated answers
- Personalized answers based on candidate information
- Copy Answer functionality
- Regenerate Answer functionality
- Clear conversation functionality
- Error handling for microphone and AI connectivity

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Desktop GUI | Tkinter |
| Speech Recognition | Faster-Whisper |
| AI Model Runtime | Ollama |
| Language Model | Llama 3.2 1B |
| Audio Recording | SoundDevice |
| Audio Processing | SoundFile, NumPy |
| API Communication | Requests |

## Project Architecture

1. Microphone captures the interview question.
2. SoundDevice records the audio.
3. Faster-Whisper converts audio into text.
4. The transcribed question is sent to the local Ollama model.
5. The LLM generates a personalized interview answer.
6. The answer is progressively displayed in the desktop application.

## Installation

### Prerequisites

- Windows 10 or Windows 11
- Python 3.11 (64-bit recommended)
- Ollama installed
- Microphone

### Step 1: Clone or extract the project

Open PowerShell in the project directory.

### Step 2: Create a virtual environment

```powershell
python -m venv venv
```

### Step 3: Activate the environment

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 5: Download the local AI model

```powershell
ollama pull llama3.2:1b
```

### Step 6: Start Ollama

Make sure the Ollama server is running before launching the application.

### Step 7: Run the application

```powershell
python main.py
```

## How to Use

1. Launch the desktop application.
2. Click Start Recording.
3. Speak an interview question.
4. Click Stop Recording.
5. Review the transcribed question.
6. Click Suggest Answer.
7. Read the generated answer.
8. Use Copy Answer to copy the response.
9. Use Regenerate Answer for another response.
10. Use Clear to reset the application.

## Privacy and Local Processing

Speech transcription and AI answer generation are designed to run locally using Faster-Whisper and Ollama. No cloud-based AI API is required for the core workflow.

## Project Status

The core desktop application has been implemented and tested, including audio recording, speech transcription, local AI generation, streaming responses, and answer management.

## Author

Sanket Kolhe

B.Tech Computer Engineering, 2026
