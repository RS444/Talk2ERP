import streamlit as st
from voice import record_and_transcribe
from agent import extract_command
from erp_api import create_material_request
from gtts import gTTS
import uuid
import os
import requests
from datetime import datetime

# ----------------------------- SPEECH SETUP -----------------------------
def speak(text):
    filename = f"response_{uuid.uuid4()}.mp3"
    tts = gTTS(text)
    tts.save(filename)
    with open(filename, "rb") as audio_file:
        st.audio(audio_file.read(), format="audio/mp3", autoplay=True)
    os.remove(filename)

# ----------------------------- LOGIN HANDLER -----------------------------
def erpnext_login(email, api_key, api_secret):
    headers = {
        "Authorization": f"token {api_key}:{api_secret}",
        "Content-Type": "application/json"
    }
    url = "http://localhost:8000/api/resource/User"
    res = requests.get(url, headers=headers)
    return res.status_code == 200

# ----------------------------- PAGE CONFIG -----------------------------
st.set_page_config(
    page_title="🎙️ ERPNext Voice Assistant",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ----------------------------- LOGIN UI -----------------------------
st.markdown("<h1 style='text-align:center; color:#2c3e50;'>🔐 ERPNext Login</h1>", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.container():
        email = st.text_input("📧 Email")
        api_key = st.text_input("🔑 API Key")
        api_secret = st.text_input("🕵️‍♂️ API Secret", type="password")

        col1, col2, _ = st.columns([1,1,3])
        with col1:
            if st.button("🔓 Login", use_container_width=True):
                if erpnext_login(email, api_key, api_secret):
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.session_state.api_key = api_key
                    st.session_state.api_secret = api_secret
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")
        with col2:
            st.button("🔁 Clear", on_click=lambda: st.session_state.clear(), use_container_width=True)

    st.stop()

# ----------------------------- MAIN DASHBOARD -----------------------------
st.markdown("<h1 style='text-align:center; color:#1abc9c;'>🎙️ ERPNext Voice Assistant</h1>", unsafe_allow_html=True)
st.info("🗣️ Speak a request like: *create material request for 5 chairs* or use the form below")

item_list = ["chairs", "fans", "Plain A4 Sheet", "laptop", "printer"]
request_log = []

# ----------------------------- MANUAL REQUEST -----------------------------
with st.expander("📝 Manual Material Request Form", expanded=True):
    st.subheader("🛒 Create Material Request")
    col1, col2 = st.columns(2)
    with col1:
        selected_item = st.selectbox("🔍 Choose Item", item_list, key="manual_selectbox")
    with col2:
        selected_qty = st.number_input("🔢 Enter Quantity", min_value=1, step=1, key="manual_qty_input")

    if st.button("📦 Submit Request", key="manual_create_btn", use_container_width=True):
        with st.spinner(f"📤 Sending request for {selected_qty} × {selected_item}..."):
            res = create_material_request(
                selected_item,
                selected_qty,
                st.session_state.api_key,
                st.session_state.api_secret
            )
        if "data" in res:
            req_id = res["data"]["name"]
            st.success(f"✅ Request {req_id} created!")
            speak(f"Material request for {selected_qty} {selected_item}s submitted.")
            request_log.append((req_id, selected_item, selected_qty))
        else:
            st.error(f"❌ Request failed: {res}")
            speak("Failed to create manual material request")

# ----------------------------- VOICE REQUEST -----------------------------
st.divider()
st.subheader("🎧 Voice Command")
display = st.empty()

if st.button("🎙️ Start Listening", key="voice_record_btn", use_container_width=True):
    with st.spinner("🎤 Listening for command..."):
        command = record_and_transcribe()
    st.success(f"🗣️ You said: *{command}*")

    parsed = extract_command(command)
    st.code(parsed, language="json")

    if parsed.get("intent") == "CREATE_MATERIAL_REQUEST" and parsed.get("item") and parsed.get("qty"):
        item = parsed["item"]
        qty = parsed["qty"]
        with st.spinner(f"Creating voice request for {qty} × {item}..."):
            res = create_material_request(
                item,
                qty,
                st.session_state.api_key,
                st.session_state.api_secret
            )
        if "data" in res:
            req_id = res["data"]["name"]
            display.success(f"✅ Voice Material Request {req_id} created!")
            speak(f"Created material request for {qty} {item}s")
            request_log.append((req_id, item, qty))
            if st.button("📄 View in ERPNext", key="view_request_btn"):
                st.write("Go to ERPNext > Material Request and search for:", req_id)
        else:
            st.error(f"❌ Request failed: {res}")
            speak("Could not create voice material request")
    else:
        st.warning("❗ Unrecognized command. Please try again.")
        speak("I could not understand that command")

# ----------------------------- HISTORY -----------------------------
st.divider()
st.subheader("📜 Request History")
with st.container():
    if request_log:
        for req_id, item, qty in reversed(request_log):
            st.markdown(f"✅ **{req_id}** — {qty} × *{item}*  ")
    else:
        st.write("No requests created yet.")
