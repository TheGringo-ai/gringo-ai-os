from fastapi import FastAPI, Query
import sqlite3
import os
import requests
import json

app = FastAPI(title="Gringo AI Death Server")

DB_PATH = "memory.db"
WORKSPACE_PATH = os.path.abspath("..")

# Ollama Chat Endpoint
@app.post("/chat")
def chat(prompt: str):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3", "prompt": prompt},
        stream=True
    )

    full_response = ""
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line)
                full_response += data.get("response", "")
            except json.JSONDecodeError:
                continue

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO memory (timestamp, prompt, response) VALUES (datetime("now"), ?, ?)',
              (prompt, full_response))
    conn.commit()
    conn.close()

    return {"response": full_response}

# Memory Search Endpoint
@app.get("/memory")
def search_memory(keyword: str = Query(...)):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT timestamp, prompt, response FROM memory WHERE prompt LIKE ? OR response LIKE ?',
              (f"%{keyword}%", f"%{keyword}%"))
    results = c.fetchall()
    conn.close()
    return {"results": results}

# File List Endpoint
@app.get("/files")
def list_files():
    files_list = []
    for root, dirs, files in os.walk(WORKSPACE_PATH):
        for file in files:
            files_list.append(os.path.join(root, file))
    return {"files": files_list}

# File Read Endpoint
@app.get("/read")
def read_file(path: str):
    try:
        with open(path, "r") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        return {"error": str(e)}

# File Write Endpoint
@app.post("/write")
def write_file(path: str, content: str):
    try:
        with open(path, "w") as f:
            f.write(content)
        return {"status": f"Updated {path}"}
    except Exception as e:
        return {"error": str(e)}
