# agent.py

import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set Groq API key and base URL
openai.api_key = os.getenv("GROQ_API_KEY")
openai.api_base = "https://api.groq.com/openai/v1"

def extract_command(text):
    word_to_num = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
        "ten": 10
    }

    text = text.lower()
    qty = None
    item = None

    # Command pattern: "create material request for 5 chairs"
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

    # Otherwise, handle as a chatbot query
    chatbot_reply = ask_chatbot(text)
    return {
        "intent": "CHAT",
        "response": chatbot_reply
    }

def ask_chatbot(user_message):
    try:
        response = openai.ChatCompletion.create(
            model="llama3-70b-8192",  # Supported model on Groq
            messages=[
                {"role": "system", "content": "You are a helpful assistant for ERP system users."},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Chatbot error: {e}"
