"""
Streamlit medical-document chatbot.

Run with:
    streamlit run app.py

Prerequisites:
    1. Ollama running locally:        ollama serve
    2. Model pulled:                  ollama pull llama3.2
    3. Python deps:                   pip install -r requirements.txt
    4. spaCy model:                   python -m spacy download en_core_web_sm
    5. (For images / scanned PDFs)    Tesseract installed at the OS level
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from pipeline import (
    DEFAULT_MODEL,
    UnsupportedFileType,
    all_entities_flat,
    analyze_document,
    evidence_as_context,
    extract_entities,
    gather_evidence,
    get_llm,
    load_document,
    stream_chat_answer,
    structured_summary,
)

# ---------------------------------------------------------------------------
# Page config + styling
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Medical Note Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Clinical, trust-forward styling: muted teal/slate, generous whitespace,
# clear typographic hierarchy. Kept minimal because Streamlit constrains CSS.
st.markdown(
    """
    <style>
      :root {
        --accent: #0f766e;
        --accent-soft: #ccfbf1;
        --warning-bg: #fef3c7;
        --warning-border: #f59e0b;
        --text-muted: #64748b;
      }
      .disclaimer {
        background: var(--warning-bg);
        border-left: 4px solid var(--warning-border);
        padding: 0.85rem 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        font-size: 0.92rem;
      }
      .pill {
        display: inline-block;
        background: var(--accent-soft);
        color: var(--accent);
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 0.82rem;
        margin: 2px 4px 2px 0;
        font-weight: 500;
      }
      .section-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
      }
      .section-card h4 {
        margin: 0 0 0.4rem 0;
        color: var(--accent);
        text-transform: uppercase;
        font-size: 0.78rem;
        letter-spacing: 0.06em;
      }
      .source-note {
        color: var(--text-muted);
        font-size: 0.82rem;
        margin-top: 0.3rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------

DEFAULTS = {
    "document_text": "",        # raw extracted text
    "document_name": "",        # original filename
    "sections": {},             # {section_name: text} from SecTag
    "entities": {"medications": [], "conditions": [], "symptoms": []},
    "evidence_results": [],     # list[TermResult]
    "evidence_context": "",     # rendered string
    "analysis": "",             # initial LLM analysis
    "messages": [],              # chat history: list[{"role", "content"}]
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ---------------------------------------------------------------------------
# Sidebar — settings + ingestion
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    model_name = st.text_input(
        "Ollama model",
        value=DEFAULT_MODEL,
        help="Any model you've pulled with `ollama pull <name>`.",
    )
    base_url = st.text_input(
        "Ollama base URL (optional)",
        value="",
        placeholder="http://localhost:11434",
    )
    max_evidence_terms = st.slider(
        "Web-evidence: max entities to research",
        min_value=0,
        max_value=10,
        value=5,
        help="How many of the extracted entities to look up online.",
    )

    st.divider()

    if st.button("🔄 Clear session", use_container_width=True):
        for k, v in DEFAULTS.items():
            st.session_state[k] = v if not isinstance(v, (list, dict)) else type(v)()
        st.rerun()

    st.divider()
    st.caption(
        "Sources used for evidence: **MedlinePlus** (US NLM), **Wikipedia**, "
        "**DuckDuckGo**. No external API keys."
    )


# ---------------------------------------------------------------------------
# Header + disclaimer
# ---------------------------------------------------------------------------

st.title("🩺 Medical Note Assistant")
st.caption(
    "Upload a clinical note or prescription. The assistant extracts sections, "
    "identifies medications/conditions/symptoms, gathers context from public "
    "medical sources, and explains it in plain language."
)

st.markdown(
    """
    <div class="disclaimer">
      <strong>⚠️ Not medical advice.</strong>
      This tool is for educational and informational purposes only. It does not
      diagnose, prescribe, or replace professional medical care. Always consult
      a qualified healthcare provider for medical decisions. If you may be
      experiencing a medical emergency, call your local emergency number.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# File ingestion
# ---------------------------------------------------------------------------


def process_uploaded_file(uploaded_file) -> bool:
    """Run the full pipeline on a freshly uploaded file. Returns True on success."""
    name = uploaded_file.name
    data = uploaded_file.read()

    with st.spinner(f"Reading **{name}** …"):
        try:
            text = load_document(data, filename=name)
        except UnsupportedFileType as e:
            st.error(str(e))
            return False
        except ImportError as e:
            st.error(f"Missing dependency: {e}")
            return False
        except Exception as e:
            st.error(f"Could not read file: {e}")
            return False

    if not text or not text.strip():
        st.error("The file appears to be empty or unreadable.")
        return False

    st.session_state.document_text = text
    st.session_state.document_name = name

    sectag_path = Path(__file__).parent / "SecTag.csv"
    with st.spinner("Extracting clinical sections …"):
        st.session_state.sections = structured_summary(text, str(sectag_path))

    with st.spinner("Identifying medications, conditions, and symptoms …"):
        # Run on the full document so we don't miss meds/conditions that live
        # outside the Subjective section.
        st.session_state.entities = extract_entities(text)

    flat_terms = all_entities_flat(st.session_state.entities)[:max_evidence_terms]
    if flat_terms:
        with st.spinner(f"Gathering evidence for {len(flat_terms)} term(s) from public sources …"):
            results = gather_evidence(flat_terms)
            st.session_state.evidence_results = results
            st.session_state.evidence_context = evidence_as_context(results)
    else:
        st.session_state.evidence_results = []
        st.session_state.evidence_context = ""

    # Initial analysis from the LLM
    with st.spinner("Generating analysis with Ollama …"):
        try:
            llm = get_llm(model=model_name, base_url=base_url or None)
            sections_text = "\n\n".join(
                f"## {name.replace('_', ' ').title()}\n{body}"
                for name, body in st.session_state.sections.items()
            ) or text  # fallback to raw text if no sections detected
            analysis = analyze_document(
                sections_text=sections_text,
                medications=st.session_state.entities["medications"],
                conditions=st.session_state.entities["conditions"],
                symptoms=st.session_state.entities["symptoms"],
                evidence=st.session_state.evidence_context,
                llm=llm,
            )
            st.session_state.analysis = analysis
            st.session_state.messages = [
                {"role": "assistant", "content": analysis},
            ]
        except Exception as e:
            st.error(
                f"Could not reach Ollama. Make sure `ollama serve` is running "
                f"and the model `{model_name}` is pulled. Error: {e}"
            )
            return False

    return True


uploaded = st.file_uploader(
    "Upload a clinical note or prescription",
    type=["txt", "md", "pdf", "png", "jpg", "jpeg", "tiff", "tif", "bmp", "webp"],
    help="Text, PDF, or image. Images and scanned PDFs are OCR'd with Tesseract.",
)

if uploaded and uploaded.name != st.session_state.document_name:
    process_uploaded_file(uploaded)


# ---------------------------------------------------------------------------
# Main two-column layout — extracted info on the left, chat on the right
# ---------------------------------------------------------------------------


if not st.session_state.document_text:
    st.info("👆 Upload a document above to get started.")
    st.stop()


left, right = st.columns([1, 1.3])


with left:
    st.markdown(f"### 📄 {st.session_state.document_name}")

    # Entity pills
    ents = st.session_state.entities
    if any(ents.values()):
        st.markdown("#### Identified")
        for label, items in [
            ("Medications", ents["medications"]),
            ("Conditions", ents["conditions"]),
            ("Symptoms", ents["symptoms"]),
        ]:
            if items:
                pills = " ".join(f'<span class="pill">{t}</span>' for t in items)
                st.markdown(f"**{label}:** {pills}", unsafe_allow_html=True)
    else:
        st.info("No medications, conditions, or symptoms matched the term lists.")

    # Sections
    if st.session_state.sections:
        st.markdown("#### Sections (via SecTag)")
        for name, body in st.session_state.sections.items():
            with st.expander(name.replace("_", " ").title()):
                st.write(body)
    else:
        with st.expander("Raw document text"):
            st.write(st.session_state.document_text)

    # Sources used
    if st.session_state.evidence_results:
        st.markdown("#### Evidence sources")
        for r in st.session_state.evidence_results:
            if not r.snippets:
                continue
            with st.expander(f"🔍 {r.term}  ({len(r.snippets)} source(s))"):
                for s in r.snippets:
                    st.markdown(f"**[{s.source}]** {s.title}")
                    st.write(s.text)
                    if s.url:
                        st.markdown(f"[Open source ↗]({s.url})")
                    st.markdown("---")


with right:
    st.markdown("### 💬 Chat")
    st.caption(
        "Ask follow-up questions: *What does Altace do?*, *Why might my BP be 150/60?*, "
        "*Should I be worried about any of this?*"
    )

    # Render existing history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_q = st.chat_input("Ask a question about your document…")
    if user_q:
        st.session_state.messages.append({"role": "user", "content": user_q})
        with st.chat_message("user"):
            st.markdown(user_q)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            collected = ""
            try:
                llm = get_llm(model=model_name, base_url=base_url or None)
                sections_text = "\n\n".join(
                    f"## {name.replace('_', ' ').title()}\n{body}"
                    for name, body in st.session_state.sections.items()
                ) or st.session_state.document_text

                # History excludes the just-appended user turn.
                history_for_prompt = st.session_state.messages[:-1]

                for token in stream_chat_answer(
                    question=user_q,
                    sections_text=sections_text,
                    medications=st.session_state.entities["medications"],
                    conditions=st.session_state.entities["conditions"],
                    symptoms=st.session_state.entities["symptoms"],
                    evidence=st.session_state.evidence_context,
                    history=history_for_prompt,
                    llm=llm,
                ):
                    collected += token
                    placeholder.markdown(collected + "▌")
                placeholder.markdown(collected)
            except Exception as e:
                collected = (
                    f"Sorry — I couldn't generate a response. "
                    f"Is Ollama running and the model `{model_name}` pulled?\n\n"
                    f"Error: `{e}`"
                )
                placeholder.error(collected)

        st.session_state.messages.append({"role": "assistant", "content": collected})
