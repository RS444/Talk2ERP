import streamlit as st
from voice import record_and_transcribe
from agent import extract_command
from erp_api import (
    create_material_request,
    approve_material_request,
    get_draft_requests
)
from gtts import gTTS
import uuid
import os
import requests
from datetime import datetime

# -------------------- SPEAK FUNCTION --------------------
def speak(text):
    filename = f"response_{uuid.uuid4()}.mp3"
    tts = gTTS(text)
    tts.save(filename)
    with open(filename, "rb") as audio_file:
        st.audio(audio_file.read(), format="audio/mp3", autoplay=True)
    os.remove(filename)

# -------------------- LOGIN CHECK --------------------
def erpnext_login(email, api_key, api_secret):
    headers = {
        "Authorization": f"token {api_key}:{api_secret}",
        "Content-Type": "application/json"
    }
    try:
        url = "https://bc199703e0ec.ngrok-free.app/api/resource/User"
        res = requests.get(url, headers=headers)
        return res.status_code == 200
    except:
        return False

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Talk2ERP", page_icon="🎙️", layout="centered")
st.title("🎙️ Talk2ERP - Voice Assistant")

# -------------------- SESSION STATE INIT --------------------
for key in ["logged_in", "api_key", "api_secret", "email", "role"]:
    if key not in st.session_state:
        st.session_state[key] = None

# -------------------- LOGIN PANEL --------------------
if not st.session_state.logged_in:
    with st.form("login_form"):
        st.subheader("🔐 ERP Login")
        email = st.text_input("Email")
        api_key = st.text_input("API Key")
        api_secret = st.text_input("API Secret", type="password")
        role = st.selectbox("Select Role", ["HR", "Purchase Manager"])
        submitted = st.form_submit_button("Login")

        if submitted:
            if erpnext_login(email, api_key, api_secret):
                st.session_state.logged_in = True
                st.session_state.api_key = api_key
                st.session_state.api_secret = api_secret
                st.session_state.email = email
                st.session_state.role = role
                st.success("✅ Login successful")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

# -------------------- DASHBOARD --------------------
if st.session_state.logged_in:
    st.sidebar.success(f"👤 Logged in as: {st.session_state.email} ({st.session_state.role})")
    if st.sidebar.button("🚪 Logout"):
        for key in st.session_state:
            st.session_state[key] = None
        st.rerun()

    role = st.session_state.role
    api_key = st.session_state.api_key
    api_secret = st.session_state.api_secret
    email = st.session_state.email

    # -------------------- HR PANEL --------------------
    if role == "HR":
        st.subheader("📦 Create Material Request")
        item_list = ["chairs", "fans", "Plain A4 Sheet", "laptop", "printer"]
        request_log = []

        col1, col2 = st.columns(2)
        with col1:
            item = st.selectbox("Choose Item", item_list)
        with col2:
            qty = st.number_input("Quantity", min_value=1, step=1)

        if st.button("📝 Submit Request"):
            with st.spinner(f"Creating request for {qty} {item}(s)..."):
                res = create_material_request(item, qty, api_key, api_secret)
            if "data" in res:
                req_id = res["data"]["name"]
                st.success(f"✅ Request {req_id} created.")
                speak(f"Material request for {qty} {item}s submitted.")
                request_log.append((req_id, item, qty))
            else:
                st.error(f"❌ Request failed: {res}")
                speak("Request failed.")

        st.divider()
        st.subheader("🎧 Voice Command")
        if st.button("🎙️ Start Listening"):
            with st.spinner("Listening..."):
                command = record_and_transcribe()
            st.success(f"You said: **{command}**")
            parsed = extract_command(command)

            if parsed.get("intent") == "CREATE_MATERIAL_REQUEST":
                item = parsed["item"]
                qty = parsed["qty"]
                with st.spinner(f"Creating request for {qty} {item}(s)..."):
                    res = create_material_request(item, qty, api_key, api_secret)
                if "data" in res:
                    req_id = res["data"]["name"]
                    st.success(f"✅ Created request {req_id}")
                    speak(f"Request created for {qty} {item}s")
                    request_log.append((req_id, item, qty))
                else:
                    st.error("❌ Failed to create request")
                    speak("Failed to create request")
            else:
                st.warning("⚠️ Unrecognized command")
                speak("Command not understood")

        # HR sees reminder
        st.divider()
        st.subheader("🔔 Pending Requests Reminder")
        pending = get_draft_requests(api_key, api_secret, email)
        if pending:
            st.info(f"📋 You have {len(pending)} draft Material Request(s):")
            for req in pending:
                st.markdown(f"- **{req['name']}** (Owner: `{req['owner']}`, Status: `{req['status']}`)")
        else:
            st.success("✅ No pending draft requests.")

    # -------------------- PM PANEL --------------------
    elif role == "Purchase Manager":
        st.subheader("🧾 Material Request Approval Panel")
        requests = get_draft_requests(api_key, api_secret)

        if requests:
            for req in requests:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{req['name']}** by `{req['owner']}` | Date: {req['transaction_date']}")
                    with col2:
                        if st.button(f"✅ Approve {req['name']}", key=req['name']):
                            result = approve_material_request(req["name"], api_key, api_secret)
                            if "data" in result:
                                st.success(f"✅ Approved {req['name']}")
                                speak(f"Approved request {req['name']}")
                                st.rerun()
                            else:
                                st.error("❌ Approval failed")
                                speak("Approval failed")
        else:
            st.info("📭 No draft material requests available.")
