import json
import os
import re
from typing import Any, Dict, List

from dotenv import load_dotenv

load_dotenv()

# Try to import emergentintegrations, use fallback if not available
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("Warning: emergentintegrations not available, using rule-based fallback only")


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
    """
    Hybrid AI + Rule-Based Symptom Assessment
    1. Use AI to understand and analyze symptoms
    2. Apply rule-based safety layer to override severity if needed
    3. Combine results for intelligent yet safe medical guidance
    """
    
    # Step 1: Apply rule-based safety classification first
    rule_severity, recommended_action = _enhanced_severity_classification(message)
    
    # Step 2: Try AI analysis if available
    ai_analysis = None
    if AI_AVAILABLE and os.environ.get("EMERGENT_LLM_KEY"):
        try:
            ai_analysis = await _get_ai_symptom_analysis(message, language, history)
        except Exception as e:
            print(f"AI analysis failed, using rule-based fallback: {e}")
    
    # Step 3: Combine AI and rule-based results
    if ai_analysis:
        # AI provided analysis, but rule-based severity takes precedence for safety
        final_severity = rule_severity  # Safety first - always use rule-based severity
        
        # Use AI's diagnosis and insights
        diagnosis = ai_analysis.get("diagnosis", "Symptom assessment based on your description")
        summary = ai_analysis.get("summary", f"{diagnosis}. {recommended_action}.")
        
        # Merge next steps: prioritize rule-based for high severity, otherwise use AI
        if rule_severity == "High":
            next_steps = _get_severity_next_steps(rule_severity, message)
        else:
            next_steps = ai_analysis.get("next_steps", _get_severity_next_steps(rule_severity, message))
        
        warning_signs = ai_analysis.get("warning_signs", _get_severity_warning_signs(rule_severity))
        emergency_message = _get_severity_emergency_message(rule_severity)
        
        return {
            "diagnosis": diagnosis,
            "severity": final_severity,
            "summary": summary,
            "next_steps": next_steps[:3],
            "warning_signs": warning_signs[:3],
            "emergency_message": emergency_message,
            "recommended_action": recommended_action,
            "analysis_method": "hybrid_ai_rules"
        }
    else:
        # No AI available, use enhanced rule-based assessment
        return _fallback_assessment(message, language)


async def _get_ai_symptom_analysis(message: str, language: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Use AI to analyze symptoms and provide intelligent medical insights
    Returns diagnosis, summary, next_steps, and warning_signs
    """
    
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise ValueError("EMERGENT_LLM_KEY not configured")
    
    system_message = """You are a medical symptom analyzer assistant. Your role is to:
1. Analyze patient-reported symptoms carefully
2. Identify possible conditions based on symptoms
3. Provide clear, actionable medical guidance
4. Be empathetic and professional

IMPORTANT: You provide analysis only. The severity level is determined by a separate safety system.

Return your analysis as JSON with this structure:
{
    "diagnosis": "Brief possible condition or issue",
    "summary": "Clear explanation of the assessment",
    "next_steps": ["Step 1", "Step 2", "Step 3"],
    "warning_signs": ["Sign 1", "Sign 2", "Sign 3"]
}"""

    if language == "hi":
        system_message += "\n\nProvide all responses in Hindi language."
    
    try:
        # Initialize AI chat
        chat = LlmChat(
            api_key=api_key,
            session_id=f"symptom-analysis-{hash(message)}",
            system_message=system_message
        ).with_model("gemini", "gemini-2.5-flash")
        
        # Create analysis prompt
        prompt = f"""Analyze these symptoms and provide medical guidance:

Patient Description: {message}

Please provide:
1. What possible condition or issue this might indicate
2. A clear summary explaining your assessment
3. Three specific next steps the patient should take
4. Three warning signs to watch for

Return ONLY valid JSON matching the specified format."""
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parse AI response
        return _extract_json(response)
        
    except Exception as e:
        print(f"AI analysis error: {e}")
        raise


def _get_severity_next_steps(severity: str, message: str) -> List[str]:
    """Get next steps based on severity level"""
    lowered = message.lower()
    
    if severity == "High":
        return [
            "Seek immediate medical attention or call emergency services",
            "Do not wait - this could be a serious condition requiring urgent care",
            "Go to the nearest emergency room or urgent care center"
        ]
    elif severity == "Medium":
        # Customize based on symptoms
        if "fever" in lowered:
            return [
                "Schedule a doctor's appointment within the next 1-2 days",
                "Monitor your temperature and keep a symptom diary",
                "Stay hydrated and rest"
            ]
        else:
            return [
                "Schedule a doctor's appointment within the next few days",
                "Monitor symptoms closely and note any changes",
                "Avoid self-medication without consulting a healthcare provider"
            ]
    else:  # Low
        return [
            "Monitor symptoms over the next 24-48 hours",
            "Rest, stay hydrated, and maintain good nutrition",
            "Consult a doctor if symptoms persist beyond a few days or worsen"
        ]


def _get_severity_warning_signs(severity: str) -> List[str]:
    """Get warning signs based on severity level"""
    if severity == "High":
        return [
            "Worsening symptoms or new severe symptoms",
            "Difficulty breathing or chest pain",
            "Loss of consciousness or severe confusion"
        ]
    elif severity == "Medium":
        return [
            "Symptoms getting worse instead of better",
            "New symptoms developing",
            "Fever above 103°F (39.4°C) or persistent high fever"
        ]
    else:  # Low
        return [
            "Symptoms lasting more than a week without improvement",
            "Fever developing or increasing",
            "Significant worsening of your condition"
        ]


def _get_severity_emergency_message(severity: str) -> str:
    """Get emergency message based on severity"""
    if severity == "High":
        return "⚠️ URGENT: Seek immediate medical help. Do not delay."
    elif severity == "Medium":
        return "If symptoms worsen rapidly or new concerning symptoms appear, seek immediate medical attention."
    else:
        return "Seek medical help if symptoms worsen or new concerning symptoms appear."


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
    """
    Hybrid brief symptom analysis
    Uses AI for intelligent response, rule-based for severity safety
    """
    stripped_message = message.strip()
    if not stripped_message:
        raise ValueError("Symptom message is required")
    
    # Rule-based severity classification (safety layer)
    severity, recommended_action = _enhanced_severity_classification(stripped_message)
    
    # Try AI for intelligent response
    if AI_AVAILABLE and os.environ.get("EMERGENT_LLM_KEY"):
        try:
            api_key = os.environ.get("EMERGENT_LLM_KEY")
            
            chat = LlmChat(
                api_key=api_key,
                session_id=f"brief-analysis-{hash(stripped_message)}",
                system_message="You are a medical assistant providing brief, empathetic symptom assessments. Be concise but caring."
            ).with_model("gemini", "gemini-2.5-flash")
            
            prompt = f"""Provide a brief (1-2 sentences) empathetic response to these symptoms: {stripped_message}

Focus on acknowledging their concern and providing reassurance or urgency as appropriate. Do not include severity level in your response."""
            
            user_message = UserMessage(text=prompt)
            ai_response = await chat.send_message(user_message)
            
            # Combine AI response with rule-based severity
            return {
                "response": f"{ai_response.strip()} {recommended_action}.",
                "severity": severity,
            }
            
        except Exception as e:
            print(f"Brief AI analysis failed: {e}")
            # Fall through to rule-based fallback
    
    # Fallback to rule-based
    return _simple_brief_fallback(stripped_message)