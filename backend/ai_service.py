import asyncio
import json
import os
import re
import uuid
from typing import Any, Dict, List

from emergentintegrations.llm.chat import LlmChat, UserMessage


GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GEMINI_MODEL = os.environ["GEMINI_MODEL"]
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
        "chest pain",
        "can\'t breathe",
        "cannot breathe",
        "breathing difficulty",
        "passed out",
        "unconscious",
        "stroke",
        "seizure",
        "bleeding heavily",
    ]
    medium_keywords = [
        "fever",
        "vomiting",
        "headache",
        "infection",
        "rash",
        "pain",
        "stomach",
        "cough",
    ]

    severity = "Low"
    if any(keyword in lowered for keyword in high_keywords):
        severity = "High"
    elif any(keyword in lowered for keyword in medium_keywords):
        severity = "Medium"

    if language == "hi":
        messages = {
            "Low": {
                "diagnosis": "हल्के लक्षण दिख रहे हैं, लेकिन निगरानी रखें।",
                "summary": "यह प्राथमिक समीक्षा है। अगर लक्षण बढ़ें तो डॉक्टर से मिलें।",
                "next_steps": [
                    "आराम करें और पानी पीते रहें।",
                    "लक्षण 24 घंटे तक देखें।",
                    "ज़रूरत हो तो डॉक्टर से परामर्श लें।",
                ],
                "warning_signs": ["सांस लेने में दिक्कत", "अचानक तेज दर्द", "बेहोशी या भ्रम"],
                "emergency_message": "अगर लक्षण तेज़ हों तो तुरंत आपातकालीन मदद लें।",
            },
            "Medium": {
                "diagnosis": "मध्यम जोखिम के लक्षण दिख रहे हैं।",
                "summary": "डॉक्टर से जल्द सलाह लेना बेहतर रहेगा।",
                "next_steps": [
                    "आराम करें और शरीर का तापमान/दर्द देखें।",
                    "तरल पदार्थ लें और लक्षण लिखें।",
                    "आज ही डॉक्टर से बात करें।",
                ],
                "warning_signs": ["तेज बुखार", "लगातार उल्टी", "लक्षण तेजी से बढ़ना"],
                "emergency_message": "अगर दर्द या कमजोरी अचानक बढ़े तो तुरंत अस्पताल जाएँ।",
            },
            "High": {
                "diagnosis": "उच्च जोखिम संकेत मिल रहे हैं।",
                "summary": "यह स्थिति गंभीर हो सकती है। तत्काल चिकित्सा सहायता लें।",
                "next_steps": [
                    "तुरंत नज़दीकी अस्पताल जाएँ।",
                    "अकेले न रहें, किसी को साथ रखें।",
                    "आपातकालीन सहायता नंबर पर कॉल करें।",
                ],
                "warning_signs": ["सीने में दर्द", "सांस लेने में दिक्कत", "बेहोशी/दौरा"],
                "emergency_message": "अभी 112 पर कॉल करें या निकटतम इमरजेंसी में जाएँ।",
            },
        }
        return {**messages[severity], "severity": severity}

    messages = {
        "Low": {
            "diagnosis": "Symptoms appear mild, but continue monitoring.",
            "summary": "This is an initial review. Please consult a doctor if symptoms get worse.",
            "next_steps": [
                "Rest and drink enough fluids.",
                "Monitor symptoms over the next 24 hours.",
                "Speak to a doctor if you do not improve.",
            ],
            "warning_signs": ["Breathing difficulty", "Sudden severe pain", "Confusion or fainting"],
            "emergency_message": "Seek urgent care immediately if symptoms rapidly worsen.",
        },
        "Medium": {
            "diagnosis": "Symptoms suggest a moderate concern.",
            "summary": "A clinician review soon would be a good next step.",
            "next_steps": [
                "Rest and keep track of temperature or pain.",
                "Stay hydrated and note any changes.",
                "Arrange a medical consultation today.",
            ],
            "warning_signs": ["High fever", "Repeated vomiting", "Symptoms escalating quickly"],
            "emergency_message": "Go for urgent care if pain, weakness, or breathing issues increase.",
        },
        "High": {
            "diagnosis": "Your symptoms suggest a high-risk situation.",
            "summary": "This may need immediate medical attention.",
            "next_steps": [
                "Go to the nearest hospital immediately.",
                "Stay with someone and avoid being alone.",
                "Call emergency support now.",
            ],
            "warning_signs": ["Chest pain", "Difficulty breathing", "Loss of consciousness or seizures"],
            "emergency_message": "Call 112 now or reach the nearest emergency room immediately.",
        },
    }
    return {**messages[severity], "severity": severity}


async def _call_gemini(message: str, language: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
    conversation = "\n".join([f"{item['role']}: {item['content']}" for item in history[-6:]])
    chat = LlmChat(
        api_key=GEMINI_API_KEY,
        session_id=str(uuid.uuid4()),
        system_message="You are ArogyaAI, a calm multilingual medical triage assistant for first-level symptom screening.",
    )
    chat.with_model("gemini", GEMINI_MODEL).with_params(temperature=0.4, max_tokens=600)

    prompt = f"""
Return ONLY valid JSON with this exact structure:
{{
  "diagnosis": "short likely condition, not final diagnosis",
  "severity": "Low|Medium|High",
  "summary": "2 sentence patient-friendly response in {'Hindi' if language == 'hi' else 'English'}",
  "next_steps": ["step 1", "step 2", "step 3"],
  "warning_signs": ["sign 1", "sign 2", "sign 3"],
  "emergency_message": "one urgent-care sentence"
}}

Rules:
- Keep medical language simple and cautious.
- If chest pain, breathing trouble, fainting, heavy bleeding, seizure, stroke signs, or severe allergic symptoms are present, set severity to High.
- Never claim certainty or replace a doctor.
- Make the response emotionally reassuring.

Conversation history:
{conversation or 'No prior history'}

Latest symptom message:
{message}
"""
    text = await chat.send_message(UserMessage(text=prompt))
    return _normalize_assessment(_extract_json(text), message)


async def generate_symptom_assessment(message: str, language: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
    try:
        return await _call_gemini(message, language, history)
    except Exception:
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
        "response": "Based on your symptoms, it may be a mild infection. Please monitor closely and consult a doctor if it gets worse.",
        "severity": "Low",
    }


async def generate_brief_symptom_analysis(message: str) -> Dict[str, str]:
    stripped_message = message.strip()
    if not stripped_message:
        raise ValueError("Symptom message is required")

    chat = LlmChat(
        api_key=GEMINI_API_KEY,
        session_id=str(uuid.uuid4()),
        system_message="You are ArogyaAI, a careful medical triage assistant. Keep answers short, calm, and cautious.",
    )
    chat.with_model("gemini", GEMINI_MODEL).with_params(temperature=0.3, max_tokens=250)

    prompt = f"""
Return ONLY valid JSON in this exact format:
{{
  "response": "one short diagnosis-style sentence or short explanation",
  "severity": "Low|Medium|High"
}}

Rules:
- Keep the response under 30 words.
- If the symptoms suggest chest pain, breathing trouble, or unconsciousness, severity must be High.
- Do not claim certainty.

User symptoms:
{stripped_message}
"""

    try:
        text = await chat.send_message(UserMessage(text=prompt))
        raw = _extract_json(text)
        response_text = str(raw.get("response") or raw.get("summary") or raw.get("diagnosis") or "Symptom review completed.").strip()
        severity = str(raw.get("severity", "Low")).strip().title()
        if severity not in {"Low", "Medium", "High"}:
            severity = "Low"

        if _has_high_severity_keywords(stripped_message):
            severity = "High"
            response_text = "Your symptoms may be serious and need urgent medical attention."

        return {
            "response": response_text,
            "severity": severity,
        }
    except Exception:
        return _simple_brief_fallback(stripped_message)