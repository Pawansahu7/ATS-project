import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("AIzaSyA2VaLo4Q1hNt7u7TWmqMiOx8l3es8iKBg"))

# Function to generate Gemini response
def get_gemini_response(prompt):
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    return response.text

# Function to extract text from PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# Prompt template
input_prompt = """
Hey Act Like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of the tech field: software engineering, data science, data analyst,
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving the resume. Assign the percentage match based 
on JD and highlight the missing keywords with high accuracy.

resume: {text}

description: {jd}

I want the response in one single string having the structure:
{{"JD Match":"%", "MissingKeywords":[], "Profile Summary":""}}
"""

# Streamlit UI
st.title("🧠 Smart ATS Evaluator")
st.write("Upload your resume and paste a job description to get instant feedback.")

jd = st.text_area("📄 Paste the Job Description")
uploaded_file = st.file_uploader("📁 Upload Your Resume (PDF)", type="pdf")

submit = st.button("🚀 Submit")

if submit:
    if uploaded_file is not None and jd.strip() != "":
        with st.spinner("Analyzing..."):
            text = input_pdf_text(uploaded_file)
            final_prompt = input_prompt.format(text=text, jd=jd)
            response = get_gemini_response(final_prompt)

        st.subheader("📊 Evaluation Result")

        # Try to parse the response as JSON
        try:
            # Attempt to locate and clean JSON content from model output
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            json_str = response[json_start:json_end]

            data = json.loads(json_str)

            st.markdown(f"### ✅ JD Match: `{data.get('JD Match', 'N/A')}`")

            st.markdown("### ❗ Missing Keywords")
            if data.get("MissingKeywords"):
                for keyword in data["MissingKeywords"]:
                    st.markdown(f"- {keyword}")
            else:
                st.markdown("*No significant keywords missing!* 🎯")

            st.markdown("### 🧾 Profile Summary")
            st.markdown(f"{data.get('Profile Summary', 'No summary provided.')}")
        
        except Exception as e:
            st.error("⚠️ Could not parse the model response. Showing raw output instead.")
            st.write(response)
    else:
        st.error("Please upload a resume and provide a job description.")
