import os
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from modules.models import LectureQuiz

load_dotenv()


# Use Gemini 2.5 Flash (fast + supports multimodal)
GEMINI_MODEL_STT = "gemini-2.5-flash"
GEMINI_MODEL_NLP = "gemini-2.5-flash"

def __init__(self):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error("GEMINI_API_KEY not found in environment variables.")
        st.stop()

    self.client = genai.Client(api_key=api_key)
    st.session_state.gemini_key_ok = True

class GeminiService:
    """Manages all interactions with the Google Gemini API."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            st.error("GEMINI_API_KEY not found in environment variables.")
            st.stop()

        self.client = genai.Client(api_key=api_key)
        st.session_state.gemini_key_ok = True


    def _safe_gemini_call(self, func, *args, **kwargs):
        max_retries = 3
        delay = 1

        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt < max_retries - 1:
                    st.warning(
                        f"Gemini API transient error "
                        f"(Attempt {attempt + 1}/{max_retries}). "
                        f"Retrying in {delay}s: {e}"
                    )
                    time.sleep(delay)
                    delay *= 2
                else:
                    st.error(f"Gemini API failed after {max_retries} attempts: {e}")
                    raise


    def _transcribe_chunk(self, chunk_path, uploaded_files_ref):

        file_obj = self._safe_gemini_call(
            self.client.files.upload,
            file=chunk_path
        )

        uploaded_files_ref.append(file_obj)

        try:
            response = self._safe_gemini_call(
                self.client.models.generate_content,
                model=GEMINI_MODEL_STT,
                contents=[file_obj]
            )

            return response.text

        finally:
            self.client.files.delete(name=file_obj.name)

            if os.path.exists(chunk_path):
                os.remove(chunk_path)


    def transcribe_full_audio(self, chunk_paths, progress_bar, progress_text):
        full_transcript = ""
        total_chunks = len(chunk_paths)
        uploaded_files_ref = []

        for i, chunk_path in enumerate(chunk_paths):
            progress_value = 0.5 + (i * 0.5) / total_chunks
            progress_text.text(f"Transcribing chunk {i + 1} of {total_chunks}...")

            chunk_transcript = self._transcribe_chunk(chunk_path, uploaded_files_ref)
            full_transcript += chunk_transcript.strip() + " "

            progress_bar.progress(progress_value)

        return full_transcript.strip()


    def generate_summary(self, transcript):

        summary_prompt = f"""
        You are an expert academic summarizer.
        Summarize the lecture into concise study notes.

        LECTURE TRANSCRIPT:
        {transcript}
        """

        response = self._safe_gemini_call(
            self.client.models.generate_content,
            model=GEMINI_MODEL_NLP,
            contents=[summary_prompt],
            config={"temperature": 0.3},
        )

        return response.text


    def generate_quiz(self, transcript):

        quiz_prompt = f"""
        Based only on this transcript,
        generate 5 MCQs and 5 flashcards.

        LECTURE TRANSCRIPT:
        {transcript}
        """

        response = self._safe_gemini_call(
            self.client.models.generate_content,
            model=GEMINI_MODEL_NLP,
            contents=[quiz_prompt],
            config={
                "temperature": 0.5,
                "response_mime_type": "application/json",
                "response_schema": LectureQuiz,
            },
        )

        return response.parsed
