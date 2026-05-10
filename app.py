import streamlit as st
from fpdf import FPDF

from question_generator import (
    extract_text_from_pdf,
    generate_questions
)

from answer_evaluator import evaluate_all_answers


# ─────────────────────────
# PAGE CONFIG
# ─────────────────────────
st.set_page_config(
    page_title="Interview AI",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Interview AI")
st.markdown(
    "**AI powered mock interview — get evaluated like a real interview!**"
)

# ─────────────────────────
# SESSION STATE
# ─────────────────────────
if "stage" not in st.session_state:
    st.session_state.stage = "setup"

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "job_description" not in st.session_state:
    st.session_state.job_description = ""

if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "report" not in st.session_state:
    st.session_state.report = None


# ─────────────────────────
# PROGRESS STEPS
# ─────────────────────────
stages = ["Setup", "Interview", "Results"]

stage_idx = {
    "setup": 0,
    "interview": 1,
    "results": 2
}

current_idx = stage_idx.get(st.session_state.stage, 0)

cols = st.columns(3)

for i, stage_name in enumerate(stages):

    with cols[i]:

        if i < current_idx:
            st.success(f"✅ {stage_name}")

        elif i == current_idx:
            st.info(f"▶ {stage_name}")

        else:
            st.write(f"⬜ {stage_name}")

st.divider()


# ─────────────────────────────────────────
# SETUP PAGE
# ─────────────────────────────────────────
if st.session_state.stage == "setup":

    st.header("📋 Step 1 — Setup Your Interview")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Upload Resume")

        resume_file = st.file_uploader(
            "Upload Resume PDF",
            type=["pdf"]
        )

        if resume_file:
            st.success(f"✅ {resume_file.name} uploaded")

    with col2:

        st.subheader("Paste Job Description")

        job_description = st.text_area(
            "Paste the job description:",
            height=220,
            placeholder="Paste the job description here..."
        )

    num_questions = st.slider(
        "Number of Interview Questions",
        min_value=3,
        max_value=8,
        value=5
    )

    st.divider()

    if st.button(
        "🚀 Start Interview",
        type="primary",
        use_container_width=True
    ):

        if not resume_file:
            st.error("Please upload a resume PDF.")

        elif not job_description.strip():
            st.error("Please paste the job description.")

        else:

            with st.spinner(
                "Reading resume and generating interview questions..."
            ):

                resume_text = extract_text_from_pdf(resume_file)

                if resume_text.startswith("Error"):
                    st.error(resume_text)

                else:

                    questions, error = generate_questions(
                        resume_text,
                        job_description,
                        num_questions
                    )

                    if error:
                        st.error(error)

                    else:

                        st.session_state.resume_text = resume_text
                        st.session_state.job_description = job_description
                        st.session_state.questions = questions
                        st.session_state.answers = {}
                        st.session_state.current_question = 0
                        st.session_state.stage = "interview"

                        st.rerun()


# ─────────────────────────────────────────
# INTERVIEW PAGE
# ─────────────────────────────────────────
elif st.session_state.stage == "interview":

    questions = st.session_state.questions

    current_q_idx = st.session_state.current_question

    total_questions = len(questions)

    q = questions[current_q_idx]

    st.header(
        f"💬 Interview — Question {current_q_idx + 1} of {total_questions}"
    )

    progress = current_q_idx / total_questions

    st.progress(progress)

    st.caption(
        f"{current_q_idx} of {total_questions} questions answered"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Type", q.get("type", "General"))

    with col2:
        st.metric("Difficulty", q.get("difficulty", "Medium"))

    with col3:
        st.metric(
            "Question",
            f"{current_q_idx + 1}/{total_questions}"
        )

    st.markdown(
        f"""
        <div style='background:#EFF6FF;
                    border-left:4px solid #2563EB;
                    padding:20px;
                    border-radius:10px;
                    margin-top:20px;
                    margin-bottom:20px;'>

            <p style='font-size:18px;
                      font-weight:bold;
                      color:#1E3A5F;'>

                ❓ {q["question"]}

            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    if q.get("what_we_test"):
        st.caption(
            f"💡 What we are testing: {q['what_we_test']}"
        )

    existing_answer = st.session_state.answers.get(
        str(q["id"]),
        ""
    )

    # FIXED ANSWER BOX
    answer = st.text_area(
        "Your Answer",
        value=existing_answer,
        height=220,
        placeholder="Write your answer here...",
        key=f"answer_box_{current_q_idx}"
    )

    col_prev, col_skip, col_next = st.columns(3)

    # PREVIOUS
    with col_prev:

        if current_q_idx > 0:

            if st.button(
                "← Previous",
                use_container_width=True
            ):

                st.session_state.answers[str(q["id"])] = answer

                st.session_state.current_question -= 1

                st.rerun()

    # SKIP
    with col_skip:

        if st.button(
            "Skip →",
            use_container_width=True
        ):

            st.session_state.answers[str(q["id"])] = ""

            st.session_state.current_question += 1

            if (
                st.session_state.current_question
                >= total_questions
            ):
                st.session_state.stage = "evaluating"

            st.rerun()

    # NEXT
    with col_next:

        if current_q_idx < total_questions - 1:
            button_label = "Next Question →"

        else:
            button_label = "✅ Submit Interview"

        if st.button(
            button_label,
            type="primary",
            use_container_width=True
        ):

            st.session_state.answers[str(q["id"])] = answer

            if current_q_idx < total_questions - 1:

                st.session_state.current_question += 1

                st.rerun()

            else:

                st.session_state.stage = "evaluating"

                st.rerun()

    # SIDEBAR
    with st.sidebar:

        st.header("📋 Interview Progress")

        for i, qq in enumerate(questions):

            ans = st.session_state.answers.get(
                str(qq["id"]),
                ""
            )

            if i == current_q_idx:
                st.info(f"Q{i+1} — Current")

            elif ans.strip():
                st.success(f"Q{i+1} — Answered")

            else:
                st.write(f"Q{i+1} — Not Answered")


# ─────────────────────────────────────────
# EVALUATION PAGE
# ─────────────────────────────────────────
elif st.session_state.stage == "evaluating":

    st.header("⏳ Evaluating Your Interview")

    st.markdown(
        "AI is evaluating your answers and generating feedback..."
    )

    progress_bar = st.progress(0)

    progress_bar.progress(30)

    report = evaluate_all_answers(
        st.session_state.questions,
        st.session_state.answers,
        st.session_state.job_description
    )

    progress_bar.progress(100)

    st.session_state.report = report

    st.session_state.stage = "results"

    st.rerun()


# ─────────────────────────────────────────
# RESULTS PAGE
# ─────────────────────────────────────────
elif st.session_state.stage == "results":

    report = st.session_state.report

    st.header("📊 Interview Report")

    percentage = report["percentage"]

    overall_rating = report["overall_rating"]

    recommendation = report["recommendation"]

    if percentage >= 80:
        icon = "🟢"

    elif percentage >= 60:
        icon = "🟡"

    elif percentage >= 40:
        icon = "🟠"

    else:
        icon = "🔴"

    st.markdown(
        f"""
        <div style='background:#F0FDF4;
                    border:2px solid #16A34A;
                    padding:25px;
                    border-radius:12px;
                    text-align:center;'>

            <h1>{icon} {percentage}%</h1>

            <h2>{overall_rating}</h2>

            <p>
                Recommendation:
                <b>{recommendation}</b>
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # OVERALL METRICS
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric(
            "Overall Score",
            f"{report['avg_score']}/10"
        )

    with m2:
        st.metric(
            "Total Points",
            f"{report['total_score']}/"
            f"{len(report['evaluations']) * 10}"
        )

    with m3:
        st.metric(
            "Questions Answered",
            f"{report['questions_answered']}/"
            f"{len(report['evaluations'])}"
        )

    with m4:
        st.metric(
            "Percentage",
            f"{percentage}%"
        )

    st.divider()

    # FINAL SUMMARY
    st.subheader("🧠 Final AI Summary")

    st.info(report.get("final_summary", ""))

    st.divider()

    # DETECTED SKILLS
    st.subheader("🛠️ Detected Skills")

    skills = report.get("detected_skills", [])

    if skills:

        for skill in skills:
            st.success(f"✅ {skill}")

    else:
        st.warning("No skills detected.")

    st.divider()

    # QUESTION BREAKDOWN
    st.subheader("📝 Question by Question Breakdown")

    for item in report["evaluations"]:

        evaluation = item["evaluation"]

        score = evaluation.get("score", 0)

        with st.expander(
            f"Q{item['question_id']} — "
            f"Score: {score}/10"
        ):

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Technical Knowledge",
                    f"{evaluation.get('technical_score', 0)}/10"
                )

                st.metric(
                    "Communication",
                    f"{evaluation.get('communication_score', 0)}/10"
                )

            with col2:

                st.metric(
                    "Confidence",
                    f"{evaluation.get('confidence_score', 0)}/10"
                )

                st.metric(
                    "Problem Solving",
                    f"{evaluation.get('problem_solving_score', 0)}/10"
                )

            st.markdown("### ❓ Question")
            st.info(item["question"])

            st.markdown("### ✍️ Your Answer")
            st.write(item["answer"])

            st.markdown("### ✅ What Was Good")
            st.success(
                evaluation.get("what_was_good", "")
            )

            st.markdown("### ❌ What Was Missing")
            st.error(
                evaluation.get("what_was_missing", "")
            )

            st.markdown("### 💡 Ideal Answer Points")

            ideal_points = evaluation.get(
                "ideal_answer_points",
                []
            )

            for point in ideal_points:
                st.markdown(f"- {point}")

            st.markdown("### 📝 AI Feedback")

            st.write(
                evaluation.get("feedback", "")
            )

    st.divider()

    # PDF REPORT
    report_text = f"""
INTERVIEW AI REPORT

Overall Score: {report['avg_score']}/10

Percentage: {report['percentage']}%

Recommendation: {report['recommendation']}

Final Summary:
{report['final_summary']}
"""

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, report_text)

    pdf.output("interview_report.pdf")

    with open(
        "interview_report.pdf",
        "rb"
    ) as pdf_file:

        st.download_button(
            "⬇️ Download PDF Report",
            pdf_file,
            file_name="Interview_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # RESET
    if st.button(
        "🔄 Start New Interview",
        use_container_width=True
    ):

        for key in [
            "stage",
            "questions",
            "answers",
            "resume_text",
            "job_description",
            "current_question",
            "report"
        ]:

            if key in st.session_state:
                del st.session_state[key]

        st.rerun()