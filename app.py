import streamlit as st
import time

from google import genai
from google.genai import types
from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE


# =========================================================
# Gemini Model
# =========================================================

MODEL_NAME = "gemini-3.5-flash"


# =========================================================
# Page Settings
# =========================================================

st.set_page_config(
    page_title="abinesh chat",
    page_icon="👍",
    layout="centered",
)


# =========================================================
# Gemini API Key
# =========================================================

import os

GEMINI_API_KEY = (
    st.secrets.get("GEMINI_API_KEY")
    or os.getenv("GEMINI_API_KEY")
)

@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()


# =========================================================
# Display Messages
# =========================================================

def render_message(message):

    with st.chat_message(message["role"]):

        if message["kind"] == "text":

            if message["role"] == "assistant":

                st.write(message["content"])

                st.code(
                    message["content"],
                    language=None
                )

            else:
                st.write(message["content"])

        elif message["kind"] == "image":
            st.image(message["content"])


# =========================================================
# Add Message
# =========================================================

def add_message(role, kind, content):

    st.session_state.messages.append(
        {
            "role": role,
            "kind": kind,
            "content": content,
        }
    )

    render_message(
        st.session_state.messages[-1]
    )


# =========================================================
# Ask Gemini
# =========================================================

def ask_gemini(parts):

    for attempt in range(3):

        try:

            response = st.session_state.chat.send_message(parts)

            return response.text

        except Exception as error:

            error_text = str(error)

            if "503" in error_text or "UNAVAILABLE" in error_text:

                if attempt < 2:
                    time.sleep(5)
                    continue

                return (
                    "Gemini server busy-ah irukku. "
                    "Konjam neram kalichu try pannunga."
                )

            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:

                return (
                    "Gemini quota mudinjiduchu 😕\n\n"
                    "Free tier-la current request limit reached. "
                    "Quota reset aana piragu try pannunga."
                )

            return f"ERROR: {error}"


# =========================================================
# Welcome / User Setup
# =========================================================

if "onboarded" not in st.session_state:

    st.title("")

    st.caption(
        "Ask anything — education, technology, "
        "general questions, food and more."
    )

    with st.form("onboarding_form"):

        name = st.text_input(
            "Your name"
        )

        submitted = st.form_submit_button(
            "Let's go 🚀"
        )

    if submitted:

        if not name.strip():

            st.warning(
                "Please enter your name."
            )

        else:

            st.session_state.name = name.strip()

            st.session_state.chat = (
                gemini_client.chats.create(
                    model=MODEL_NAME,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT
                    ),
                )
            )

            st.session_state.messages = []

            st.session_state.onboarded = True

            st.rerun()

    st.stop()


# =========================================================
# Chat Interface
# =========================================================

st.title("MY CHAT👍")


# =========================================================
# Show Previous Messages
# =========================================================

if not st.session_state.messages:

    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(
            name=st.session_state.name
        ),
    )

else:

    for message in st.session_state.messages:

        render_message(message)


# =========================================================
# Chat Input + Image Upload
# =========================================================

user_input = st.chat_input(
    "Ask anything or attach a photo",
    accept_file=True,
    file_type=[
        "jpg",
        "jpeg",
        "png",
    ],
)


# =========================================================
# Process User Input
# =========================================================

if user_input:

    photo = (
        user_input.files[0]
        if user_input.files
        else None
    )

    text = user_input.text

    parts = []


    # =====================================================
    # Photo
    # =====================================================

    if photo is not None:

        photo_bytes = photo.getvalue()

        add_message(
            "user",
            "image",
            photo_bytes,
        )

        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type,
            )
        )


    # =====================================================
    # Text
    # =====================================================

    if text:

        add_message(
            "user",
            "text",
            text,
        )

        parts.append(text)


    # =====================================================
    # Photo Only
    # =====================================================

    elif photo is not None:

        parts.append(
            """
            Analyze this image carefully.

            If it is food:
            - Identify the food.
            - Estimate calories.
            - Estimate protein.
            - Estimate carbohydrates.
            - Estimate fat.

            If it is not food:
            - Describe what is visible in the image.
            - Answer questions about the image.
            """
        )


    # =====================================================
    # Get Gemini Response
    # =====================================================

    if parts:

        with st.spinner(
            "Thinking... 🤔"
        ):

            answer = ask_gemini(parts)

        add_message(
            "assistant",
            "text",
            answer,
        )