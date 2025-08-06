import requests
import sys
import json

prompt = " ".join(sys.argv[1:])

response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "llama3", "prompt": prompt},
    stream=True
)

for line in response.iter_lines():
    if line:
        try:
            data = json.loads(line)
            print(data.get("response", ""), end="", flush=True)
        except json.JSONDecodeError:
            continue
print()
