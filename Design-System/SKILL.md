---
name: mednote-design
description: Use this skill to generate well-branded interfaces and assets for MedNote (Medical Note Assistant), an AI clinical chatbot, either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

Read the README.md file within this skill, and explore the other available files.

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view. If working on production code, you can copy assets and read the rules here to become an expert in designing with this brand.

If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions, and act as an expert designer who outputs HTML artifacts _or_ production code, depending on the need.

## Quick reference

- **Brand color**: teal `#0f766e` (`--accent`)
- **Voice**: calm, second-person, plain language, never diagnostic. Always end with "informational, not medical advice."
- **Type**: Inter (sans), JetBrains Mono (data/vitals)
- **Icons**: Lucide, 1.5px stroke, currentColor
- **No gradients**, no full-bleed photography, no decorative emoji. Amber rail (`#fef3c7` / `#f59e0b`) is reserved for the disclaimer.

See `colors_and_type.css` for tokens, `ui_kits/mednote/` for components, `preview/` for visual specimens.
