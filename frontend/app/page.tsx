"use client";

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL!;

export default function Home() {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  async function uploadCV() {
    if (!file) return;

    setUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_URL}/upload-cv`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      setChat((prev) => [
        ...prev,
        `System: CV uploaded (${data.length} characters)`
      ]);
    } catch (err) {
      setChat((prev) => [...prev, "System: Upload failed"]);
    }

    setUploading(false);
  }

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
        <h1 className="text-3xl font-bold mb-6">AI CV Agent</h1>

        {/* UPLOAD SECTION */}
        <div className="mb-6 p-4 border rounded">
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />

          <button
            onClick={uploadCV}
            className="ml-3 px-4 py-1 bg-white text-black"
          >
            {uploading ? "Uploading..." : "Upload CV"}
          </button>
        </div>

        {/* CHAT */}
        <div className="h-[500px] overflow-y-auto border p-4 rounded">
          {chat.map((c, i) => (
            <div key={i} className="mb-2">{c}</div>
          ))}
          {loading && <div>AI skriver...</div>}
        </div>

        {/* INPUT */}
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