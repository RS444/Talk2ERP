
# agent.py
import openai
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("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")

def extract_command(text):
    word_to_num = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
        "ten": 10
    }

    text = text.lower()
    qty = None
    item = None

    if "material request" in text:
        words = text.split()
        for i, word in enumerate(words):
            if word.isdigit():
                qty = int(word)
                if i + 1 < len(words):
                    item = words[i + 1]
                break
            elif word in word_to_num:
                qty = word_to_num[word]
                if i + 1 < len(words):
                    item = words[i + 1]
                break

        if item and qty:
            return {
                "intent": "CREATE_MATERIAL_REQUEST",
                "item": item,
                "qty": qty
            }

    return {
        "intent": None,
        "item": None,
        "qty": None
    }
import streamlit as st
from voice import record_and_transcribe
from agent import extract_command
from erp_api import create_material_request
from gtts import gTTS
import uuid
import os

# Voice function using gTTS and native Streamlit audio
def speak(text):
    filename = f"response_{uuid.uuid4()}.mp3"
    tts = gTTS(text)
    tts.save(filename)

    with open(filename, "rb") as audio_file:
        st.audio(audio_file.read(), format="audio/mp3", autoplay=True)

    os.remove(filename)

st.set_page_config(page_title="🎙️ ERPNext Voice Assistant", layout="centered")
st.title("🎙️ ERPNext Voice Assistant")
st.markdown("Speak a request like **'create material request for 5 chairs'** or use the manual input below")

# Item input options
item_list = ["chairs", "fans", "Plain A4 Sheet", "laptop", "printer"]
request_log = []

with st.expander("📝 Manual Request"):
    selected_item = st.selectbox("Choose Item", item_list)
    selected_qty = st.number_input("Enter Quantity", min_value=1, step=1)
    if st.button("➕ Create Request Manually"):
        with st.spinner(f"Creating manual request for {selected_qty} {selected_item}(s)..."):
            res = create_material_request(selected_item, selected_qty)
        if "data" in res:
            req_id = res["data"]["name"]
            st.success(f"✅ Created Material Request {req_id} for {selected_qty} {selected_item}(s)")
            speak(f"Manual request created for {selected_qty} {selected_item}s")
            request_log.append((req_id, selected_item, selected_qty))
        else:
            st.error(f"❌ Failed to create manual request: {res}")
            speak("Failed to create manual material request")

# Placeholder for result
display = st.empty()

# Voice Input Button
if st.button("🎧 Start Voice Recording"):
    with st.spinner("Listening..."):
        command = record_and_transcribe()
    st.success(f"You said: **{command}**")

    # Parse command
    parsed = extract_command(command)
    st.text(f"🔍 Parsed intent: {parsed}")

    if parsed.get("intent") == "CREATE_MATERIAL_REQUEST" and parsed.get("item") and parsed.get("qty"):
        item = parsed["item"]
        qty = parsed["qty"]

        with st.spinner(f"Creating request for {qty} {item}(s)..."):
            res = create_material_request(item, qty)

        if "data" in res:
            req_id = res["data"]["name"]
            msg = f"✅ Created Material Request {req_id} for {qty} {item}(s)."
            display.success(msg)
            speak(f"Request created for {qty} {item}s")
            request_log.append((req_id, item, qty))

            # Display button
            if st.button("🧾 View Request in ERPNext"):
                st.write("Go to ERPNext > Material Request and find:", req_id)
        else:
            st.error(f"❌ Failed to create request: {res}")
            speak("Failed to create material request")
    else:
        st.warning("❌ Could not understand or unsupported command.")
        speak("I could not understand that command")

# Display Request History
with st.expander("📜 Request History"):
    if request_log:
        for req_id, item, qty in reversed(request_log):
            st.markdown(f"- **{req_id}** → {qty} × {item}")
    else:
        st.write("No requests created yet.")
