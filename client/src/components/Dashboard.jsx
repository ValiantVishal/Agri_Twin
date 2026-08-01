import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getProfile, plotService } from "../api/plotService";
import { Compass, User, Layers, Map, RefreshCw, AlertCircle } from "lucide-react";

export default function Dashboard() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [plotStats, setPlotStats] = useState({ count: 0, acres: 0 });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const profRes = await getProfile();
        setProfile(profRes.data);
        
        const plots = await plotService.getPlots();
        const totalAcres = plots.reduce((acc, p) => acc + p.area_acres, 0);
        setPlotStats({ count: plots.length, acres: totalAcres });
      } catch (err) {
        console.error("Dashboard load warning:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
        <div style={{ textAlign: "center" }}>
          <RefreshCw className="spin" size={40} style={{ color: "var(--paddy-green)", marginBottom: "16px" }} />
          <p style={{ fontStyle: "italic", color: "var(--text-muted)" }}>AgriTwin...</p>
        </div>
      </div>
    );
  }

  const isTamil = profile?.language === "Tamil";

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", padding: "24px", minHeight: "100vh" }}>
      {/* Top Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: "32px", borderBottom: "2px solid var(--border-soil)", paddingBottom: "16px" }}>
        <div>
          <h1 style={{ margin: 0, fontSize: "2rem", color: "var(--paddy-green)" }}>AgriTwin</h1>
          <p style={{ margin: "4px 0 0 0", color: "var(--text-muted)", fontSize: "0.95rem", fontWeight: "600" }}>
            {isTamil ? `${profile?.name || "விவசாயி"} அவர்களின் கட்டுப்பாட்டு அறை` : `Farmer Dashboard — ${profile?.name || "Farmer"}`}
          </p>
        </div>
        <button
          onClick={() => {
            localStorage.removeItem("token");
            navigate("/");
          }}
          style={{
            padding: "8px 16px",
            border: "1px solid var(--border-soil)",
            background: "none",
            fontSize: "0.85rem",
            color: "var(--text-muted)"
          }}
        >
          {isTamil ? "வெளியேறு" : "Logout"}
        </button>
      </div>

      {/* Primary Visual Anchor / Call to Action */}
      {plotStats.count === 0 ? (
        <div style={{
          border: "2px dashed var(--clay-red)",
          backgroundColor: "white",
          borderRadius: "8px",
          padding: "40px 24px",
          textAlign: "center",
          marginBottom: "32px"
        }}>
          <div style={{ color: "var(--clay-red)", marginBottom: "16px" }}>
            <Map size={48} strokeWidth={1.5} />
          </div>
          <h2 style={{ fontSize: "1.5rem", color: "var(--text-main)", marginBottom: "12px" }}>
            {isTamil ? "முதல் நில வரைபடத்தை உருவாக்கவும்" : "No Land Mapped Yet"}
          </h2>
          <p style={{ color: "var(--text-muted)", maxWidth: "500px", margin: "0 auto 24px auto", lineHeight: "1.6", fontSize: "0.95rem" }}>
            {isTamil 
              ? "உங்கள் வயலின் எல்லையில் நடப்பதன் மூலம் துல்லியமான நில எல்லையையும் பரப்பளவையும் (சென்ட்/ஏக்கர்) கணக்கிடுங்கள்." 
              : "Walk your field boundary with your phone to automatically calculate your actual farm area in acres & cents and save it offline."}
          </p>
          <Link 
            to="/plots" 
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "8px",
              backgroundColor: "var(--clay-red)",
              color: "white",
              padding: "14px 28px",
              borderRadius: "6px",
              textDecoration: "none",
              fontWeight: "700",
              boxShadow: "0 2px 4px rgba(162, 61, 29, 0.15)"
            }}
          >
            <Compass size={20} />
            {isTamil ? "பதிவு செய்யத் தொடங்கவும்" : "Start Plot Mapping"}
          </Link>
        </div>
      ) : (
        /* If plots exist, show Stats summary card */
        <div style={{
          background: "white",
          border: "1px solid var(--border-soil)",
          borderRadius: "8px",
          padding: "24px",
          marginBottom: "32px"
        }}>
          <h2 style={{ fontSize: "1.2rem", margin: "0 0 16px 0", color: "var(--text-muted)" }}>
            {isTamil ? "நில வரைபட சுருக்கம்" : "Farm Property Summary"}
          </h2>
          
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
            <div>
              <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontWeight: "600", textTransform: "uppercase" }}>
                {isTamil ? "வரைபடங்களின் எண்ணிக்கை" : "Total Mapped Plots"}
              </span>
              <div style={{ fontSize: "2.5rem", fontWeight: "800", color: "var(--paddy-green)", fontFamily: "var(--font-body)" }}>
                {plotStats.count}
              </div>
            </div>
            <div>
              <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontWeight: "600", textTransform: "uppercase" }}>
                {isTamil ? "மொத்த பரப்பளவு" : "Total Area"}
              </span>
              <div style={{ fontSize: "2.5rem", fontWeight: "800", color: "var(--paddy-green)", fontFamily: "var(--font-body)" }}>
                {plotStats.acres.toFixed(2)} <span style={{ fontSize: "1.1rem", fontWeight: "600", color: "var(--text-muted)" }}>{isTamil ? "ஏக்கர்" : "Acres"}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Feature Links Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "20px" }}>
        
        {/* Plot Mapping Quicklink (only if already mapped, otherwise CTA dominates) */}
        {plotStats.count > 0 && (
          <Link to="/plots" style={{
            display: "flex",
            flexDirection: "column",
            padding: "20px",
            textDecoration: "none",
            background: "white",
            borderRadius: "8px",
            border: "1px solid var(--border-soil)",
            transition: "transform 0.2s"
          }}>
            <h3 style={{ margin: "0 0 8px 0", color: "var(--paddy-green)", fontSize: "1.2rem" }}>
              {isTamil ? "நில வரைபடம் & ஜி.பி.எஸ்" : "Plot Mapping & GPS"}
            </h3>
            <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "0.9rem", lineHeight: "1.5" }}>
              {isTamil 
                ? "புதிய எல்லையை அளவிடவும் அல்லது ஏற்கனவே வரைந்த எல்லையை மாற்றியமைக்கவும்." 
                : "Map new field boundaries or re-walk and edit existing plot vertices in the field."}
            </p>
            <span style={{ marginTop: "16px", color: "var(--clay-red)", fontWeight: "700", fontSize: "0.9rem" }}>
              {isTamil ? "அளவிடச் செல்" : "Open Workspace"} &rarr;
            </span>
          </Link>
        )}

        {/* Profile Settings */}
        <Link to="/profile" style={{
          display: "flex",
          flexDirection: "column",
          padding: "20px",
          textDecoration: "none",
          background: "white",
          borderRadius: "8px",
          border: "1px solid var(--border-soil)",
          transition: "transform 0.2s"
        }}>
          <h3 style={{ margin: "0 0 8px 0", color: "var(--text-main)", fontSize: "1.2rem" }}>
            {isTamil ? "சுயவிவரம்" : "Farmer Profile"}
          </h3>
          <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "0.9rem", lineHeight: "1.5" }}>
            {isTamil 
              ? "உங்கள் மொழி, பயிர், மண்வகை மற்றும் பாசன வசதி விபரங்களை மாற்றவும்." 
              : "Update your crops, district settings, preferred language, and farming experience."}
          </p>
          <span style={{ marginTop: "16px", color: "var(--text-main)", fontWeight: "700", fontSize: "0.9rem" }}>
            {isTamil ? "விபரங்களை மாற்று" : "View Settings"} &rarr;
          </span>
        </Link>

      </div>
    </div>
  );
}