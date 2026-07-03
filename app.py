import streamlit as st
from google import genai
import pdfplumber
import tempfile
import os

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def analyze_lecture_notes(text):
    prompt = f"""
You are an expert academic assistant and subject matter expert. First, identify the subject domain of the provided lecture notes (e.g., Mathematics, Physics, Chemistry, Computer Science, Biology, History, Economics, Engineering, etc.).

Then based on the identified subject, analyze the notes and provide:

1. SUBJECT DETECTED — State the subject/topic identified.

2. SUMMARY — A clear, concise summary in 5-8 sentences capturing the core concepts.

3. KEY POINTS — 10 bullet points of the most critical concepts, formulas, theorems, or facts a student must know.

4. POSSIBLE EXAM QUESTIONS — Generate 6 exam questions strictly following these rules:
   - MATHEMATICS: Generate ONLY numerical problems with specific given values that require calculation and working. No theory questions.
   - PHYSICS / CHEMISTRY / ENGINEERING: Mix of BOTH numerical problems (with specific given values requiring calculation) AND theoretical questions (concept explanation, derive, state and prove). Ratio: 60% numerical, 40% theory.
   - COMPUTER SCIENCE / PROGRAMMING: Mix of code-writing questions, algorithm problems, and short conceptual questions. Include at least 2 questions that require writing actual code or pseudocode.
   - BIOLOGY / MEDICINE: Mix of diagram-based questions, process explanation questions, and application-based clinical/real-world questions.
   - HISTORY / ECONOMICS / SOCIAL SCIENCE: Mix of analytical essay questions, cause-effect questions, and data/case-based interpretation questions.
   - MIXED CONTENT: Proportionally mix numerical and theoretical questions based on content ratio.

5. QUICK REVISION TIPS — 3 specific memory tricks, mnemonics, or study strategies tailored to this subject content.

Lecture Notes:
{text}

Format each section clearly with its heading. Be specific, precise, and academically rigorous.
IMPORTANT: Detect the language of the lecture notes and respond entirely in that same language.
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

st.set_page_config(page_title="AI Lecture Notes Summarizer", page_icon="📚")
st.title("📚 AI Lecture Notes Summarizer")
st.markdown("Upload your lecture notes PDF or paste text below to get a summary, key points, and exam questions.")

option = st.radio("Choose input method:", ["Upload PDF", "Paste Text"])

text = ""

if option == "Upload PDF":
    uploaded_file = st.file_uploader("Upload your lecture notes (PDF)", type="pdf")
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        text = extract_text_from_pdf(tmp_path)
        os.unlink(tmp_path)
        if text.strip():
            st.success("PDF uploaded and text extracted ✅")
        else:
            st.error("⚠️ The uploaded PDF appears to be empty or contains no readable text. Please upload a valid PDF.")
else:
    text = st.text_area("Paste your lecture notes here:", height=300)

if st.button("🔍 Analyze Notes"):
    if not text.strip():
        st.warning("⚠️ Please upload a valid PDF or paste some text before analyzing.")
    else:
        with st.spinner("Analyzing your notes..."):
            result = analyze_lecture_notes(text)
        st.markdown("---")
        st.markdown(result)
