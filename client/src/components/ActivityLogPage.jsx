import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { activityService } from "../api/activityService";
import { plotService, getProfile } from "../api/plotService";
import { Mic, MicOff, Save, Trash2, ArrowLeft, Cloud, CloudLightning } from "lucide-react";

export default function ActivityLogPage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [plots, setPlots] = useState([]);
  const [selectedPlotId, setSelectedPlotId] = useState("");
  
  const [inputText, setInputText] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [language, setLanguage] = useState("ta"); // ta or en
  const [pastLogs, setPastLogs] = useState([]);
  const [onlineStatus, setOnlineStatus] = useState(navigator.onLine);
  
  const recognitionRef = useRef(null);

  useEffect(() => {
    const handleOnline = () => setOnlineStatus(true);
    const handleOffline = () => setOnlineStatus(false);
    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const profRes = await getProfile();
        setProfile(profRes.data);
        setLanguage(profRes.data.language === "Tamil" ? "ta" : "en");
        
        const listPlots = await plotService.getPlots();
        setPlots(listPlots);
      } catch (err) {
        console.error("Unable to load details", err);
      }
      await loadLogs();
    };
    loadInitialData();
  }, []);

  const loadLogs = async () => {
    try {
      const logs = await activityService.getActivities();
      setPastLogs(logs);
    } catch (e) {
      console.error(e);
    }
  };

  const initSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Voice speech recognition is not supported in this browser. Please type your entry instead.");
      return null;
    }

    const rec = new SpeechRecognition();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = language === "ta" ? "ta-IN" : "en-IN";

    rec.onresult = (event) => {
      let finalTranscript = "";
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        }
      }
      if (finalTranscript) {
        setInputText((prev) => (prev ? prev + " " + finalTranscript : finalTranscript));
      }
    };

    rec.onerror = (e) => {
      console.error("Speech error", e);
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

  const handleSave = async () => {
    if (!inputText.trim()) {
      alert("Please record or type something first.");
      return;
    }

    const payload = {
      plot_id: selectedPlotId || null,
      entry_text: inputText,
      entry_language: language,
      input_mode: isRecording ? "voice" : "text",
    };

    try {
      await activityService.saveActivityLocally(payload);
      setInputText("");
      setSelectedPlotId("");
      await loadLogs();
      alert("Activity Log Saved Successfully!");
    } catch (e) {
      console.error(e);
      alert("Error saving log.");
    }
  };

  // Group logs by date
  const groupedLogs = pastLogs.reduce((acc, log) => {
    const dateStr = new Date(log.created_at).toLocaleDateString(undefined, {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
    if (!acc[dateStr]) acc[dateStr] = [];
    acc[dateStr].push(log);
    return acc;
  }, {});

  const getPlotName = (id) => {
    const plot = plots.find((p) => p.id === id);
    return plot ? plot.plot_name : "General Farm Work";
  };

  const isTamil = language === "ta";

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto", padding: "20px", minHeight: "100vh" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px", marginBottom: "24px", borderBottom: "2px solid var(--border-soil)", paddingBottom: "16px" }}>
        <button onClick={() => navigate("/dashboard")} style={{ background: "none", border: "none", display: "flex", alignItems: "center", color: "var(--text-muted)", cursor: "pointer" }}>
          <ArrowLeft size={24} />
        </button>
        <h1 style={{ margin: 0, fontSize: "1.75rem", color: "var(--paddy-green)" }}>
          {isTamil ? "தினசரி செயல்பாட்டுப் பதிவு" : "Daily Activity Log"}
        </h1>
      </div>

      {/* Control Card */}
      <div style={{ background: "white", border: "1px solid var(--border-soil)", borderRadius: "8px", padding: "24px", marginBottom: "32px" }}>
        <h2 style={{ fontSize: "1.1rem", marginBottom: "16px", color: "var(--text-main)" }}>
          {isTamil ? "இன்றைய வேலையை பதிவு செய்யவும்" : "Log What You Did Today"}
        </h2>

        {/* Language selector & Plot select */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "20px" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
            <label style={{ fontSize: "0.75rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-muted)" }}>
              {isTamil ? "மொழி" : "Log Language"}
            </label>
            <select value={language} onChange={(e) => setLanguage(e.target.value)} style={{ padding: "10px" }}>
              <option value="ta">தமிழ் (Tamil)</option>
              <option value="en">English</option>
            </select>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
            <label style={{ fontSize: "0.75rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-muted)" }}>
              {isTamil ? "நிலம் (விரும்பினால்)" : "Tag Mapped Plot"}
            </label>
            <select value={selectedPlotId} onChange={(e) => setSelectedPlotId(e.target.value)} style={{ padding: "10px" }}>
              <option value="">{isTamil ? "-- பொதுவான வேலை --" : "-- General / No Plot --"}</option>
              {plots.map((p) => (
                <option key={p.id} value={p.id}>{p.plot_name} ({p.area_acres.toFixed(1)} ac)</option>
              ))}
            </select>
          </div>
        </div>

        {/* Audio Recording Button */}
        <div style={{ textAlign: "center", marginBottom: "20px" }}>
          <button
            onClick={toggleRecording}
            style={{
              width: "80px",
              height: "80px",
              borderRadius: "50%",
              border: isRecording ? "3px solid var(--clay-red)" : "1px solid var(--border-soil)",
              backgroundColor: isRecording ? "rgba(162, 61, 29, 0.08)" : "#fcfbfa",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              color: isRecording ? "var(--clay-red)" : "var(--paddy-green)",
              outline: "none",
              animation: isRecording ? "pulse-record 1.5s infinite" : "none",
              boxShadow: "none"
            }}
          >
            {isRecording ? <MicOff size={32} /> : <Mic size={32} />}
          </button>
          <div style={{ fontSize: "0.85rem", color: isRecording ? "var(--clay-red)" : "var(--text-muted)", marginTop: "8px", fontWeight: "700" }}>
            {isRecording 
              ? (isTamil ? "ஒலிப்பதிவு செய்யப்படுகிறது... நிறுத்த கிளிக் செய்க" : "Recording Audio... Click to Stop") 
              : (isTamil ? "பேசி பதிவு செய்ய கிளிக் செய்க" : "Click to Speak & Record")}
          </div>
        </div>

        {/* Text Area display */}
        <div style={{ display: "flex", flexDirection: "column", gap: "6px", marginBottom: "20px" }}>
          <label style={{ fontSize: "0.75rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-muted)" }}>
            {isTamil ? "உரையாடல் / தட்டச்சு செய்ய வேண்டிய உரை" : "Transcription / Type Fallback"}
          </label>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={isTamil ? "விதைப்பு, நீர்ப்பாசனம் அல்லது உரமிடுதல் விபரங்களை இங்கே கூறவும் அல்லது தட்டச்சு செய்யவும்..." : "Describe sowing details, irrigation cycles, or fertilizing actions here..."}
            style={{
              width: "100%",
              height: "120px",
              padding: "12px",
              border: "1.5px solid var(--border-soil)",
              borderRadius: "6px",
              fontSize: "0.95rem",
              fontFamily: "var(--font-body)",
              resize: "none"
            }}
          />
        </div>

        {/* Save Button */}
        <button
          onClick={handleSave}
          style={{
            width: "100%",
            padding: "14px",
            backgroundColor: "var(--paddy-green)",
            color: "white",
            border: "none",
            borderRadius: "6px",
            fontSize: "1rem",
            fontWeight: "750",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
            boxShadow: "0 2px 4px rgba(27, 77, 44, 0.1)"
          }}
        >
          <Save size={18} />
          {isTamil ? "செயல்பாட்டை சேமிக்கவும்" : "Save Farm Activity"}
        </button>
      </div>

      {/* Timeline Section */}
      <h2 style={{ fontSize: "1.25rem", color: "var(--text-main)", marginBottom: "16px", borderBottom: "1px solid var(--border-soil)", paddingBottom: "8px" }}>
        {isTamil ? "கடந்த கால பதிவுகள்" : "Observation Timeline"}
      </h2>
      
      {Object.keys(groupedLogs).length === 0 ? (
        <div style={{ textAlign: "center", padding: "40px", color: "var(--text-muted)", fontStyle: "italic" }}>
          {isTamil ? "இன்னும் பதிவுகள் எதுவும் இல்லை." : "No logs saved yet. Record your daily farm updates!"}
        </div>
      ) : (
        Object.keys(groupedLogs).map((date) => (
          <div key={date} style={{ marginBottom: "24px" }}>
            <h3 style={{ fontSize: "0.9rem", color: "var(--clay-red)", margin: "0 0 12px 0", fontWeight: "700" }}>{date}</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              {groupedLogs[date].map((log) => (
                <div
                  key={log.client_id || log.id}
                  style={{
                    background: "white",
                    border: "1px solid var(--border-soil)",
                    borderRadius: "6px",
                    padding: "14px",
                    position: "relative"
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                    <span style={{ fontSize: "0.8rem", color: "var(--paddy-green)", fontWeight: "700" }}>
                      {getPlotName(log.plot_id)}
                    </span>
                    <span className={`status-badge ${log.synced ? "synced" : "unsynced"}`} style={{ fontSize: "0.7rem", padding: "2px 6px" }}>
                      {log.synced ? <Cloud size={10} /> : <CloudLightning size={10} />}
                      {log.synced ? (isTamil ? "ஒத்திசைக்கப்பட்டது" : "Synced") : (isTamil ? "ஆஃப்லைன்" : "Offline")}
                    </span>
                  </div>
                  <p style={{ margin: 0, fontSize: "0.95rem", color: "var(--text-main)", lineHeight: "1.5" }}>{log.entry_text}</p>
                </div>
              ))}
            </div>
          </div>
        ))
      )}

      {/* Global CSS styles injection for pulse-record animation */}
      <style>{`
        @keyframes pulse-record {
          0% {
            box-shadow: 0 0 0 0 rgba(162, 61, 29, 0.4);
          }
          70% {
            box-shadow: 0 0 0 12px rgba(162, 61, 29, 0);
          }
          100% {
            box-shadow: 0 0 0 0 rgba(162, 61, 29, 0);
          }
        }
      `}</style>
    </div>
  );
}
