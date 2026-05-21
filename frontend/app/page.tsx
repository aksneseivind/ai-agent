"use client";

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL!;

export default function Home() {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  async function sendMessage() {
    if (!message.trim()) return;

    const userMessage = message;
    setMessage("");
    setChat((prev) => [...prev, "You: " + userMessage]);
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage }),
      });

      const data = await res.json();

      setChat((prev) => [...prev, "AI: " + data.reply]);
    } catch {
      setChat((prev) => [...prev, "AI: Error contacting backend"]);
    }

    setLoading(false);
  }

  return (
    <main className="min-h-screen p-10 bg-black text-white">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">AI Agent</h1>

        <div className="h-[500px] overflow-y-auto border p-4 rounded">
          {chat.map((c, i) => (
            <div key={i} className="mb-2">{c}</div>
          ))}
          {loading && <div>AI skriver...</div>}
        </div>

        <div className="flex gap-2 mt-4">
          <input
            className="flex-1 p-2 text-black"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />

          <button
            onClick={sendMessage}
            className="px-4 bg-white text-black"
          >
            Send
          </button>
        </div>
      </div>
    </main>
  );
}