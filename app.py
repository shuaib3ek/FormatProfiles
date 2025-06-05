import os
import docx
import pdfplumber
import streamlit as st
import openai
from jinja2 import Template
from weasyprint import HTML
from zipfile import ZipFile
import json

TEMPLATE_FILE = "template_stats_structured_grouped_final.html"
OUTPUT_DIR = "downloads"
os.makedirs(OUTPUT_DIR, exist_ok=True)

st.set_page_config(page_title="Trainer Profile Formatter", layout="centered")
st.title("📄 AI-Powered Trainer Profile Formatter")

openai_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")

uploaded_files = st.file_uploader(
    "Upload DOCX or PDF profiles",
    type=["docx", "pdf"],
    accept_multiple_files=True
)

def extract_text(file, extension):
    if extension == "docx":
        doc = docx.Document(file)
        return "\n".join(para.text for para in doc.paragraphs)
    elif extension == "pdf":
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    return ""

def extract_profile_data(text, key):
    openai.api_key = key

    prompt = f"""You are an expert AI assistant that extracts technical training profile data.

Given the raw resume text, return a JSON object with the following fields:
- Full_Name
- Professional_Summary
- Work_Experience (list of descriptions)
- Training_Experience (list of training-specific activities)
- Skill_Set (grouped into categories like Programming Languages, Tools, Platforms, Cloud, Data, etc.)
- Certifications (list)
- Clients (list)

Your goal is to deeply analyze the text and extract meaningful, grouped skillsets from any section mentioning tools, platforms, technologies, or methods.

Respond ONLY with JSON. No comments or markdown. Group Skill_Set into categories as a dictionary of lists.

Here is the text:
{text}
"""

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You extract structured data from resumes and return JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```json"):
        content = content.split("```json")[-1].strip()
    elif content.startswith("```"):
        content = content.split("```")[-1].strip()

    
    import re
    try:
        json_str = re.search(r"{.*}", content, re.DOTALL).group()
        return json.loads(json_str)
    except Exception as e:
        print("\n⚠️ RAW OpenAI Response:\n", content)
        raise ValueError(f"❌ Failed to parse JSON: {e}")
    

def generate_pdf(profile_data, output_path):
    with open(TEMPLATE_FILE) as f:
        template = Template(f.read())
    html = template.render(**profile_data)
    HTML(string=html, base_url=".").write_pdf(output_path)

if uploaded_files and openai_key:
    zip_path = os.path.join(OUTPUT_DIR, "Formatted_Profiles.zip")
    with ZipFile(zip_path, 'w') as zipf:
        for file in uploaded_files:
            ext = file.name.split(".")[-1].lower()
            raw_text = extract_text(file, ext)

            if not raw_text.strip():
                st.warning(f"⚠️ Skipping empty file: {file.name}")
                continue

            try:
                with st.spinner(f"Processing: {file.name}"):
                    data = extract_profile_data(raw_text, openai_key)
                    filename = data.get("Full_Name", "Trainer_Profile").replace(" ", "_") + ".pdf"
                    out_path = os.path.join(OUTPUT_DIR, filename)
                    generate_pdf(data, out_path)
                    zipf.write(out_path, arcname=filename)
                    st.success(f"✅ {file.name} formatted.")
            except Exception as e:
                st.error(f"❌ Error with {file.name}: {e}")

    with open(zip_path, "rb") as f:
        st.download_button("📥 Download All PDFs", f, file_name="Formatted_Profiles.zip", mime="application/zip")
elif uploaded_files:
    st.warning("🔐 Please enter your OpenAI API key.")