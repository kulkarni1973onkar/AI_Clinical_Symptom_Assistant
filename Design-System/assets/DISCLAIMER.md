# Medical Disclaimer

**This software is for educational and informational purposes only.**

## It is not medical advice

The Medical Note Assistant uses local large language models and public medical
information sources (MedlinePlus, Wikipedia, DuckDuckGo) to help users
understand the contents of clinical notes and prescriptions. The output is
**not a diagnosis, treatment plan, or prescription**, and it does not
substitute for the professional judgment of a licensed healthcare provider.

## What you should do

- **Always consult a qualified healthcare provider** (physician, pharmacist,
  nurse practitioner, etc.) for any medical question or decision.
- **Do not start, stop, or change a medication** based on the output of this
  tool.
- **In case of a medical emergency**, call your local emergency number
  (e.g., 911 in the US, 112 in the EU, 999 in the UK) immediately.

## Privacy

This application processes documents locally on your machine. The Ollama
language model runs locally and does not transmit your data. However, the
**evidence-retrieval step** sends *the names of medications and conditions*
extracted from your document to public medical-information services
(MedlinePlus, Wikipedia, DuckDuckGo) to fetch background information.

If your documents contain sensitive identifying information, consider
redacting it before uploading, or disabling the web-evidence step in the
sidebar (set "max entities to research" to 0).

## Limitations

- LLMs can produce confident-sounding but incorrect answers ("hallucinations").
- The entity extractor uses a fixed keyword list; it will miss terms that
  aren't on that list and may produce false positives for terms that share
  spellings with non-medical words.
- The SecTag section extractor depends on standard clinical-note headers; it
  may fail on free-form documents.
- Evidence retrieval depends on third-party services that may be rate-limited
  or unavailable.

## No warranty

This software is provided "as is" without warranty of any kind, express or
implied, including but not limited to the warranties of merchantability,
fitness for a particular purpose, and noninfringement.
