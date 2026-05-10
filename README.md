Interview AI – AI Powered Mock Interview System

An intelligent AI-powered mock interview platform that generates interview questions from resumes and job descriptions, evaluates user answers using LLMs, and provides detailed performance feedback with scoring, skill analysis, and improvement suggestions.

🚀 Live Demo

(Add this after deployment)
👉 https://your-streamlit-app-link.streamlit.app

📌 Features
📄 Resume PDF upload & parsing
🧠 AI-generated interview questions (based on Resume + Job Description)
💬 Interactive interview interface (like real interview flow)
🤖 LLM-based answer evaluation (technical + communication scoring)
📊 Detailed performance report with:
Overall score
Percentage rating
Question-wise analysis
🛠️ Skill detection from answers
📥 Downloadable PDF interview report
🔄 Multi-stage interview system (Setup → Interview → Results)
🧠 System Architecture
Resume Parser → Extracts text from uploaded PDF
Question Generator (LLM) → Creates interview questions
Interview Engine (Streamlit UI) → Collects user answers
Answer Evaluator (LLM + Prompt Engineering) → Scores responses
Report Generator → Generates final performance report
⚙️ Tech Stack
Frontend: Streamlit
Backend Logic: Python
LLM: Groq (LLaMA 3) / LangChain
PDF Processing: PyPDF / FPDF
AI Pipeline: Prompt Engineering + RAG concepts
Deployment: Streamlit Cloud (or AWS-ready)
📂 Project Structure
interview-ai/
│
├── app.py                  # Main Streamlit application
├── question_generator.py  # Generates interview questions
├── answer_evaluator.py     # Evaluates answers using LLM
├── requirements.txt        # Dependencies
├── .gitignore              # Ignored files
└── README.md               # Project documentation
🧪 How It Works
Upload your resume (PDF)
Paste job description
AI generates interview questions
You answer questions one by one
LLM evaluates each answer
Final report is generated with:
Score (0–100)
Skill analysis
Strengths & weaknesses
📊 Sample Output
Overall Score: 82%
Rating: Excellent Candidate
Recommendation: Strongly Recommended
Skills Detected:
Machine Learning
NLP
Data Preprocessing
API Integration
🔥 Key Highlights
Uses LLM-based evaluation instead of static rules
Real-world HR-style interview simulation
Structured JSON-based scoring system
Modular and scalable architecture
Production-style AI workflow
🚀 Future Improvements
Voice-based interview mode 🎤
Multi-agent AI interviewer 🤖
Real-time feedback system
ATS resume scoring integration
Cloud database storage
👨‍💻 Author

Palak Biradar
AI/ML & Generative AI Developer

📜 License

This project is for educational and portfolio purposes.

🎯 FINAL RESULT

This README makes your project:

✔ Recruiter-ready
✔ Internship-ready
✔ Capgemini/Infosys interview-ready
✔ Portfolio-level strong
