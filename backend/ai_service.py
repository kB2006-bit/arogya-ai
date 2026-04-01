import json
import re
from typing import Any, Dict, List


HIGH_SEVERITY_KEYWORDS = ["chest pain", "breathing", "unconscious"]


def _extract_json(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError("No JSON object returned by model")

    return json.loads(match.group(0))


def _normalize_assessment(raw: Dict[str, Any], message: str) -> Dict[str, Any]:
    severity = str(raw.get("severity", "Medium")).strip().title()
    if severity not in {"Low", "Medium", "High"}:
        severity = "Medium"

    diagnosis = str(raw.get("diagnosis", raw.get("likely_condition", "General symptom review"))).strip()
    summary = str(raw.get("summary", diagnosis or "General symptom review")).strip()
    next_steps = [str(step).strip() for step in raw.get("next_steps", []) if str(step).strip()][:3]
    warning_signs = [str(sign).strip() for sign in raw.get("warning_signs", []) if str(sign).strip()][:3]
    emergency_message = str(raw.get("emergency_message", "Seek urgent care if symptoms worsen.")).strip()

    if not next_steps:
        next_steps = [
            "Rest and monitor how your symptoms change.",
            "Stay hydrated and avoid self-medicating heavily.",
            "Consult a licensed clinician for a confirmed diagnosis.",
        ]

    if not warning_signs:
        warning_signs = [
            "Severe worsening of symptoms",
            "Breathing difficulty or confusion",
            "Persistent high fever or chest pain",
        ]

    if not diagnosis:
        diagnosis = f"Review needed for: {message[:80]}"

    if not summary:
        summary = diagnosis

    return {
        "diagnosis": diagnosis,
        "severity": severity,
        "summary": summary,
        "next_steps": next_steps,
        "warning_signs": warning_signs,
        "emergency_message": emergency_message,
    }


def _fallback_assessment(message: str, language: str) -> Dict[str, Any]:
    lowered = message.lower()

    high_keywords = [
        "chest pain", "can't breathe", "cannot breathe", "breathing difficulty",
        "passed out", "unconscious", "stroke", "seizure", "bleeding heavily"
    ]

    medium_keywords = [
        "fever", "vomiting", "headache", "infection",
        "rash", "pain", "stomach", "cough"
    ]

    severity = "Low"
    if any(keyword in lowered for keyword in high_keywords):
        severity = "High"
    elif any(keyword in lowered for keyword in medium_keywords):
        severity = "Medium"

    return {
        "diagnosis": "Symptom-based initial assessment",
        "severity": severity,
        "summary": "This is a basic automated review. Consult a doctor if symptoms worsen.",
        "next_steps": [
            "Rest and monitor symptoms",
            "Stay hydrated",
            "Consult a doctor if needed"
        ],
        "warning_signs": [
            "Breathing difficulty",
            "Severe pain",
            "Loss of consciousness"
        ],
        "emergency_message": "Seek immediate medical help if symptoms worsen."
    }


async def generate_symptom_assessment(message: str, language: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
    return _fallback_assessment(message, language)


def _has_high_severity_keywords(message: str) -> bool:
    lowered = message.lower()
    return any(keyword in lowered for keyword in HIGH_SEVERITY_KEYWORDS)


def _simple_brief_fallback(message: str) -> Dict[str, str]:
    if _has_high_severity_keywords(message):
        return {
            "response": "Your symptoms may be serious and need urgent medical attention.",
            "severity": "High",
        }

    return {
        "response": "Symptoms seem mild. Monitor closely and consult a doctor if needed.",
        "severity": "Low",
    }


async def generate_brief_symptom_analysis(message: str) -> Dict[str, str]:
    stripped_message = message.strip()
    if not stripped_message:
        raise ValueError("Symptom message is required")

    return _simple_brief_fallback(stripped_message)