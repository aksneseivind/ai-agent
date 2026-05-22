import { useState } from "react";

const API =
  import.meta.env.VITE_API_URL ||
  "https://ai-agent-lvvc.onrender.com";

export default function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  // ----------------------------
  // UPLOAD PDF
  // ----------------------------
  const uploadPDF = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      await fetch(`${API}/upload`, {
        method: "POST",
        body: formData,
      });

      alert("PDF uploaded ✔");
    } catch (err) {
      alert("Upload failed");
      console.error(err);
    }
  };

  // ----------------------------
  // CHAT
  // ----------------------------
  const askQuestion = async () => {
    if (!question) return;

    const userMsg = { role: "user", text: question };
    setMessages((p) => [...p, userMsg]);

    setLoading(true);

    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();

      const botMsg = {
        role: "bot",
        text: data.answer || "No response",
      };

      setMessages((p) => [...p, botMsg]);
    } catch (err) {
      setMessages((p) => [
        ...p,
        {
          role: "bot",
          text: "Error contacting server",
        },
      ]);
    }

    setLoading(false);
    setQuestion("");
  };

  // ----------------------------
  // UI
  // ----------------------------
  return (
    <div style={styles.bg}>
      <div style={styles.shell}>
        {/* SIDEBAR */}
        <div style={styles.sidebar}>
          <div style={styles.logo}>AI Agent</div>

          <div style={styles.card}>
            <div style={styles.label}>Upload document</div>
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
            />
            <button onClick={uploadPDF} style={styles.button}>
              Upload PDF
            </button>
          </div>

          <div style={styles.hint}>
            Ask questions about your document
          </div>
        </div>

        {/* CHAT */}
        <div style={styles.main}>
          <div style={styles.topbar}>
            Document Intelligence Chat
          </div>

          <div style={styles.chat}>
            {messages.length === 0 && (
              <div style={styles.empty}>
                Upload a document and start asking questions
              </div>
            )}

            {messages.map((m, i) => (
              <div
                key={i}
                style={{
                  ...styles.msg,
                  alignSelf:
                    m.role === "user" ? "flex-end" : "flex-start",
                  background:
                    m.role === "user"
                      ? "linear-gradient(135deg,#3b82f6,#2563eb)"
                      : "rgba(255,255,255,0.9)",
                  color:
                    m.role === "user" ? "white" : "#111827",
                }}
              >
                {m.text}
              </div>
            ))}

            {loading && (
              <div style={styles.typing}>AI is thinking…</div>
            )}
          </div>

          {/* INPUT */}
          <div style={styles.inputBar}>
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask your document..."
              style={styles.chatInput}
            />
            <button onClick={askQuestion} style={styles.send}>
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ----------------------------
// STYLES (RESTORED UI)
// ----------------------------
const styles = {
  bg: {
    height: "100vh",
    background: "radial-gradient(circle at top, #eef2ff, #f8fafc)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    fontFamily: "Inter, Arial",
  },

  shell: {
    width: "95%",
    height: "92vh",
    display: "flex",
    borderRadius: 20,
    overflow: "hidden",
    boxShadow: "0 20px 60px rgba(0,0,0,0.1)",
    background: "white",
  },

  sidebar: {
    width: 300,
    padding: 20,
    background: "linear-gradient(180deg, #ffffff, #f9fafb)",
    borderRight: "1px solid #e5e7eb",
  },

  logo: {
    fontSize: 22,
    fontWeight: 700,
    marginBottom: 20,
  },

  card: {
    padding: 12,
    borderRadius: 12,
    background: "white",
    border: "1px solid #e5e7eb",
    marginBottom: 12,
  },

  label: {
    fontSize: 12,
    color: "#6b7280",
    marginBottom: 6,
  },

  button: {
    marginTop: 10,
    width: "100%",
    padding: 10,
    borderRadius: 10,
    border: "none",
    background: "#111827",
    color: "white",
    cursor: "pointer",
  },

  hint: {
    marginTop: 20,
    fontSize: 12,
    color: "#9ca3af",
  },

  main: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
  },

  topbar: {
    padding: 16,
    fontWeight: 600,
    borderBottom: "1px solid #e5e7eb",
    background: "rgba(255,255,255,0.8)",
    backdropFilter: "blur(10px)",
  },

  chat: {
    flex: 1,
    padding: 20,
    display: "flex",
    flexDirection: "column",
    gap: 12,
    overflowY: "auto",
  },

  msg: {
    padding: 14,
    borderRadius: 16,
    maxWidth: "65%",
    fontSize: 14,
    boxShadow: "0 6px 20px rgba(0,0,0,0.05)",
  },

  empty: {
    marginTop: 40,
    textAlign: "center",
    color: "#9ca3af",
  },

  typing: {
    fontSize: 12,
    color: "#6b7280",
  },

  inputBar: {
    display: "flex",
    padding: 14,
    borderTop: "1px solid #e5e7eb",
    background: "rgba(255,255,255,0.8)",
  },

  chatInput: {
    flex: 1,
    padding: 12,
    borderRadius: 12,
    border: "1px solid #e5e7eb",
  },

  send: {
    marginLeft: 10,
    padding: "12px 18px",
    borderRadius: 12,
    border: "none",
    background: "linear-gradient(135deg,#3b82f6,#2563eb)",
    color: "white",
    cursor: "pointer",
  },
};