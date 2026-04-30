# Medical Note Assistant — Design System

A calm, trust-forward design system for an AI clinical chatbot that reads medical notes, prescriptions, and OCR'd images, then explains them in plain language.

## Product context

**Product name:** Medical Note Assistant (working name "MedNote")
**Category:** Local-first AI chatbot for clinical document understanding.
**Users:** Patients trying to make sense of their own medical paperwork; caregivers; med students; clinicians wanting a fast plain-language summary.
**Stance:** Educational, grounded, not-medical-advice. Every screen reminds the user this is informational only.

The product:

1. Lets the user upload a clinical note or prescription (`.txt`, `.pdf`, image — OCR auto-applies).
2. Splits it into clinical sections via SecTag (Subjective, Medications, Plan, etc).
3. Extracts medications, conditions, and symptoms via a spaCy rule-based matcher.
4. Pulls evidence from MedlinePlus, Wikipedia, DuckDuckGo (no API keys).
5. Generates a structured plain-language analysis via a **local** LLM (Ollama + LangChain).
6. Lets the user chat to ask follow-ups, with token streaming.

The whole thing runs locally — privacy is a first-class brand value. The only external traffic is the evidence step (and only term names go out).

## Sources used to build this system

- **Local codebase**: `Medical_Chatbot/` (mounted via File System Access API). Key files:
  - `Medical_Chatbot/app.py` — Streamlit UI; **this defines the visual DNA** (teal `#0f766e`, slate slate-50/slate-200, amber warning rail, pill components, section cards).
  - `Medical_Chatbot/DISCLAIMER.md` — voice & legal posture.
  - `Medical_Chatbot/README.md` — product narrative.
  - `Medical_Chatbot/pipeline/llm_chain.py` — system prompt, content tone, the 5-part analysis structure.
  - `Medical_Chatbot/pipeline/extractor.py` — entity term lists (symptoms / conditions / medications).
  - `Medical_Chatbot/ClinicalNotes/sample_70.txt` — representative input the UI will display.
- **GitHub**: [`kulkarni1973onkar/AI_Clinical_Symptom_Assistant`](https://github.com/kulkarni1973onkar/AI_Clinical_Symptom_Assistant) — the public predecessor of the local codebase. Same files; nothing new there.

No Figma was provided. No brand guidelines existed before this — the system below is **synthesized from the existing code's CSS and tone**, then extended into a complete language.

---

## CONTENT FUNDAMENTALS

The product talks to a frightened human about their own body. Tone is **calm, second-person, plain-language, careful**.

### Voice rules

- **Plain language a patient could understand.** No jargon without an immediate gloss. ("Altace (a blood-pressure medicine)" not just "Altace".)
- **Second person, you/your.** "Your document mentions…", not "The user uploaded…".
- **Never diagnose, prescribe, or replace care.** Every analysis ends with a one-line reminder: *This is informational and not medical advice.*
- **Quote the document, not the model's training data.** When listing meds/conditions, the source is always the user's file.
- **Cite sources by name** — "MedlinePlus says…", "Per Wikipedia…". Never silent claims.
- **Emergency guardrail.** If the user describes chest pain + shortness of breath, signs of stroke, severe bleeding, or suicidal ideation → tell them to seek emergency care immediately, then keep the rest brief.

### Structure
The default analysis follows a fixed 5-part scaffold (from `llm_chain.py`):
1. **Summary** (2–3 sentences)
2. **Medications** — what each is typically used for, cited.
3. **Conditions** — same.
4. **Notable symptoms** — present vs. denied (e.g. "denies chest pain").
5. **Questions you might ask your doctor** — 3 short, specific ones.

### Casing & punctuation

- **Sentence case** for all UI strings, headings, button labels. ("Upload a document", not "Upload A Document".)
- Section labels in the analysis are bold, e.g. **Summary**, **Medications**.
- Em dashes are fine; avoid exclamation marks.
- Section headers in the side panel are ALL-CAPS, letterspaced, small (`text-transform: uppercase; letter-spacing: 0.06em; font-size: 0.78rem`) — straight from the existing CSS.

### Emoji

Used **sparingly and semantically** — only as functional glyphs that anchor a category, never decoratively.

| Emoji | Meaning | Where |
|---|---|---|
| 🩺 | The product itself | Page title, favicon |
| ⚠️ | Disclaimer / not medical advice | Warning callout only |
| 📄 | Uploaded document | Document header |
| 💬 | Chat | Chat panel header |
| 🔍 | Evidence source | Each source expander |
| ⚙️ | Settings | Sidebar |
| 🔄 | Reset / clear | Clear-session button |

That's the whole inventory. Don't introduce new ones without a reason.

### Sample copy (real, in-product)

- Hero caption: *"Upload a clinical note or prescription. The assistant extracts sections, identifies medications/conditions/symptoms, gathers context from public medical sources, and explains it in plain language."*
- Disclaimer: *"⚠️ Not medical advice. This tool is for educational and informational purposes only. It does not diagnose, prescribe, or replace professional medical care…"*
- Chat placeholder: *"Ask a question about your document…"*
- Chat helper examples: *"What does Altace do? — Why might my BP be 150/60? — Should I be worried about any of this?"*
- Empty state: *"👆 Upload a document above to get started."*

---

## VISUAL FOUNDATIONS

A "clinical, trust-forward" aesthetic — the kind a hospital intranet would aspire to but rarely achieve. Generous whitespace, cool muted teal as the only saturated color, slate neutrals, and one warm amber reserved for *you must read this*.

### Color

The whole palette derives from three named hues from `app.py`:

- `--accent: #0f766e` — **teal-700** (Tailwind). The single brand color; used for buttons, links, pill text, section labels.
- `--accent-soft: #ccfbf1` — **teal-100**. Pill backgrounds, hover halos, soft fills.
- `--warning-bg: #fef3c7` / `--warning-border: #f59e0b` — **amber-100/500**. Disclaimers ONLY. Never decorative.
- `--text-muted: #64748b` — **slate-500**. Captions, source notes.
- Surface neutrals: `#ffffff`, `#f8fafc` (slate-50), `#e2e8f0` (slate-200), `#0f172a` (slate-900 ink).

A short scale of teal is provided (50→900) for charts/states. Reds/greens exist as semantic-only (`error`, `success`) and look slightly desaturated to fit the medical context.

### Type

- **Display + body**: `Source Sans 3` (free, Google Fonts) — Adobe-designed for on-screen reading; tall x-height, open apertures, very legible at small sizes. Picked specifically for clarity in a medical context.
- **Mono**: `JetBrains Mono` for clinical data, vitals, dosages, and ASCII section markers ("S1, S2 without murmur" reads like code).
- **Optional readable variant**: `Lexend` is loaded as `--font-readable` for any long-form copy where extra readability matters (it widens letter-spacing and rounds shapes for easier scanning).
- Type scale is generous: 13 / 15 / 17 / 19 / 22 / 26 / 32 / 40px. Body is 17px (not 16) for medical contexts where readers may be older or stressed. No font weights heavier than 700.
- Letterspacing: tight on display (-0.01em), normal on body, +0.06em on the small uppercase eyebrows.

> **Substitution flag for the user:** No font files shipped with the codebase. We're using **Source Sans 3** and **JetBrains Mono** from Google Fonts as our defaults (with **Lexend** available as the high-readability fallback). If you have a brand-licensed font set, drop the `.woff2` files in `fonts/` and we'll wire them up.

### Spacing & rhythm

- 4-pt grid: `4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 56 / 80`.
- Card inner padding: `16–24px`. Card-to-card gap: `12–16px`.
- Section vertical rhythm: `40–56px` between major sections.

### Backgrounds

- **No gradients.** No mesh blobs. The product is a clinic, not a music app.
- **No full-bleed photography.** The codebase has zero imagery — we keep it that way.
- **No textures or patterns.** Surfaces are flat slate-50 / white.
- Dividers do the work that gradients would: 1px `#e2e8f0` hairlines, never thicker.

### Borders & radii

- Card radius: `8px` (the value in `app.py`).
- Pill radius: `999px` (full).
- Button radius: `6px`.
- Border weight: `1px`. Borders are slate-200 (`#e2e8f0`). The disclaimer uses a 4px **left rail** in amber-500 — that pattern is reserved exclusively for warnings.

### Shadows & elevation

Three-step elevation scale. No glow.

- `shadow-sm` — `0 1px 2px rgba(15, 23, 42, 0.04)`. Default for cards.
- `shadow-md` — `0 4px 12px rgba(15, 23, 42, 0.06)`. Hover, dropdowns.
- `shadow-lg` — `0 12px 28px rgba(15, 23, 42, 0.08)`. Modals, the focused chat composer.
- Inner shadow: `inset 0 1px 0 rgba(255,255,255,0.5)` on filled buttons for a clinical "embossed" feel — used sparingly.

### Hover & press states

- **Hover (text/links):** color shifts from `--accent` (teal-700) to `--accent-hover` (teal-800, `#115e59`). No underline appearing/disappearing — accessibility prefers stable affordances.
- **Hover (cards):** border darkens slate-200 → slate-300, shadow steps from `sm` → `md`. No transform.
- **Hover (buttons primary):** background teal-700 → teal-800. Cursor pointer.
- **Press:** background drops one more step (teal-900 `#134e4a`), transform `translateY(1px)`. No "shrink to 0.95" — feels toy-like.
- **Focus ring:** `0 0 0 3px rgba(15, 118, 110, 0.2)` — teal-500 at 20%. Always visible on keyboard focus.

### Animation

Healthcare-cautious. **Fast, short, calm** — no bounce, no spring overshoot.

- Easing: `cubic-bezier(0.2, 0, 0, 1)` — a gentle ease-out.
- Durations: `120ms` (color/shadow), `200ms` (panels expanding), `400ms` (page-level transitions). Nothing slower.
- Streaming text in chat shows a single `▌` block-cursor (1ch wide) blinking at 1.2s — taken directly from the Streamlit implementation. No typewriter sound, no shimmer.
- Loading: simple "spinner + label" pairs ("Reading sample_70.txt…", "Identifying medications…"). The labels themselves carry information; the spinner is decoration.
- We do not use bounces, pop-ins, or staggered list reveals.

### Transparency & blur

- The disclaimer banner is fully opaque amber-100. We **don't** stack glass-blurred surfaces.
- The only blur in the system is `backdrop-filter: blur(6px)` on the modal scrim, and even that's optional.

### Layout rules

- Page max-width: `1280px`, centered.
- Two-column main layout: left column (extracted info) ratio `1`, right column (chat) ratio `1.3`. Mirror of `app.py`'s `st.columns([1, 1.3])`.
- Sidebar: `280px` fixed, never overlays content.
- Chat composer is **fixed to the bottom** of the chat column, with a fade-to-white "protection gradient" 24px tall above it so message text doesn't visually collide. This is the **only** place a gradient appears.

### Imagery treatment

If imagery is ever added (it isn't, currently): cool-toned, desaturated, no skin-bare medical photography, no stock-art doctors with stethoscopes. Diagrammatic illustrations only, in single-color teal line work.

### Iconography

See the **ICONOGRAPHY** section below.

---

## ICONOGRAPHY

The codebase ships **no icon system** — Streamlit handles its own affordances and the only glyphs in source are emoji used semantically (🩺 ⚠️ 📄 💬 🔍 ⚙️ 🔄).

For the design system we standardize on **[Lucide](https://lucide.dev)** — open-source, MIT, 1.5px stroke, rounded line caps, geometrically simple. It matches the calm-clinical posture and pairs well with Inter.

- **Stroke**: 1.5px, `currentColor`. Default size `20px`.
- **Linecap/linejoin**: round.
- **Filled icons** are not used. Stroke-only across the system.
- Loaded via CDN: `https://unpkg.com/lucide@latest/dist/umd/lucide.js` (or via `<img src="https://unpkg.com/lucide-static@latest/icons/<name>.svg">`).

> **Substitution flag for the user:** Lucide is a substitution — the source codebase has no icon set. If you'd prefer Phosphor, Heroicons, or a custom set, swap the CDN.

### Icon role mapping

| Role | Lucide name | Notes |
|---|---|---|
| Document upload | `upload-cloud` | Empty-state hero |
| Uploaded document | `file-text` | Replaces the 📄 emoji in higher-fidelity contexts |
| Medications | `pill` | Pill list eyebrow |
| Conditions | `activity` | Heart-rate-ish line |
| Symptoms | `thermometer` | |
| Evidence source | `search` | Replaces 🔍 |
| Chat | `message-square` | Replaces 💬 |
| Settings | `settings-2` | Replaces ⚙️ |
| Reset | `refresh-cw` | Replaces 🔄 |
| Disclaimer | `alert-triangle` | Replaces ⚠️ |
| Source link | `external-link` | "Open source ↗" |
| Open emergency | `siren` | Used only by emergency-guardrail UI |

### Emoji policy
The seven emoji listed in CONTENT FUNDAMENTALS are kept available for low-fidelity contexts (terminal logs, the existing Streamlit screen, README files). In hi-fi React components prefer the Lucide equivalent.

### Logo
No logo was provided. We synthesize a placeholder mark: a teal `+` cross inscribed in a rounded square, with the wordmark "MedNote" in Inter SemiBold. Files in `assets/`. **Flag**: replace with the brand's real mark when one exists.

---

## Index

Root files & folders:

- `README.md` — this file.
- `SKILL.md` — agent-skill manifest; lets this system be invoked as a Claude Skill.
- `colors_and_type.css` — CSS custom properties for the whole system (color, type, spacing, radius, shadow tokens + semantic helpers like `.h1`, `.body`, `.eyebrow`).
- `fonts/` — *empty placeholder*. Inter & JetBrains Mono load from Google Fonts; replace with self-hosted `.woff2` if needed.
- `assets/` — logos, sample document, placeholder illustrations.
- `preview/` — the cards rendered in the Design System tab.
- `ui_kits/mednote/` — high-fidelity React UI kit recreating the chatbot's screens.

UI kits:

- **mednote** (`ui_kits/mednote/`) — the only product surface. `index.html` is an interactive click-thru of upload → analysis → chat. Includes header, sidebar, document panel, entity pills, section cards, evidence list, chat composer, message bubbles.
