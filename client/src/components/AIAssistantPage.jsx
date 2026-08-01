import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { aiService } from "../api/aiService";
import { plotService, getProfile } from "../api/plotService";
import { Mic, MicOff, Send, ArrowLeft, Volume2, VolumeX, Sparkles, RefreshCw } from "lucide-react";
import ReactMarkdown from "react-markdown";

export default function AIAssistantPage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [plots, setPlots] = useState([]);
  const [selectedPlotId, setSelectedPlotId] = useState("");
  
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState("ta"); // ta or en
  const [speakingMessageId, setSpeakingMessageId] = useState(null);

  const recognitionRef = useRef(null);
  const synthRef = useRef(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      synthRef.current = window.speechSynthesis;
    }
    
    const loadData = async () => {
      try {
        const profRes = await getProfile();
        setProfile(profRes.data);
        const langCode = profRes.data.language === "Tamil" ? "ta" : "en";
        setLanguage(langCode);
        
        const listPlots = await plotService.getPlots();
        setPlots(listPlots);

        if (listPlots.length > 0) {
          setSelectedPlotId(listPlots[0].id);
        } else {
          // If no plots, trigger general brief load directly
          loadChatForPlot("");
        }
      } catch (err) {
        console.error("Assistant data load failure", err);
      }
    };
    loadData();
  }, []);

  const loadChatForPlot = async (plotId) => {
    setLoading(true);
    try {
      const history = await aiService.getChatHistory(plotId);
      if (history && history.length > 0) {
        const formatted = history.map((msg) => ({
          id: msg.id.toString(),
          sender: msg.sender,
          text: msg.message_text,
          timestamp: new Date(msg.created_at),
        }));
        setMessages(formatted);
      } else {
        setMessages([]);
      }
    } catch (err) {
      console.error("Error loading chat history:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (profile) {
      loadChatForPlot(selectedPlotId);
    }
  }, [selectedPlotId, profile]);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, loading]);

  const initSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Voice speech recognition is not supported in this browser. Please type your query instead.");
      return null;
    }

    const rec = new SpeechRecognition();
    rec.continuous = false; // Stop after one question sentence
    rec.interimResults = false;
    rec.lang = language === "ta" ? "ta-IN" : "en-IN";

    rec.onresult = (event) => {
      const resultText = event.results[0][0].transcript;
      if (resultText) {
        setInputText(resultText);
      }
    };

    rec.onerror = (e) => {
      console.error("Speech recognition error", e);
      setIsRecording(false);
    };

    rec.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current = rec;
    return rec;
  };

  const toggleRecording = () => {
    if (isRecording) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsRecording(false);
    } else {
      const rec = recognitionRef.current || initSpeechRecognition();
      if (rec) {
        rec.lang = language === "ta" ? "ta-IN" : "en-IN";
        rec.start();
        setIsRecording(true);
      }
    }
  };

  const handleSend = async (e) => {
    if (e) e.preventDefault();
    if (!inputText.trim()) return;

    const userMessage = {
      id: crypto.randomUUID(),
      sender: "user",
      text: inputText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const queryText = inputText;
    setInputText("");
    setLoading(true);

    try {
      const response = await aiService.askAI(queryText, selectedPlotId || null);
      const aiMessage = {
        id: crypto.randomUUID(),
        sender: "ai",
        text: response.response,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          sender: "ai",
          text: language === "ta" 
            ? "சேவையகத்திலிருந்து விடையைப் பெறுவதில் சிக்கல் ஏற்பட்டுள்ளது. மீண்டும் முயலவும்." 
            : "Sorry, I am having trouble connecting to the model engine. Please check again in a moment.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const speakText = (msgId, text) => {
    if (!synthRef.current) return;

    if (speakingMessageId === msgId) {
      synthRef.current.cancel();
      setSpeakingMessageId(null);
      return;
    }

    synthRef.current.cancel(); // Stop any current speaking
    
    // Split clean text to read (e.g. remove markdown bullet stars)
    const cleanText = text.replace(/[*#_`]/g, "");

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = language === "ta" ? "ta-IN" : "en-IN";
    
    // Try to find a matched voice on the device
    const voices = synthRef.current.getVoices();
    const matchingVoice = voices.find((v) => v.lang.startsWith(language === "ta" ? "ta" : "en"));
    if (matchingVoice) {
      utterance.voice = matchingVoice;
    }

    utterance.onend = () => {
      setSpeakingMessageId(null);
    };
    
    utterance.onerror = () => {
      setSpeakingMessageId(null);
    };

    setSpeakingMessageId(msgId);
    synthRef.current.speak(utterance);
  };

  const isTamil = language === "ta";

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto", padding: "20px", height: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Top Header */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px", borderBottom: "2px solid var(--border-soil)", paddingBottom: "16px" }}>
        <button onClick={() => navigate("/dashboard")} style={{ background: "none", border: "none", display: "flex", alignItems: "center", color: "var(--text-muted)", cursor: "pointer" }}>
          <ArrowLeft size={24} />
        </button>
        <div style={{ flex: 1 }}>
          <h1 style={{ margin: 0, fontSize: "1.5rem", color: "var(--paddy-green)", display: "flex", alignItems: "center", gap: "6px" }}>
            <Sparkles size={20} style={{ color: "var(--clay-red)" }} />
            {isTamil ? "விவசாய ஆலோசனைக் கூடம்" : "AgriTwin Advisor"}
          </h1>
        </div>
        <select value={language} onChange={(e) => setLanguage(e.target.value)} style={{ padding: "6px 10px", fontSize: "0.85rem" }}>
          <option value="ta">தமிழ்</option>
          <option value="en">English</option>
        </select>
      </div>

      {/* Selector bar for current plot context */}
      <div style={{ padding: "10px 0", borderBottom: "1px solid var(--border-soil)", display: "flex", alignItems: "center", justifyStyle: "space-between", gap: "12px" }}>
        <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontWeight: "600" }}>
          {isTamil ? "நிலத்தின் விபரம்:" : "Active Plot:"}
        </span>
        <select 
          value={selectedPlotId} 
          onChange={(e) => setSelectedPlotId(e.target.value)} 
          style={{ flex: 1, padding: "6px", fontSize: "0.85rem", backgroundColor: "white" }}
        >
          <option value="">{isTamil ? "-- பொதுவான பரிந்துரைகள் --" : "-- General Advice --"}</option>
          {plots.map((p) => (
            <option key={p.id} value={p.id}>{p.plot_name} ({p.area_acres.toFixed(1)} ac)</option>
          ))}
        </select>
      </div>

      {/* Messages Thread */}
      <div style={{ flex: 1, overflowY: "auto", padding: "16px 0", display: "flex", flexDirection: "column", gap: "16px" }}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
              maxWidth: "85%",
              background: msg.sender === "user" ? "var(--paddy-green)" : "white",
              color: msg.sender === "user" ? "white" : "var(--text-main)",
              borderRadius: "8px",
              border: msg.sender === "user" ? "none" : "1px solid var(--border-soil)",
              padding: "12px 16px",
              position: "relative"
            }}
          >
            {/* Header with Read Aloud toggle for AI responses */}
            {msg.sender === "ai" && (
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px", borderBottom: "1px solid #e2e8f0", paddingBottom: "4px" }}>
                <span style={{ fontSize: "0.75rem", color: "var(--clay-red)", fontWeight: "700" }}>AI Recommendation</span>
                <button
                  onClick={() => speakText(msg.id, msg.text)}
                  style={{
                    background: "none",
                    border: "none",
                    color: speakingMessageId === msg.id ? "var(--clay-red)" : "var(--text-muted)",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "4px",
                    padding: "2px"
                  }}
                >
                  {speakingMessageId === msg.id ? <VolumeX size={14} /> : <Volume2 size={14} />}
                  <span style={{ fontSize: "0.7rem", fontWeight: "700" }}>
                    {speakingMessageId === msg.id ? (isTamil ? "நிறுத்து" : "Stop") : (isTamil ? "கேட்க" : "Listen")}
                  </span>
                </button>
              </div>
            )}
            
            <div style={{ margin: 0, fontSize: "0.95rem", lineHeight: "1.5" }}>
              <ReactMarkdown>{msg.text}</ReactMarkdown>
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ alignSelf: "flex-start", background: "white", border: "1px solid var(--border-soil)", borderRadius: "8px", padding: "12px 16px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--text-muted)" }}>
              <RefreshCw className="spin" size={16} />
              <span style={{ fontSize: "0.85rem", fontStyle: "italic" }}>
                {isTamil ? "விவசாய உதவியாளர் பதிலளிக்கிறார்..." : "Consulting AgriTwin engine..."}
              </span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input panel */}
      <form onSubmit={handleSend} style={{ display: "flex", gap: "12px", borderTop: "1px solid var(--border-soil)", paddingTop: "16px", paddingBottom: "12px" }}>
        <button
          type="button"
          onClick={toggleRecording}
          style={{
            padding: "12px",
            borderRadius: "6px",
            border: isRecording ? "1.5px solid var(--clay-red)" : "1px solid var(--border-soil)",
            backgroundColor: isRecording ? "rgba(162, 61, 29, 0.08)" : "#fcfbfa",
            color: isRecording ? "var(--clay-red)" : "var(--paddy-green)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer"
          }}
        >
          {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
        </button>

        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder={isRecording 
            ? (isTamil ? "பேசவும்..." : "Listening...") 
            : (isTamil ? "உர உர அளவு, பாசன விபரம் கேட்க..." : "Ask about fertilizers, crop advisory...")}
          style={{
            flex: 1,
            padding: "12px",
            border: "1.5px solid var(--border-soil)",
            borderRadius: "6px",
            fontSize: "0.95rem"
          }}
          disabled={isRecording}
        />

        <button
          type="submit"
          disabled={!inputText.trim() || loading}
          style={{
            padding: "12px 18px",
            backgroundColor: "var(--paddy-green)",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center"
          }}
        >
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}
