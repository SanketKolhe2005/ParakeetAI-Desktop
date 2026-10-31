
import requests
import json

url = "http://localhost:11434/api/generate"

payload = {
    "model": "llama3.2:1b",
    "prompt": "What is Python? Explain in 3 simple sentences.",
    "stream": True
}

print("AI is generating an answer:\n")

with requests.post(url, json=payload, stream=True) as response:
    response.raise_for_status()

    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            print(data.get("response", ""), end="", flush=True)

print("\n\nAI response completed!")
