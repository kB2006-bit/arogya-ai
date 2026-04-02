import json
import re
from typing import Any, Dict, List


# Enhanced severity classification keywords
HIGH_SEVERITY_KEYWORDS = [
    "chest pain", "heart attack", "stroke", "can't breathe", "cannot breathe",
    "breathing difficulty", "shortness of breath", "unconscious", "passed out",
    "seizure", "bleeding heavily", "severe bleeding", "blood in stool", "blood in urine",
    "coughing blood", "vomiting blood", "severe head injury", "head trauma",
    "loss of vision", "sudden blindness", "paralysis", "can't move", "cannot move",
    "severe abdominal pain", "suicide", "suicidal", "overdose"
]

MEDIUM_SEVERITY_KEYWORDS = [
    "fever", "high fever", "persistent fever", "vomiting", "severe vomiting",
    "diarrhea", "severe diarrhea", "infection", "wound infection", "deep cut",
    "broken bone", "fracture", "sprain", "severe pain", "persistent pain",
    "rash", "severe rash", "allergic reaction", "swelling", "severe swelling",
    "headache", "migraine", "severe headache", "dehydration", "fainting",
    "dizziness", "confusion", "disorientation", "weakness", "numbness"
]

SERIOUS_SYMPTOMS_INDICATORS = [
    "lump", "mass", "growth", "tumor", "unexplained weight loss",
    "night sweats", "persistent cough", "coughing for weeks",
    "difficulty swallowing", "blood", "bleeding", "bruising easily",
    "chronic pain", "pain for weeks", "yellow skin", "jaundice"
]


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
    """Enhanced fallback assessment with better severity classification"""
    severity, recommended_action = _enhanced_severity_classification(message)
    lowered = message.lower()
    
    # Determine possible condition based on keywords
    possible_condition = "General symptom assessment"
    
    if "fever" in lowered and "cough" in lowered:
        possible_condition = "Possible respiratory infection or flu"
    elif "chest pain" in lowered:
        possible_condition = "Possible cardiac or respiratory issue - requires immediate attention"
    elif "headache" in lowered and ("severe" in lowered or "persistent" in lowered):
        possible_condition = "Possible migraine or other neurological concern"
    elif "stomach" in lowered or "abdominal" in lowered:
        possible_condition = "Possible gastrointestinal issue"
    elif "rash" in lowered or "skin" in lowered:
        possible_condition = "Possible dermatological condition or allergic reaction"
    elif any(word in lowered for word in ["lump", "mass", "growth"]):
        possible_condition = "Requires medical examination for proper diagnosis"
    elif "bleeding" in lowered or "blood" in lowered:
        possible_condition = "Requires immediate medical evaluation"
    
    # Customize next steps based on severity
    if severity == "High":
        next_steps = [
            "Seek immediate medical attention or call emergency services",
            "Do not wait - this could be a serious condition",
            "Go to the nearest emergency room or urgent care center"
        ]
        warning_signs = [
            "Worsening symptoms",
            "Difficulty breathing",
            "Loss of consciousness or severe confusion"
        ]
        emergency_message = "⚠️ URGENT: Seek immediate medical help. Do not delay."
    elif severity == "Medium":
        next_steps = [
            "Schedule a doctor's appointment within the next few days",
            "Monitor symptoms closely and keep a symptom diary",
            "Avoid self-medication without consulting a healthcare provider"
        ]
        warning_signs = [
            "Symptoms getting worse instead of better",
            "New symptoms developing",
            "Fever above 103°F (39.4°C)"
        ]
        emergency_message = "If symptoms worsen rapidly, seek immediate medical attention."
    else:  # Low severity
        next_steps = [
            "Monitor symptoms over the next 24-48 hours",
            "Rest, stay hydrated, and maintain good nutrition",
            "Consult a doctor if symptoms persist beyond a few days"
        ]
        warning_signs = [
            "Symptoms lasting more than a week",
            "Fever developing or increasing",
            "Significant worsening of condition"
        ]
        emergency_message = "Seek medical help if symptoms worsen or new concerning symptoms appear."

    return {
        "diagnosis": possible_condition,
        "severity": severity,
        "summary": f"{possible_condition}. {recommended_action}.",
        "next_steps": next_steps,
        "warning_signs": warning_signs,
        "emergency_message": emergency_message,
        "recommended_action": recommended_action
    }


async def generate_symptom_assessment(message: str, language: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
    return _fallback_assessment(message, language)


def _enhanced_severity_classification(message: str) -> tuple[str, str]:
    """
    Enhanced rule-based severity classification
    Returns: (severity_level, recommended_action)
    """
    lowered = message.lower()
    
    # Check for high severity indicators
    for keyword in HIGH_SEVERITY_KEYWORDS:
        if keyword in lowered:
            return ("High", "Seek immediate medical attention or call emergency services")
    
    # Check for serious symptoms that warrant medical consultation
    for indicator in SERIOUS_SYMPTOMS_INDICATORS:
        if indicator in lowered:
            return ("High", "Consult a doctor as soon as possible for proper diagnosis")
    
    # Check for medium severity
    for keyword in MEDIUM_SEVERITY_KEYWORDS:
        if keyword in lowered:
            return ("Medium", "Schedule a doctor's appointment within the next few days")
    
    # Default to low if no specific indicators found
    return ("Low", "Monitor symptoms and consult a doctor if they persist or worsen")


def _simple_brief_fallback(message: str) -> Dict[str, str]:
    """Enhanced brief analysis with better severity detection"""
    severity, recommended_action = _enhanced_severity_classification(message)
    
    if severity == "High":
        response = f"⚠️ Your symptoms may require immediate medical attention. {recommended_action}."
    elif severity == "Medium":
        response = f"Your symptoms should be evaluated by a healthcare provider. {recommended_action}."
    else:
        response = f"Monitor your symptoms closely. {recommended_action}."
    
    return {
        "response": response,
        "severity": severity,
    }


async def generate_brief_symptom_analysis(message: str) -> Dict[str, str]:
    stripped_message = message.strip()
    if not stripped_message:
        raise ValueError("Symptom message is required")

    return _simple_brief_fallback(stripped_message)