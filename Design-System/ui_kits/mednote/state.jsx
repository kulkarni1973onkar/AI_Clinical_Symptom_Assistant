/* @jsx React.createElement */
const { useState } = React;

const SAMPLE_DOC = {
  name: "sample_70.txt",
  size: "2.3 KB",
  sections: [
    { title: "Chief complaint", body: "Followup on hypertension and hypercholesterolemia." },
    { title: "Subjective", body: "78-year-old male, knee replacement and back surgery in past year. Denies chest pain, heaviness, tightness, pressure, shortness of breath (with stairs only), cough, or palpitations. Known Crohn's, sees Dr. Ferguson. Nonsmoker. Denies ankle swelling." },
    { title: "Vitals", body: "Wt: 172 lbs (+2) · B/P: 150/60 · T: 96.4°F · P: 72 / regular" },
    { title: "Impression", body: "1. Hypertension. 2. Hypercholesterolemia. 3. Osteoarthritis. 4. Fatigue." },
    { title: "Plan", body: "Check BMP, lipid, liver profile, CPK, CBC. Refill medications x 3 months. Increase Altace to 5 mg/day for better blood pressure control. Diet, exercise, weight loss. Follow up in 3 months and prn." },
  ],
  meds: ["altace"],
  conds: ["hypertension", "hypercholesterolemia", "osteoarthritis", "crohn's"],
  syms: ["fatigue", "denies chest pain", "denies cough", "denies palpitations"],
  evidence: [
    { term: "altace", source: "MedlinePlus", snippet: "Ramipril (Altace) is in a class of medications called ACE inhibitors. It works by decreasing certain natural substances that tighten the blood vessels.", url: "#" },
    { term: "hypertension", source: "Wikipedia", snippet: "Hypertension, also known as high blood pressure, is a long-term medical condition in which the blood pressure in the arteries is persistently elevated.", url: "#" },
    { term: "osteoarthritis", source: "MedlinePlus", snippet: "Osteoarthritis is the most common form of arthritis. It causes pain, swelling, and reduced motion in your joints, often in the hands, knees, and hips.", url: "#" },
  ],
  initialAnalysis:
`**Summary**
Your document is a routine follow-up note for a 78-year-old man with high blood pressure and high cholesterol. He is doing well overall after recent knee and back surgery and denies most warning symptoms.

**Medications**
· **Altace (ramipril)** — per MedlinePlus, this is an ACE inhibitor used to lower blood pressure. The plan increases your dose to 5 mg/day.

**Conditions**
· **Hypertension** (high blood pressure) — Wikipedia notes this is a long-term elevation in arterial pressure.
· **Hypercholesterolemia** — high cholesterol; the plan checks a lipid panel.
· **Osteoarthritis** — joint wear; consistent with the recent knee replacement.

**Notable symptoms**
· Reports: fatigue
· Denies: chest pain, cough, palpitations, ankle swelling

**Questions you might ask your doctor**
1. Is a B/P of 150/60 still high enough to need a higher Altace dose, or could the wide pulse pressure mean something else?
2. Should I track my fatigue between visits — what changes would be worth a call?
3. With Crohn's plus the new lipid plan, are there any medication interactions to watch?

*This is informational and not medical advice — please discuss with your doctor.*`,
};

window.useChatbot = function useChatbot() {
  const [doc, setDoc] = useState(null);
  const [messages, setMessages] = useState([]);
  const [streaming, setStreaming] = useState(false);
  const [model, setModel] = useState("llama3.2");
  const [evidenceMax, setEvidenceMax] = useState(5);

  const loadSample = () => {
    setDoc(SAMPLE_DOC);
    setMessages([{ role: "assistant", content: SAMPLE_DOC.initialAnalysis }]);
  };
  const clear = () => { setDoc(null); setMessages([]); };

  const send = (q) => {
    setMessages(m => [...m, { role: "user", content: q }, { role: "assistant", content: "" }]);
    setStreaming(true);
    const reply = fakeReply(q);
    let i = 0;
    const tick = () => {
      i += Math.max(2, Math.floor(Math.random() * 5));
      setMessages(m => {
        const copy = m.slice();
        copy[copy.length - 1] = { role: "assistant", content: reply.slice(0, i) };
        return copy;
      });
      if (i < reply.length) setTimeout(tick, 28);
      else setStreaming(false);
    };
    setTimeout(tick, 200);
  };

  return { doc, messages, streaming, model, setModel, evidenceMax, setEvidenceMax, loadSample, clear, send };
};

function fakeReply(q) {
  const lower = q.toLowerCase();
  if (lower.includes("altace") || lower.includes("ramipril"))
    return "Altace is the brand name for ramipril, an ACE inhibitor. Per MedlinePlus, it works by relaxing blood vessels so blood flows more easily — which lowers your blood pressure.\n\nIn your document, the plan is to increase Altace to 5 mg/day for better blood-pressure control.\n\n*This is informational and not medical advice.*";
  if (lower.includes("bp") || lower.includes("blood pressure") || lower.includes("150"))
    return "Your reading was 150/60. The top number (systolic) of 150 is above the typical target of <130 — which is why your doctor increased your Altace.\n\nThe wide gap between 150 and 60 (a wide pulse pressure) can be normal in older adults but is worth asking about.\n\n*Please discuss specifics with your doctor — this is informational only.*";
  return "Based on the document, I can speak to what's there: hypertension, hypercholesterolemia, osteoarthritis, and Altace. If your question is outside that, I'll answer generally and flag it.\n\n*This is informational and not medical advice.*";
}
