"""
No-API-key medical information retrieval.

Sources:
    - MedlinePlus Connect Web Service (free, US National Library of Medicine).
      Authoritative for drugs and conditions. No key required.
    - Wikipedia (via the official `wikipedia` Python library — uses public
      Wikipedia API, no key).
    - DuckDuckGo HTML search (via `duckduckgo-search` — no key, but rate-limited).

All three are free and require no signup. Results are cached in-process so we
don't repeat work for the same term during a chat session.
"""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from functools import lru_cache
from typing import List, Optional
from urllib.parse import quote

import requests

log = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 8  # seconds
USER_AGENT = "medical-chatbot/0.1 (educational use)"


@dataclass
class Snippet:
    """A single retrieved piece of evidence."""
    source: str         # e.g. "MedlinePlus", "Wikipedia", "DuckDuckGo"
    title: str
    url: str
    text: str           # short summary, suitable for prompting

    def as_prompt_block(self) -> str:
        return f"[{self.source}] {self.title}\n{self.text}\nURL: {self.url}"


@dataclass
class TermResult:
    term: str
    snippets: List[Snippet] = field(default_factory=list)


# ---------------------------------------------------------------------------
# MedlinePlus
# ---------------------------------------------------------------------------

# MedlinePlus Web Service – consumer-facing, no key, returns ATOM XML.
# Docs: https://medlineplus.gov/about/developers/webservicesoverview/
_MEDLINEPLUS_URL = "https://wsearch.nlm.nih.gov/ws/query"


def _strip_html(s: str) -> str:
    """Crude HTML-to-text. MedlinePlus snippets contain <span class='qt0'> highlights."""
    import re
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip()


def search_medlineplus(term: str, max_results: int = 2) -> List[Snippet]:
    """Query MedlinePlus health topics for a term."""
    params = {"db": "healthTopics", "term": term, "rettype": "brief"}
    try:
        r = requests.get(
            _MEDLINEPLUS_URL,
            params=params,
            headers={"User-Agent": USER_AGENT},
            timeout=DEFAULT_TIMEOUT,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        log.debug("MedlinePlus request failed for %r: %s", term, e)
        return []

    snippets: List[Snippet] = []
    try:
        root = ET.fromstring(r.content)
    except ET.ParseError as e:
        log.debug("MedlinePlus XML parse failed for %r: %s", term, e)
        return []

    for doc in root.findall(".//document")[:max_results]:
        url = doc.attrib.get("url", "")
        title = ""
        snippet = ""
        for content in doc.findall("content"):
            name = content.attrib.get("name", "")
            value = _strip_html(content.text or "")
            if name == "title":
                title = value
            elif name == "FullSummary" and not snippet:
                snippet = value
            elif name == "snippet" and not snippet:
                snippet = value
        if title or snippet:
            snippets.append(
                Snippet(
                    source="MedlinePlus",
                    title=title or term,
                    url=url,
                    text=snippet[:600],
                )
            )
    return snippets


# ---------------------------------------------------------------------------
# Wikipedia
# ---------------------------------------------------------------------------


def search_wikipedia(term: str, sentences: int = 3) -> List[Snippet]:
    """Return one Wikipedia summary for a term, if a reasonable match exists."""
    try:
        import wikipedia  # type: ignore
    except ImportError:
        log.debug("wikipedia package not installed; skipping")
        return []

    wikipedia.set_user_agent(USER_AGENT)
    try:
        # Restrict to top match. auto_suggest=True helps with typos & morphology.
        page_title = wikipedia.search(term, results=1)
        if not page_title:
            return []
        page = wikipedia.page(page_title[0], auto_suggest=False, redirect=True)
        summary = wikipedia.summary(page.title, sentences=sentences, auto_suggest=False)
    except wikipedia.DisambiguationError as e:
        # Pick the first disambiguation option that contains the term.
        try:
            choice = next((o for o in e.options if term.lower() in o.lower()), e.options[0])
            page = wikipedia.page(choice, auto_suggest=False)
            summary = wikipedia.summary(page.title, sentences=sentences, auto_suggest=False)
        except Exception as inner:
            log.debug("Wikipedia disambiguation failed for %r: %s", term, inner)
            return []
    except Exception as e:
        log.debug("Wikipedia lookup failed for %r: %s", term, e)
        return []

    return [Snippet(source="Wikipedia", title=page.title, url=page.url, text=summary)]


# ---------------------------------------------------------------------------
# DuckDuckGo
# ---------------------------------------------------------------------------


def search_duckduckgo(term: str, max_results: int = 2) -> List[Snippet]:
    """Plain web search via DuckDuckGo. Best-effort — DDG sometimes rate-limits."""
    try:
        # The package was renamed; try both import paths.
        try:
            from ddgs import DDGS  # newer name
        except ImportError:
            from duckduckgo_search import DDGS  # type: ignore
    except ImportError:
        log.debug("duckduckgo-search / ddgs not installed; skipping")
        return []

    query = f"{term} medical information"
    snippets: List[Snippet] = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                snippets.append(
                    Snippet(
                        source="DuckDuckGo",
                        title=r.get("title", "") or term,
                        url=r.get("href", "") or r.get("url", ""),
                        text=(r.get("body", "") or "")[:500],
                    )
                )
    except Exception as e:
        log.debug("DuckDuckGo search failed for %r: %s", term, e)
        return []
    return snippets


# ---------------------------------------------------------------------------
# Aggregator
# ---------------------------------------------------------------------------


@lru_cache(maxsize=256)
def lookup_term(term: str, per_source: int = 2) -> tuple:
    """Search all three sources for a term. Returns a tuple of Snippet
    (tuple so it's hashable for lru_cache compatibility — callers typically
    convert to list).
    """
    term = term.strip()
    if not term:
        return tuple()

    results: List[Snippet] = []
    # MedlinePlus first — most authoritative for clinical terms.
    results.extend(search_medlineplus(term, max_results=per_source))
    results.extend(search_wikipedia(term))
    # DuckDuckGo only if the others returned little, to limit rate-limit risk.
    if len(results) < 2:
        results.extend(search_duckduckgo(term, max_results=per_source))
    return tuple(results)


def gather_evidence(terms: List[str], max_per_term: int = 2) -> List[TermResult]:
    """Run lookup_term across many terms and return structured results."""
    out: List[TermResult] = []
    for term in terms:
        snippets = list(lookup_term(term, per_source=max_per_term))
        out.append(TermResult(term=term, snippets=snippets))
    return out


def evidence_as_context(results: List[TermResult], max_chars: int = 6000) -> str:
    """Render the collected evidence as a single context string for the LLM,
    truncated to roughly `max_chars` so we don't blow the model's context window.
    """
    blocks: List[str] = []
    used = 0
    for r in results:
        if not r.snippets:
            continue
        header = f"\n=== Evidence for: {r.term} ===\n"
        blocks.append(header)
        used += len(header)
        for s in r.snippets:
            block = s.as_prompt_block() + "\n"
            if used + len(block) > max_chars:
                blocks.append("... [evidence truncated] ...\n")
                return "".join(blocks)
            blocks.append(block)
            used += len(block)
    return "".join(blocks).strip()
