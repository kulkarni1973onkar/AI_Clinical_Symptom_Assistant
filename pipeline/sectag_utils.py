"""
SecTag-based section extraction for clinical notes.

Original logic from the user's sectag_utils.py is preserved (sectag_to_regex
and find_segs). Adds higher-level helpers (extract_section, extract_all_sections)
that the rest of the pipeline uses.
"""

import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

# ---------------------------------------------------------------------------
# Original functions (kept compatible with the user's existing notebook)
# ---------------------------------------------------------------------------


def sectag_to_regex(header_file_path: str, seg_col: str, header_col: str):
    """Load SecTag.csv and build header regex patterns + section name list.

    Args:
        header_file_path: Path to SecTag.csv.
        seg_col:    Column with the canonical section name (e.g. "str").
        header_col: Column with the raw header text used for regex (e.g. "kmname").

    Returns:
        (header_patterns, seg_names): two parallel lists of equal length.
    """
    header_df = pd.read_csv(header_file_path)
    header_df = header_df.drop_duplicates()
    headers = header_df[header_col].tolist()
    header_patterns = [f"^{header}[\n:]" for header in headers]
    return header_patterns, header_df[seg_col].tolist()


def find_segs(note: str, header_patterns: List[str], seg_names: List[str]):
    """Locate every section in `note`. Returns a sorted list of
    [header_text, [section_name, ...], start, end] entries.
    """
    segs: Dict[Tuple[str, int], List[str]] = {}

    for i, pattern in enumerate(header_patterns):
        for m in re.finditer(pattern, note.lower(), re.MULTILINE):
            seg_head = (note[m.span()[0]:m.span()[1]], m.span()[0])
            if seg_head not in segs:
                segs[seg_head] = []
            segs[seg_head].append(seg_names[i])

    seg_list = [[k[0], segs[k], k[1]] for k in segs.keys()]
    seg_list = sorted(seg_list, key=lambda x: x[2])

    for i in range(len(seg_list)):
        if i == len(seg_list) - 1:
            seg_list[i].append(len(note))
        else:
            seg_list[i].append(seg_list[i + 1][2])

    return seg_list


# ---------------------------------------------------------------------------
# New helpers for the chatbot pipeline
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _load_patterns(sectag_csv_path: str):
    """Cache parsed SecTag.csv across calls (CSV has ~6.7k rows; reload is wasteful)."""
    return sectag_to_regex(sectag_csv_path, seg_col="str", header_col="kmname")


def extract_all_sections(note: str, sectag_csv_path: str = "SecTag.csv") -> Dict[str, str]:
    """Return {section_name: text} for every section detected in the note.

    If a header maps to several canonical section names, the section text is
    stored under each — but we keep only the first occurrence per name so
    downstream code gets a stable mapping.
    """
    csv_path = str(Path(sectag_csv_path).resolve())
    header_patterns, seg_names = _load_patterns(csv_path)
    segs = find_segs(note, header_patterns, seg_names)

    sections: Dict[str, str] = {}
    for header_text, names, start, end in segs:
        body = note[start:end].strip()
        for name in names:
            sections.setdefault(name.lower(), body)
    return sections


def extract_section(note: str, section: str = "subjective",
                    sectag_csv_path: str = "SecTag.csv") -> str:
    """Pull a single named section. Returns empty string if not found."""
    return extract_all_sections(note, sectag_csv_path).get(section.lower(), "")


# Sections we surface in the UI (in display order). Anything else still gets
# extracted but lives under "Other".
DISPLAY_SECTIONS = [
    "chief_complaint",
    "subjective",
    "history_of_present_illness",
    "past_medical_history",
    "medications",
    "allergies",
    "physical_examination",
    "assessment",
    "plan",
    "impression",
]


def structured_summary(note: str, sectag_csv_path: str = "SecTag.csv") -> Dict[str, str]:
    """Return a dict with the high-value clinical sections present in the note."""
    all_sections = extract_all_sections(note, sectag_csv_path)
    out = {name: all_sections[name] for name in DISPLAY_SECTIONS if name in all_sections}
    return out
