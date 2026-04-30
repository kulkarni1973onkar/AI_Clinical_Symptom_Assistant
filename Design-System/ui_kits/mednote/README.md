# MedNote UI Kit

High-fidelity recreation of the Medical Note Assistant interface, refactored into clean React components.

## What's here

- **`index.html`** — the full click-thru. Loads the included sample clinical note, simulates token streaming on chat replies. Click the dropzone to load `sample_70.txt`.
- **`Sidebar.jsx`** — settings panel (model, evidence cap, clear session) + brand mark.
- **`Panels.jsx`** — `<Disclaimer>`, `<Uploader>`, `<EntityPills>`, `<SectionCard>`, `<EvidenceItem>`.
- **`Chat.jsx`** — `<ChatPanel>` with composer, message bubbles, streaming cursor.
- **`state.jsx`** — `useChatbot()` hook + canned sample doc & faked reply stream.

## Layout

Mirrors `Medical_Chatbot/app.py`:

```
┌─ Sidebar (280px) ─┬─ Header ────────────────────────────┐
│  brand            │                                     │
│  settings         ├─ Disclaimer banner                  │
│  evidence slider  │                                     │
│  clear            │  ┌─ Doc panel (1) ─┬─ Chat (1.3) ─┐ │
│                   │  │ pills           │ messages     │ │
│  privacy note     │  │ section cards   │              │ │
│                   │  │ evidence list   │ composer     │ │
│                   │  └─────────────────┴──────────────┘ │
└───────────────────┴─────────────────────────────────────┘
```

## Notes / fidelity caveats

- The original is Streamlit, so widgets like the file uploader are recreated cosmetically — no real upload happens. Click the dropzone to load the bundled sample.
- LLM streaming is faked locally (a JS interval revealing characters) — the visual cursor & timing match the real `▌` block.
- All copy comes from the real source: `app.py` strings, `DISCLAIMER.md`, `llm_chain.py` system/analysis prompts.
- Entity term lists from `pipeline/extractor.py` are reflected in the pill examples.
