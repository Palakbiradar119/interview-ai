import json
import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def evaluate_answer(question_data, answer, job_description):
    question = question_data["question"]
    q_type = question_data.get("type", "General")

    if not answer.strip():
        return {
            "score": 0,
            "rating": "No Answer",
            "technical_score": 0,
            "communication_score": 0,
            "confidence_score": 0,
            "problem_solving_score": 0,
            "what_was_good": "No answer was provided",
            "what_was_missing": "A complete answer was expected",
            "feedback": "No answer was submitted for this question.",
            "ideal_answer_points": [],
            "detected_skills": []
        }

    prompt = f"""You are an expert AI interviewer. Evaluate the candidate answer carefully.

Question: {question}
Question Type: {q_type}
Job Description: {job_description}
Candidate Answer: {answer}

Return ONLY valid JSON with no extra text. Use this exact format:

{{
    "score": 7,
    "rating": "Good",
    "technical_score": 7,
    "communication_score": 8,
    "confidence_score": 7,
    "problem_solving_score": 6,
    "what_was_good": "Write what was good about the answer here",
    "what_was_missing": "Write what was missing here",
    "feedback": "Write 2-3 sentences of overall feedback here",
    "ideal_answer_points": [
        "First key point",
        "Second key point",
        "Third key point"
    ],
    "detected_skills": [
        "Skill 1",
        "Skill 2"
    ]
}}

Score must be a whole number from 0 to 10. Return ONLY the JSON object."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )

        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()

        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group()

        result = json.loads(content)
        result["score"] = float(result.get("score", 0))
        return result

    except json.JSONDecodeError:
        return {
            "score": 5,
            "rating": "Average",
            "technical_score": 5,
            "communication_score": 5,
            "confidence_score": 5,
            "problem_solving_score": 5,
            "what_was_good": "Answer was provided",
            "what_was_missing": "Could not fully evaluate",
            "feedback": "Your answer was received but could not be fully parsed.",
            "ideal_answer_points": [],
            "detected_skills": []
        }

    except Exception as e:
        return {
            "score": 0,
            "rating": "Error",
            "technical_score": 0,
            "communication_score": 0,
            "confidence_score": 0,
            "problem_solving_score": 0,
            "what_was_good": "",
            "what_was_missing": "",
            "feedback": f"Evaluation error: {str(e)}",
            "ideal_answer_points": [],
            "detected_skills": []
        }


def evaluate_all_answers(questions, answers, job_description):
    evaluations = []
    total_score = 0
    questions_answered = 0
    all_skills = set()

    for q in questions:
        qid = str(q["id"])
        ans = answers.get(qid, "")

        if ans.strip():
            questions_answered += 1

        evaluation = evaluate_answer(q, ans, job_description)
        score = float(evaluation.get("score", 0))
        total_score += score

        for skill in evaluation.get("detected_skills", []):
            all_skills.add(skill)

        evaluations.append({
            "question_id": q["id"],
            "question": q["question"],
            "type": q.get("type", "General"),
            "difficulty": q.get("difficulty", "Medium"),
            "answer": ans,
            "evaluation": evaluation
        })

    avg_score = round(total_score / len(questions), 1) if questions else 0
    percentage = round((total_score / (len(questions) * 10)) * 100, 1) if questions else 0

    if percentage >= 80:
        overall_rating = "Excellent Candidate"
        recommendation = "Strongly Recommended"
        color = "green"
    elif percentage >= 60:
        overall_rating = "Good Candidate"
        recommendation = "Recommended"
        color = "blue"
    elif percentage >= 40:
        overall_rating = "Average Candidate"
        recommendation = "Needs Improvement"
        color = "orange"
    else:
        overall_rating = "Weak Candidate"
        recommendation = "Not Recommended"
        color = "red"

    final_summary = f"""Candidate answered {questions_answered} out of {len(questions)} questions.
Average score: {avg_score}/10 ({percentage}%).
Overall Recommendation: {recommendation}"""

    return {
        "evaluations": evaluations,
        "total_score": round(total_score, 1),
        "avg_score": avg_score,
        "percentage": percentage,
        "questions_answered": questions_answered,
        "overall_rating": overall_rating,
        "recommendation": recommendation,
        "color": color,
        "final_summary": final_summary,
        "detected_skills": list(all_skills)
    }