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
You are an expert academic assistant. Analyze the following lecture notes and provide:

1. SUMMARY — A clean, concise summary in 5-8 sentences
2. KEY POINTS — 8 to 10 bullet points of the most important concepts
3. POSSIBLE EXAM QUESTIONS — 5 likely exam questions based on the content

Lecture Notes:
{text}

Format your response clearly with the three sections labeled.
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
        st.success("PDF uploaded and text extracted ✅")
else:
    text = st.text_area("Paste your lecture notes here:", height=300)

if st.button("🔍 Analyze Notes") and text:
    with st.spinner("Analyzing your notes..."):
        result = analyze_lecture_notes(text)
    st.markdown("---")
    st.markdown(result)
elif st.button and not text:
    st.warning("Please upload a PDF or paste some text first.")
