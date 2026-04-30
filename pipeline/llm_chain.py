"""
LangChain + Ollama integration using the modern LCEL (`prompt | llm`) syntax.

No deprecated APIs:
    - Uses `langchain_ollama.ChatOllama` (not `langchain.llms.Ollama`)
    - Uses `prompt | llm | parser` pipelines (not `LLMChain`)
    - Uses `.invoke()` / `.stream()` (not `.run()`)
"""

from __future__ import annotations

from typing import Iterable, Iterator, List, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

DEFAULT_MODEL = "llama3.2"

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a medical information assistant. You help users \
understand medical notes and prescriptions.

CRITICAL RULES — these are non-negotiable:
1. You are NOT a doctor. You do NOT diagnose, prescribe, or replace medical care.
2. Always remind the user to consult a qualified healthcare provider for any \
medical decision.
3. Ground every factual claim in the EVIDENCE provided. If the evidence does \
not cover something the user asks, say so explicitly — do not invent facts.
4. When listing medications or conditions from the user's document, quote the \
DOCUMENT, not your training data.
5. If the user describes a medical emergency (chest pain with shortness of \
breath, signs of stroke, severe bleeding, suicidal ideation, etc.), tell them \
to seek emergency care immediately and keep the rest of the answer brief.

Style:
- Use plain language a patient could understand.
- Be concise. Use short paragraphs and only use bullets when listing 3+ items.
- When you cite evidence, mention the source name (MedlinePlus, Wikipedia, etc.).
"""

ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", """The user has uploaded a clinical document. Below is what we extracted.

DOCUMENT SECTIONS:
{sections}

ENTITIES FOUND IN THE DOCUMENT:
- Medications: {medications}
- Conditions: {conditions}
- Symptoms: {symptoms}

EVIDENCE GATHERED FROM PUBLIC MEDICAL SOURCES:
{evidence}

Please produce a structured analysis with these parts:
1. **Summary** — what the document is about, in 2-3 sentences.
2. **Medications** — for each medication found, briefly explain what it is \
typically used for, citing the evidence above. If no evidence, say "no \
information retrieved".
3. **Conditions** — same treatment, for each condition.
4. **Notable symptoms** — list symptoms the patient mentioned and whether the \
document indicates they are present or denied (e.g. "denies chest pain").
5. **Questions you might ask your doctor** — 3 short, specific questions \
based on what's in the document.

End with a one-line reminder that this is informational and not medical advice."""),
])

CHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", """A user is asking a follow-up question about their uploaded \
clinical document.

DOCUMENT (relevant sections):
{sections}

ENTITIES FOUND:
- Medications: {medications}
- Conditions: {conditions}
- Symptoms: {symptoms}

EVIDENCE FROM PUBLIC MEDICAL SOURCES:
{evidence}

CONVERSATION SO FAR:
{history}

USER'S QUESTION:
{question}

Answer the user's question. Stay grounded in the document and the evidence. \
If the question is outside what the document covers, say so and answer \
generally if you can — but make clear you're speaking generally.

Briefly remind them this is informational, not medical advice, only if the \
question is asking for advice (not for a definition or simple explanation)."""),
])

SYMPTOM_CLASSIFY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a clinical text classifier. You answer in one word."),
    ("user", """Given the patient's subjective report:
---
{text}
---
Is the symptom or condition '{condition}' present or absent?
Reply with exactly one word: Present or Absent."""),
])


# ---------------------------------------------------------------------------
# LLM factory + chain helpers
# ---------------------------------------------------------------------------


def get_llm(model: str = DEFAULT_MODEL, temperature: float = 0.2,
            base_url: Optional[str] = None) -> ChatOllama:
    """Build a ChatOllama instance. `base_url` defaults to localhost:11434."""
    kwargs = {"model": model, "temperature": temperature}
    if base_url:
        kwargs["base_url"] = base_url
    return ChatOllama(**kwargs)


def _format_history(history: Iterable[dict]) -> str:
    """Render a list of {role, content} messages as a plain transcript."""
    if not history:
        return "(no previous messages)"
    lines = []
    for msg in history:
        role = msg.get("role", "user").capitalize()
        content = msg.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def analyze_document(
    *,
    sections_text: str,
    medications: List[str],
    conditions: List[str],
    symptoms: List[str],
    evidence: str,
    llm: Optional[ChatOllama] = None,
) -> str:
    """One-shot analysis of a freshly uploaded document. Returns the full text."""
    llm = llm or get_llm()
    chain = ANALYSIS_PROMPT | llm | StrOutputParser()
    return chain.invoke({
        "sections": sections_text or "(no sections detected)",
        "medications": ", ".join(medications) or "none detected",
        "conditions": ", ".join(conditions) or "none detected",
        "symptoms": ", ".join(symptoms) or "none detected",
        "evidence": evidence or "(no evidence retrieved)",
    })


def stream_chat_answer(
    *,
    question: str,
    sections_text: str,
    medications: List[str],
    conditions: List[str],
    symptoms: List[str],
    evidence: str,
    history: Iterable[dict],
    llm: Optional[ChatOllama] = None,
) -> Iterator[str]:
    """Stream a follow-up answer token-by-token (great for Streamlit)."""
    llm = llm or get_llm()
    chain = CHAT_PROMPT | llm | StrOutputParser()
    inputs = {
        "sections": sections_text or "(no sections detected)",
        "medications": ", ".join(medications) or "none detected",
        "conditions": ", ".join(conditions) or "none detected",
        "symptoms": ", ".join(symptoms) or "none detected",
        "evidence": evidence or "(no evidence retrieved)",
        "history": _format_history(history),
        "question": question,
    }
    for chunk in chain.stream(inputs):
        yield chunk


def classify_symptom(text: str, condition: str,
                     llm: Optional[ChatOllama] = None) -> str:
    """Replicates the original notebook's Present/Absent classifier, modernized."""
    llm = llm or get_llm(temperature=0.0)
    chain = SYMPTOM_CLASSIFY_PROMPT | llm | StrOutputParser()
    raw = chain.invoke({"text": text, "condition": condition}).strip().split()
    return raw[0] if raw else "Unknown"
