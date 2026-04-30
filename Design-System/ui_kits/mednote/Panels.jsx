/* @jsx React.createElement */
const teal = "#0f766e";

window.Disclaimer = function Disclaimer() {
  return (
    <div style={{
      background: "#fef3c7", borderLeft: "4px solid #f59e0b",
      padding: "12px 16px", borderRadius: 6, fontSize: 14,
      lineHeight: 1.55, color: "#451a03", marginBottom: 18,
    }}>
      <strong style={{ color: "#78350f" }}>⚠ Not medical advice.</strong>{" "}
      This tool is for educational and informational purposes only. It does not diagnose, prescribe, or replace professional medical care. Always consult a qualified healthcare provider.
    </div>
  );
};

window.Uploader = function Uploader({ onPickSample }) {
  return (
    <div style={{
      border: "2px dashed #cbd5e1", borderRadius: 8, padding: "32px 24px",
      textAlign: "center", background: "#f8fafc", color: "#475569",
      transition: "all 200ms cubic-bezier(0.2,0,0,1)", cursor: "pointer",
    }}
      onMouseEnter={e => { e.currentTarget.style.borderColor = teal; e.currentTarget.style.background = "#f0fdfa"; }}
      onMouseLeave={e => { e.currentTarget.style.borderColor = "#cbd5e1"; e.currentTarget.style.background = "#f8fafc"; }}
      onClick={onPickSample}>
      <div style={{
        width: 44, height: 44, borderRadius: 10, background: "#ccfbf1",
        color: teal, display: "inline-flex", alignItems: "center",
        justifyContent: "center", marginBottom: 12, fontSize: 22,
      }}>⤴</div>
      <div style={{ margin: "0 0 6px", fontSize: 16, fontWeight: 600, color: "#0f172a" }}>
        Upload a clinical note or prescription
      </div>
      <div style={{ margin: 0, fontSize: 14, color: "#64748b" }}>
        Drop a file here, or <span style={{ color: teal, fontWeight: 500 }}>click to load the sample</span>
      </div>
      <div style={{ marginTop: 10, fontFamily: "JetBrains Mono, monospace", fontSize: 11, color: "#94a3b8" }}>
        .txt · .pdf · .png · .jpg — OCR'd automatically
      </div>
    </div>
  );
};

window.EntityPills = function EntityPills({ label, items, kind }) {
  if (!items || !items.length) return null;
  const palettes = {
    med:  { bg: "#ccfbf1", fg: "#0f766e" },
    cond: { bg: "#fef3c7", fg: "#78350f" },
    sym:  { bg: "#f1f5f9", fg: "#475569" },
  };
  const c = palettes[kind] || palettes.med;
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ fontSize: 13, fontWeight: 600, color: "#0f172a", marginBottom: 6 }}>{label}</div>
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
        {items.map(t => (
          <span key={t} style={{
            background: c.bg, color: c.fg, padding: "3px 11px",
            borderRadius: 999, fontSize: 13, fontWeight: 500,
          }}>{t}</span>
        ))}
      </div>
    </div>
  );
};

window.SectionCard = function SectionCard({ title, body }) {
  return (
    <div style={{
      background: "#f8fafc", border: "1px solid #e2e8f0",
      borderRadius: 8, padding: "12px 14px", marginBottom: 8,
    }}>
      <div style={{
        margin: "0 0 6px", color: teal, textTransform: "uppercase",
        fontSize: 11, letterSpacing: "0.06em", fontWeight: 600,
      }}>{title}</div>
      <div style={{ margin: 0, fontSize: 14, color: "#334155", lineHeight: 1.55 }}>{body}</div>
    </div>
  );
};

window.EvidenceItem = function EvidenceItem({ term, source, snippet, url }) {
  return (
    <div style={{
      border: "1px solid #e2e8f0", borderRadius: 8,
      padding: "12px 14px", marginBottom: 8, background: "#fff",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
        <span style={{ fontWeight: 600, fontSize: 14, color: "#0f172a" }}>{term}</span>
        <span style={{
          fontSize: 12, color: teal, background: "#ccfbf1",
          padding: "2px 8px", borderRadius: 999, fontWeight: 500,
        }}>{source}</span>
      </div>
      <div style={{ margin: "0 0 6px", fontSize: 13, color: "#475569", lineHeight: 1.5 }}>{snippet}</div>
      <a href={url} style={{ fontSize: 12, color: teal, textDecoration: "none", fontWeight: 500 }}>Open source ↗</a>
    </div>
  );
};
