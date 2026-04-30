"""medical-chatbot pipeline package.

Submodule imports are lazy so that modules with light dependencies (e.g.
sectag_utils) can be used even when heavier optional deps (langchain,
spacy) aren't installed yet.
"""

from importlib import import_module
from typing import Any

# Map of public name -> (submodule, attribute)
_LAZY = {
    "load_document":        ("document_loader", "load_document"),
    "UnsupportedFileType":  ("document_loader", "UnsupportedFileType"),
    "SUPPORTED_ALL":        ("document_loader", "SUPPORTED_ALL"),
    "extract_section":      ("sectag_utils",    "extract_section"),
    "extract_all_sections": ("sectag_utils",    "extract_all_sections"),
    "structured_summary":   ("sectag_utils",    "structured_summary"),
    "extract_entities":     ("extractor",       "extract_entities"),
    "all_entities_flat":    ("extractor",       "all_entities_flat"),
    "gather_evidence":      ("web_search",      "gather_evidence"),
    "evidence_as_context":  ("web_search",      "evidence_as_context"),
    "analyze_document":     ("llm_chain",       "analyze_document"),
    "stream_chat_answer":   ("llm_chain",       "stream_chat_answer"),
    "classify_symptom":     ("llm_chain",       "classify_symptom"),
    "get_llm":              ("llm_chain",       "get_llm"),
    "DEFAULT_MODEL":        ("llm_chain",       "DEFAULT_MODEL"),
}

__all__ = list(_LAZY.keys())


def __getattr__(name: str) -> Any:
    if name in _LAZY:
        mod_name, attr_name = _LAZY[name]
        mod = import_module(f".{mod_name}", __name__)
        value = getattr(mod, attr_name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
