import { useState, useEffect, useRef } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi! Ask me about hostel rooms 😊" },
  ]);
  const [input, setInput] = useState("");
  const chatEndRef = useRef(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return; // 🚨 prevents duplicate

    setLoading(true);

    const userMessage = { role: "user", content: input };

    setMessages((prev) => [
      ...prev,
      userMessage,
      { role: "assistant", content: "Typing..." }
    ]);

    setInput("");

    try {
      const res = await fetch(
        `http://127.0.0.1:8000/chat?user_query=${encodeURIComponent(input)}`,
        { method: "POST" }
      );

      const data = await res.json();

      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content: data.response,
        };
        return updated;
      });

    } 
    catch {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content: "Server error 😢",
        };
        return updated;
        });
      }
    setLoading(false);
  };

  return (
    <div className="app">
      <div className="header">Hostel Assistant 🤖</div>

      <div className="chat-container">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message-row ${
              msg.role === "user" ? "user" : "bot"
            }`}
          >
            {msg.role === "assistant" && (
              <div className="avatar">🤖</div>
            )}

            <div className={`message ${msg.role === "user" ? "user" : "bot"}`}>
              {msg.content.split("\n").map((line, i) => (
              <div key={i}>{line}</div>
              ))}
            </div>

            {msg.role === "user" && (
              <div className="avatar user">👤</div>
            )}
          </div>
        ))}
        <div ref={chatEndRef}></div>
      </div>

      <div className="input-box">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about rooms..."
          onKeyDown={(e) => {
            if (e.key === "Enter" && !loading) {
              e.preventDefault(); // 🚨 prevents double fire
              sendMessage();
            }
            }}/>
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default App;