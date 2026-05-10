import pdfplumber
import os
from groq import Groq
from dotenv import load_dotenv
import json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_text_from_pdf(pdf_file):
    """Read text from uploaded PDF resume"""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        return f"Error: {e}"

def generate_questions(resume_text, job_description, num_questions=5):
    """
    Takes resume + job description
    Returns 5 interview questions tailored to this candidate
    """
    prompt = f"""
You are an expert technical interviewer.

Based on this candidate's resume and the job they applied for,
generate exactly {num_questions} interview questions.

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_text}

Rules:
- Mix technical and behavioral questions
- Make questions specific to THIS candidate's background
- Questions should test if they can do THIS job
- Vary difficulty from easy to hard

Return ONLY a JSON array like this — no other text:
[
    {{
        "id": 1,
        "question": "Your question here",
        "type": "Technical",
        "difficulty": "Medium",
        "what_we_test": "What skill this question tests"
    }},
    {{
        "id": 2,
        "question": "Your question here",
        "type": "Behavioral",
        "difficulty": "Easy",
        "what_we_test": "What skill this question tests"
    }}
]
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        result = response.choices[0].message.content.strip()
        result = result.replace("```json", "").replace("```", "").strip()
        questions = json.loads(result)
        return questions, None
    except Exception as e:
        return None, str(e)