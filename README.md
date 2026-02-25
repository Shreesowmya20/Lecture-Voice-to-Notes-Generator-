---

# 🎓 Lecture Voice-to-Notes Generator

> 🚀 AI-powered web application that converts lecture audio/video recordings into structured study notes, quizzes, and downloadable PDF study guides.

<p align="center">
  <b>Developed as part of the IBM SkillsBuild – AICTE Edunet AIML Internship</b>
</p>



---

## 🌐 Live Deployment

🔗 **Try the Application Here:**
👉 [https://jajsjwztac5x2hxmcxffxy.streamlit.app/](https://jajsjwztac5x2hxmcxffxy.streamlit.app/)

---

## 📌 Project Overview

The **Lecture Voice-to-Notes Generator** leverages **Google Gemini 2.5 Flash AI models** to:

* 🎙 Transcribe lecture audio into text
* 📝 Generate concise and structured study notes
* ❓ Create Multiple-Choice Questions (MCQs)
* 🧠 Generate Flashcards
* 📄 Export a complete study guide as a professional PDF

✨ This system reduces manual note-taking effort and enhances learning efficiency using **Artificial Intelligence and Natural Language Processing (NLP).**

---

## 🚀 Key Features

✔ Supports MP3, MP4, WAV, M4A, and MOV file formats
✔ Automatically extracts audio from video files using FFmpeg
✔ Splits long lectures into intelligent 15-minute audio chunks
✔ Performs AI-powered speech-to-text transcription using Gemini API
✔ Generates structured and concise study notes using NLP
✔ Creates multiple-choice questions (MCQs) automatically
✔ Generates interactive flashcards for revision
✔ Exports a professionally formatted downloadable PDF study guide
✔ Includes Light/Dark theme toggle for better user experience
✔ Secures API keys using environment variables (.env)

---

## 🏗 System Architecture

```
User Upload
     ↓
Audio Extraction (FFmpeg)
     ↓
Audio Chunking (Pydub)
     ↓
Gemini API – Transcription
     ↓
Gemini API – Summary Generation
     ↓
Gemini API – Quiz Generation
     ↓
PDF Compilation (FPDF)
     ↓
Download Study Guide
```

---

## 🛠 Technologies Used

### 👨‍💻 Programming Language

* Python

### 🎨 Frontend

* Streamlit

### 🤖 AI / ML

* Google Gemini 2.5 Flash (Speech-to-Text + NLP)

### 📚 Libraries

* Pydub – Audio Processing
* FFmpeg – Media Conversion
* Pydantic – Structured Data Validation
* FPDF – PDF Generation
* python-dotenv – Environment Variable Management

---

## 📂 Project Structure

```
.
├── app.py
├── modules/
│   ├── core_services.py
│   ├── utilities.py
│   ├── models.py
├── .env
├── .gitignore
├── requirements.txt
├── runtime.txt
└── README.md
```

---

## ⚙️ Installation & Setup

Follow these steps to clone and run the application locally.

### 🔹 Prerequisites

* Python 3.11+ installed
* FFmpeg installed and added to system PATH

---

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/lecture-voice-to-notes-generator.git
cd lecture-voice-to-notes-generator
```

---

### 2️⃣ Create & Activate Virtual Environment

```bash
python -m venv venv
```

**Linux / macOS**

```bash
source venv/bin/activate
```

**Windows**

```bash
.\venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configure Gemini API Key

1. Obtain your API key from **Google AI Studio**
2. Create a `.env` file and a '.gitignore' file in the root directory
3. Add your key inside `.env`:

```env
GEMINI_API_KEY="AIzaSy.............."
```

⚠️ Ensure `.env` is included in `.gitignore` to protect your API key.

---

### 5️⃣ Run the Application

```bash
streamlit run app.py
```

🌐 The application will automatically open in your browser and is ready to process lecture files.

---
