import streamlit as st
import os
import tempfile
import time
from dotenv import load_dotenv

# Import Custom Modules
from modules.core_services import GeminiService
from modules.utilities import (
    save_uploaded_file,
    extract_audio_if_video,
    chunk_audio_file,
    create_pdf
)
from modules.models import LectureQuiz

load_dotenv()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    layout="wide",
    page_title="Lecture Voice-to-Notes Generator",
    page_icon="🎙️"
)

# ---------------- THEME TOGGLE ----------------
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state.theme = st.radio(
        "Choose Theme",
        ["Light", "Dark"],
        index=0 if st.session_state.theme == "Light" else 1
    )
    st.markdown("---")
    st.info("Supported Formats:\n- MP3\n- MP4\n- WAV\n- M4A\n- MOV")



# ---------------- THEME STYLING ----------------

if st.session_state.theme == "Dark":
    bg_color = "linear-gradient(135deg, #0f172a, #020617)"
    card_bg = "#111827"
    secondary_bg = "#1f2937"
    text_color = "#F9FAFB"
    border_color = "#374151"
else:
    bg_color = "#FFFFFF"
    card_bg = "#FFFFFF"
    secondary_bg = "#F3F4F6"
    text_color = "#111827"
    border_color = "#E5E7EB"

st.markdown(f"""
<style>

/* ---------------- APP BACKGROUND ---------------- */
[data-testid="stAppViewContainer"] {{
    background: {bg_color} !important;
}}

/* ---------------- SIDEBAR ---------------- */
[data-testid="stSidebar"] {{
    background-color: {secondary_bg} !important;
}}

/* ---------------- TEXT ---------------- */
html, body, p, span, label, div {{
    color: {text_color} !important;
}}

/* ---------------- MAIN HEADER ---------------- */
h1 {{
    font-size: 42px !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
}}

p {{
    font-size: 17px !important;
    opacity: 0.85;
}}

/* ---------------- UPLOAD CARD ---------------- */
div[data-testid="stFileUploader"] {{
    background-color: {card_bg} !important;
    border: 1px solid {border_color} !important;
    border-radius: 18px !important;
    padding: 25px !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    transition: 0.3s ease-in-out;
}}

div[data-testid="stFileUploader"]:hover {{
    box-shadow: 0 15px 40px rgba(0,0,0,0.35);
    transform: translateY(-3px);
}}

/* Inner Drop Area */
div[data-testid="stFileUploader"] section {{
    background-color: {secondary_bg} !important;
    border: 2px dashed {border_color} !important;
    border-radius: 14px !important;
    padding: 30px !important;
}}

/* Browse Button */
div[data-testid="stFileUploader"] button {{
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600;
}}

div[data-testid="stFileUploader"] button:hover {{
    opacity: 0.9;
}}

/* ---------------- MAIN BUTTON ---------------- */
.stButton>button {{
    background: linear-gradient(135deg, #6366F1, #8B5CF6);
    color: white;
    border-radius: 14px;
    height: 3em;
    font-weight: 700;
    border: none;
    transition: 0.3s;
}}

.stButton>button:hover {{
    opacity: 0.9;
    transform: translateY(-2px);
}}

/* ---------------- DOWNLOAD BUTTON ---------------- */
.stDownloadButton>button {{
    background: linear-gradient(135deg, #10B981, #059669);
    color: white;
    border-radius: 14px;
    height: 3em;
    font-weight: 700;
    border: none;
}}

.stDownloadButton>button:hover {{
    opacity: 0.9;
}}


/* ---------------- TOP HEADER / TOOLBAR ---------------- */
header {{
    background-color: {secondary_bg} !important;
}}

[data-testid="stHeader"] {{
    background-color: {secondary_bg} !important;
}}

</style>
""", unsafe_allow_html=True)


# ---------------- SESSION STATE ----------------
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'quiz_obj' not in st.session_state:
    st.session_state.quiz_obj = None

if 'gemini_service' not in st.session_state:
    try:
        st.session_state.gemini_service = GeminiService()
    except Exception as e:
        st.error(f"Failed to initialize Gemini Client: {e}")

def clear_session():
    st.session_state.processing_complete = False
    st.session_state.transcript = None
    st.session_state.summary = None
    st.session_state.quiz_obj = None
    st.session_state.gemini_service = GeminiService()

# ---------------- HEADER ----------------
st.markdown(f"""
<div style='text-align:center'>
    <h1>🎓 Lecture Voice-to-Notes Generator</h1>
    <p style='font-size:18px;'>
    Upload your lecture audio/video and instantly generate structured study notes, quizzes, and transcripts.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------------- SYSTEM STATUS ----------------

# ---------------- SYSTEM STATUS ----------------
with st.sidebar:
    st.markdown("---")
    #st.caption("AI/ML Internship Project Demo")


# ---------------- UPLOAD SECTION ----------------
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.subheader("📂 Upload Lecture File")

    uploaded_file = st.file_uploader(
        "Choose your lecture file",
        type=["mp3", "mp4", "wav", "m4a", "mov"],
        on_change=clear_session
    )

    process_button = st.button(
        "🚀 Generate Notes & Quiz",
        disabled=not uploaded_file or not os.getenv("GEMINI_API_KEY")
    )

st.markdown("---")

# ---------------- MAIN PROCESSING ----------------
if process_button and uploaded_file:
    clear_session()

    progress_container = st.empty()
    progress_bar = progress_container.progress(0, text="Initializing processing...")
    progress_text = st.empty()

    input_path = None
    temp_audio_path = os.path.join(tempfile.gettempdir(), f"temp_audio_{time.time()}.mp3")

    try:
        service = st.session_state.gemini_service

        progress_text.text("Step 1/5: Saving and preparing media file...")
        input_path = save_uploaded_file(uploaded_file)
        audio_path = extract_audio_if_video(input_path, temp_audio_path)
        progress_bar.progress(0.1)

        progress_text.text("Step 2/5: Analyzing audio and chunking...")
        chunk_paths = chunk_audio_file(audio_path, progress_text)
        progress_bar.progress(0.5)

        progress_text.text(f"Step 3/5: Transcribing {len(chunk_paths)} chunks...")
        st.session_state.transcript = service.transcribe_full_audio(
            chunk_paths, progress_bar, progress_text
        )

        if st.session_state.transcript == "Transcription failed.":
            raise Exception("Transcription failed.")

        progress_bar.progress(0.8)

        progress_text.text("Step 4/5: Generating study notes...")
        st.session_state.summary = service.generate_summary(
            st.session_state.transcript
        )
        progress_bar.progress(0.9)

        progress_text.text("Step 5/5: Generating structured quiz...")
        st.session_state.quiz_obj = service.generate_quiz(
            st.session_state.transcript
        )
        progress_bar.progress(1.0)

        st.session_state.processing_complete = True

    except Exception as e:
        progress_container.empty()
        st.error(f"Error occurred: {e}")
        if input_path and os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

# ---------------- OUTPUT DISPLAY ----------------
if st.session_state.processing_complete:

    st.success("🎉 Lecture processing completed successfully!")

    if st.session_state.quiz_obj and st.session_state.summary and st.session_state.transcript:
        st.markdown("### 📥 Download Study Guide")

        pdf_bytes = create_pdf(
            st.session_state.transcript,
            st.session_state.summary,
            st.session_state.quiz_obj
        )

        st.download_button(
            label="⬇ Download Complete Study Guide (PDF)",
            data=pdf_bytes,
            file_name="Lecture_Study_Guide.pdf",
            mime="application/pdf"
        )

    st.markdown("---")

    tab_notes, tab_quiz, tab_transcript = st.tabs(
        ["📝 Study Notes", "🧠 Quiz / Flashcards", "📜 Full Transcript"]
    )

    with tab_notes:
        st.subheader("📚 Concise Study Notes")
        st.markdown(st.session_state.summary)

    with tab_quiz:
        st.subheader("🧠 Quiz & Flashcards")

        if st.session_state.quiz_obj:
            quiz_data: LectureQuiz = st.session_state.quiz_obj
            st.markdown(f"### {quiz_data.title}")

            for i, q in enumerate(quiz_data.questions):
                st.markdown(f"#### Q{i+1}. {q.question_text}")

                if q.question_type == "multiple_choice" and q.options:
                    for idx, opt in enumerate(q.options):
                        label = chr(65 + idx)
                        st.markdown(f"**{label}.** {opt.option_text}")

                    with st.expander("Show Answer"):
                        correct_option = next(
                            (opt.option_text for opt in q.options if opt.is_correct),
                            "N/A"
                        )
                        st.success(f"Correct Answer: {correct_option}")
                        st.info(f"Explanation: {q.rationale}")

                elif q.question_type == "flashcard":
                    with st.expander("Show Flashcard Answer"):
                        answer_text = q.options[0].option_text if q.options else "N/A"
                        st.success(f"Answer: {answer_text}")
                        st.info(f"Explanation: {q.rationale}")

                st.markdown("---")

    with tab_transcript:
        st.subheader("📜 Raw Transcript")
        st.text_area(
        "Transcript",
        st.session_state.transcript,
        height=500
        )
