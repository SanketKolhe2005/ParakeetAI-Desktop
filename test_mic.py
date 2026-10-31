
import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel

print("Loading Whisper model...")
model = WhisperModel(
    "tiny.en",
    device="cpu",
    compute_type="int8",
    cpu_threads=2
)

print("Speak now! Recording for 8 seconds...")

audio = sd.rec(
    16000 * 8,
    samplerate=16000,
    channels=1,
    dtype="float32",
    device=1
)

sd.wait()
sf.write("test_recording.wav", audio, 16000)

print("Recording completed. Transcribing...")

segments, info = model.transcribe("test_recording.wav")

result = " ".join(segment.text for segment in segments)

print("\nYour spoken words:")
print(result if result else "No speech detected.")
