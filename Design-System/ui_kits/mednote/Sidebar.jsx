/* @jsx React.createElement */
const { useState } = React;

const teal = "#0f766e";

window.Sidebar = function Sidebar({ onClear, model, setModel, evidenceMax, setEvidenceMax }) {
  return (
    <aside style={{
      width: 280, flex: "none", borderRight: "1px solid #e2e8f0",
      background: "#f8fafc", padding: "20px 18px", boxSizing: "border-box",
      display: "flex", flexDirection: "column", gap: 18, minHeight: "100%",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{ width: 36, height: 36, borderRadius: 10, background: teal, position: "relative", boxShadow: "0 4px 12px rgba(15,118,110,0.25)" }}>
          <div style={{ position: "absolute", top: 10, left: 16, width: 4, height: 16, background: "#fff", borderRadius: 2 }} />
          <div style={{ position: "absolute", top: 16, left: 10, width: 16, height: 4, background: "#fff", borderRadius: 2 }} />
        </div>
        <div style={{ fontWeight: 600, fontSize: 18, letterSpacing: "-0.3px", color: "#0f172a" }}>
          Med<span style={{ color: teal }}>Note</span>
        </div>
      </div>

      <div>
        <div style={{ fontSize: 11, fontWeight: 600, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 10 }}>
          Settings
        </div>
        <label style={fieldLabel}>Ollama model</label>
        <input style={inputStyle} value={model} onChange={e => setModel(e.target.value)} />
        <label style={{ ...fieldLabel, marginTop: 12 }}>
          Web evidence — max terms <span style={{ color: teal, fontWeight: 600 }}>{evidenceMax}</span>
        </label>
        <input type="range" min="0" max="10" value={evidenceMax}
          onChange={e => setEvidenceMax(+e.target.value)}
          style={{ width: "100%", accentColor: teal }} />
      </div>

      <button onClick={onClear} style={ghostBtn}>↻ Clear session</button>

      <div style={{ marginTop: "auto", fontSize: 12, color: "#64748b", lineHeight: 1.5 }}>
        Sources: <strong>MedlinePlus</strong> · <strong>Wikipedia</strong> · <strong>DuckDuckGo</strong>. No external API keys. Document text never leaves your machine.
      </div>
    </aside>
  );
};

const fieldLabel = {
  display: "block", fontSize: 11, fontWeight: 600, color: "#475569",
  textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 6,
};
const inputStyle = {
  width: "100%", boxSizing: "border-box", padding: "8px 10px",
  border: "1px solid #cbd5e1", borderRadius: 6, fontSize: 13,
  fontFamily: "inherit", color: "#0f172a", background: "#fff",
};
const ghostBtn = {
  background: "#fff", border: "1px solid #cbd5e1", color: "#0f766e",
  borderRadius: 6, padding: "8px 12px", fontSize: 13, fontWeight: 500,
  fontFamily: "inherit", cursor: "pointer", textAlign: "left",
};
