import streamlit as st
import sqlite3
import os
import requests
import json

DB_PATH = "memory.db"
WORKSPACE_PATH = os.path.abspath("..")

# Chat Section
st.title("🦙 Gringo AI Cockpit - God Mode")

prompt = st.text_area("Enter prompt:")

if st.button("Send to LLaMA"):
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
    st.write(full_response)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO memory (timestamp, prompt, response) VALUES (datetime("now"), ?, ?)', (prompt, full_response))
    conn.commit()
    conn.close()

# Memory Section
st.subheader("🧠 Memory Log")
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT timestamp, prompt, response FROM memory ORDER BY id DESC LIMIT 10')
    logs = c.fetchall()
    for log in logs:
        st.markdown(f"**[{log[0]}] Prompt:** {log[1]}")
        st.markdown(f"**Response:** {log[2]}")
    conn.close()

# File Section
st.subheader("�� File Browser")
for root, dirs, files in os.walk(WORKSPACE_PATH):
    for file in files:
        if st.button(file):
            with open(os.path.join(root, file), "r") as f:
                content = f.read()
            st.text_area(f"Editing {file}", content, height=300)
