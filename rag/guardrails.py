import re

EMERGENCY_PATTERNS = [
    r"chest pain", r"can'?t breathe", r"cannot breathe", r"difficulty breathing",
    r"severe bleeding", r"unconscious", r"seizure", r"stroke", r"heart attack",
    r"suicid", r"kill myself", r"end my life", r"overdose", r"poison",
]

DIAGNOSIS_PATTERNS = [
    r"do i have", r"what disease do i have", r"diagnose me", r"am i suffering from",
    r"what'?s wrong with me",
]

EMERGENCY_MESSAGE = (
    "This may be a medical emergency. Please call your local emergency number "
    "(112 in India) or go to the nearest hospital now. If you are thinking about "
    "harming yourself, please contact a mental health helpline or talk to someone "
    "you trust right away."
)

DIAGNOSIS_MESSAGE = (
    "I can't diagnose conditions. I can share general information from WHO fact "
    "sheets, but please see a doctor for a diagnosis."
)

NO_INFO_MESSAGE = (
    "I couldn't find reliable information on this in my sources, so I won't guess. "
    "Please ask a doctor or check an official health website."
)

DISCLAIMER = "\n\nThis is general information from WHO fact sheets, not medical advice."


def is_emergency(text):
    t = text.lower()
    return any(re.search(p, t) for p in EMERGENCY_PATTERNS)


def asks_for_diagnosis(text):
    t = text.lower()
    return any(re.search(p, t) for p in DIAGNOSIS_PATTERNS)