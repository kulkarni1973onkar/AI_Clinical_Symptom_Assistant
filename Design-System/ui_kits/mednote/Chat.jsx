/* @jsx React.createElement */
const { useState, useRef, useEffect } = React;
const tealC = "#0f766e";

window.ChatPanel = function ChatPanel({ messages, onSend, streaming }) {
  const [draft, setDraft] = useState("");
  const scrollRef = useRef(null);
  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, streaming]);

  const submit = () => {
    if (!draft.trim()) return;
    onSend(draft.trim());
    setDraft("");
  };

  return (
    <div style={{
      flex: 1, display: "flex", flexDirection: "column",
      background: "#fff", border: "1px solid #e2e8f0",
      borderRadius: 8, overflow: "hidden", minHeight: 0,
    }}>
      <div style={{
        padding: "14px 18px", borderBottom: "1px solid #e2e8f0",
        display: "flex", alignItems: "center", gap: 8,
      }}>
        <span style={{ fontSize: 16 }}>💬</span>
        <strong style={{ fontSize: 15, color: "#0f172a" }}>Chat</strong>
        <span style={{ fontSize: 12, color: "#64748b", marginLeft: "auto" }}>
          Ask follow-ups about your document
        </span>
      </div>

      <div ref={scrollRef} style={{ flex: 1, overflowY: "auto", padding: "16px 18px", minHeight: 0 }}>
        {messages.map((m, i) => (
          <ChatBubble key={i} role={m.role} content={m.content}
            streaming={streaming && i === messages.length - 1 && m.role === "assistant"} />
        ))}
        {messages.length === 0 && (
          <div style={{ color: "#94a3b8", fontSize: 13, padding: "20px 0", lineHeight: 1.6 }}>
            Examples:<br/>
            · What does Altace do?<br/>
            · Why might my BP be 150/60?<br/>
            · Should I be worried about any of this?
          </div>
        )}
      </div>

      <div style={{ borderTop: "1px solid #e2e8f0", padding: 12, background: "#fff" }}>
        <div style={{
          display: "flex", gap: 8, alignItems: "flex-end",
          border: "1px solid #cbd5e1", borderRadius: 8, padding: 6,
          background: "#fff", transition: "all 120ms",
        }}>
          <textarea
            rows={2}
            value={draft}
            onChange={e => setDraft(e.target.value)}
            onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); } }}
            placeholder="Ask a question about your document…"
            style={{
              flex: 1, border: 0, outline: 0, resize: "none",
              fontFamily: "inherit", fontSize: 14, lineHeight: 1.5,
              padding: "6px 8px", background: "transparent", color: "#0f172a",
            }}
          />
          <button onClick={submit} style={{
            background: tealC, color: "#fff", border: 0, borderRadius: 6,
            padding: "8px 16px", fontFamily: "inherit", fontSize: 13,
            fontWeight: 500, cursor: "pointer", boxShadow: "inset 0 1px 0 rgba(255,255,255,0.5)",
          }}>Send</button>
        </div>
      </div>
    </div>
  );
};

function ChatBubble({ role, content, streaming }) {
  const isUser = role === "user";
  return (
    <div style={{ display: "flex", gap: 10, marginBottom: 12, alignItems: "flex-start" }}>
      <div style={{
        width: 28, height: 28, borderRadius: 6, flex: "none",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 13, fontWeight: 600,
        background: isUser ? "#e2e8f0" : tealC,
        color: isUser ? "#334155" : "#fff",
      }}>{isUser ? "JP" : "🩺"}</div>
      <div style={{
        background: isUser ? tealC : "#f8fafc",
        color: isUser ? "#fff" : "#334155",
        border: isUser ? "1px solid " + tealC : "1px solid #e2e8f0",
        borderRadius: 8, padding: "10px 14px", fontSize: 14,
        lineHeight: 1.6, maxWidth: 560, whiteSpace: "pre-wrap",
      }}>
        {content}
        {streaming && (
          <span style={{
            display: "inline-block", width: 8, height: 14, background: tealC,
            verticalAlign: "-2px", marginLeft: 1, animation: "bblink 1.2s steps(2) infinite",
          }} />
        )}
      </div>
    </div>
  );
}
