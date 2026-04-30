"""
Entity extraction over clinical text using spaCy's rule-based Matcher.

Three entity types:
    - symptoms:   patient-reported issues (cough, pain, headache, ...)
    - medications: common drug names and pharma stems
    - conditions: chronic diagnoses / impressions

This is intentionally rule-based (not a NER model) so it runs fast on CPU
and is easy to extend — add a term to the relevant list and it just works.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Dict, List

import spacy
from spacy.matcher import Matcher, PhraseMatcher

# ---------------------------------------------------------------------------
# Term lists. Extend these freely — they're the easiest customization point.
# ---------------------------------------------------------------------------

SYMPTOMS = [
    "pain", "numbness", "tingling", "insomnia", "asthma", "cough", "fever",
    "diarrhea", "headache", "depression", "nausea", "vomiting", "fatigue",
    "dizziness", "shortness of breath", "chest pain", "palpitations",
    "constipation", "abdominal pain", "swelling", "tightness", "heaviness",
    "pressure", "rash", "itching", "anxiety", "weight loss", "weight gain",
    "blurred vision", "sore throat", "sinus congestion", "drainage",
    "back pain", "joint pain", "nocturia",
]

CONDITIONS = [
    "hypertension", "hypercholesterolemia", "diabetes mellitus", "diabetes",
    "asthma", "copd", "osteoarthritis", "arthritis", "depression",
    "anxiety", "sinusitis", "crohn's", "crohn's disease", "cancer",
    "stroke", "heart failure", "atrial fibrillation", "obesity",
    "hypothyroidism", "hyperthyroidism", "anemia", "migraine",
    "gerd", "pneumonia", "bronchitis",
]

# Common medications (generic + a few brand names that appear in clinical notes).
MEDICATIONS = [
    "altace", "ramipril", "lisinopril", "metoprolol", "atorvastatin", "lipitor",
    "simvastatin", "metformin", "insulin", "amlodipine", "losartan",
    "hydrochlorothiazide", "aspirin", "ibuprofen", "acetaminophen",
    "tylenol", "advil", "warfarin", "clopidogrel", "omeprazole", "prilosec",
    "allegra", "fexofenadine", "albuterol", "prednisone", "amoxicillin",
    "azithromycin", "ciprofloxacin", "levothyroxine", "synthroid",
    "gabapentin", "tramadol", "oxycodone", "morphine", "sertraline",
    "fluoxetine", "citalopram", "escitalopram",
]


# ---------------------------------------------------------------------------
# spaCy setup
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _load_nlp():
    """Load en_core_web_sm once and configure Matchers.

    Symptoms use `Matcher` with LOWER tokens (matches your original notebook).
    Conditions and medications use `PhraseMatcher` because some terms are
    multi-word and PhraseMatcher handles that more cleanly than nested patterns.
    """
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError as e:
        raise OSError(
            "spaCy model 'en_core_web_sm' is missing. Install it with:\n"
            "    python -m spacy download en_core_web_sm"
        ) from e

    # Symptoms — match exactly your original logic.
    symptom_matcher = Matcher(nlp.vocab)
    single_word = [s for s in SYMPTOMS if " " not in s]
    multi_word = [s for s in SYMPTOMS if " " in s]
    symptom_matcher.add(
        "SYMPTOMS_SINGLE",
        [[{"LOWER": w}] for w in single_word],
    )
    symptom_phrases = PhraseMatcher(nlp.vocab, attr="LOWER")
    if multi_word:
        symptom_phrases.add("SYMPTOMS_MULTI", [nlp.make_doc(t) for t in multi_word])

    # Conditions
    condition_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    condition_matcher.add("CONDITIONS", [nlp.make_doc(t) for t in CONDITIONS])

    # Medications
    medication_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    medication_matcher.add("MEDICATIONS", [nlp.make_doc(t) for t in MEDICATIONS])

    return nlp, symptom_matcher, symptom_phrases, condition_matcher, medication_matcher


def _matches_to_terms(doc, *matchers) -> List[str]:
    """Apply matchers to a doc and return a deduplicated, lowercased term list."""
    seen = set()
    out: List[str] = []
    for matcher in matchers:
        for _, start, end in matcher(doc):
            term = doc[start:end].text.lower().strip()
            if term and term not in seen:
                seen.add(term)
                out.append(term)
    return out


def extract_entities(text: str) -> Dict[str, List[str]]:
    """Run all matchers on `text` and return entities grouped by category.

    Returns:
        {"symptoms": [...], "conditions": [...], "medications": [...]}
    """
    if not text or not text.strip():
        return {"symptoms": [], "conditions": [], "medications": []}

    nlp, sym_m, sym_p, cond_m, med_m = _load_nlp()
    doc = nlp(text)
    return {
        "symptoms": _matches_to_terms(doc, sym_m, sym_p),
        "conditions": _matches_to_terms(doc, cond_m),
        "medications": _matches_to_terms(doc, med_m),
    }


def all_entities_flat(entities: Dict[str, List[str]]) -> List[str]:
    """Flatten the entity dict into a single deduplicated list, preserving order."""
    seen = set()
    out = []
    for group in ("medications", "conditions", "symptoms"):
        for term in entities.get(group, []):
            if term not in seen:
                seen.add(term)
                out.append(term)
    return out
