import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { saveProfile } from "../api/profile";
import apiClient from "../api/apiClient";

function ProfileSetup() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    phone: "",
    state: "",
    district: "",
    village: "",
    language: "Tamil",
    farmerType: "",
    experience: "",
    crop: "",
    irrigation: "",
    soilType: ""
  });

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const response = await apiClient.get("/profile");
        if (response.data) {
          setForm({
            phone: response.data.phone || "",
            state: response.data.state || "",
            district: response.data.district || "",
            village: response.data.village || "",
            language: response.data.language || "Tamil",
            farmerType: response.data.farmerType || "",
            experience: response.data.experience !== undefined ? String(response.data.experience) : "",
            crop: response.data.crop || "",
            irrigation: response.data.irrigation || "",
            soilType: response.data.soilType || ""
          });
        }
      } catch (error) {
        console.log("No existing profile found to pre-fill.");
      }
    };
    loadProfile();
  }, []);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };
    
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const profile = {
      ...form,
      experience: Number(form.experience)
    };

    try {
      const response = await saveProfile(profile);
      console.log(response.data);
      alert("Profile Saved Successfully!");
      navigate("/dashboard");
    } catch (error) {
      console.error(error.response?.data || error);
      const errorMsg = error.response?.data?.detail || "Unable to save profile.";
      alert(`Error: ${errorMsg}`);
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: "520px" }}>
        <h1>Configure Profile</h1>
        <p>Enter your agricultural preferences and village location</p>

        <form onSubmit={handleSubmit}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              <label style={{ fontSize: "0.8rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-muted)" }}>Phone Number</label>
              <input
                name="phone"
                placeholder="e.g. +91 98765 43210"
                value={form.phone}
                onChange={handleChange}
                required
              />
            </div>
            
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              <label style={{ fontSize: "0.8rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-muted)" }}>Language preference</label>
              <select
                name="language"
                value={form.language}
                onChange={handleChange}
              >
                <option value="Tamil">தமிழ் (Tamil)</option>
                <option value="English">English</option>
              </select>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              <label style={{ fontSize: "0.75rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-muted)" }}>State</label>
              <input
                name="state"
                placeholder="State"
                value={form.state}
                onChange={handleChange}
                required
              />
            </div>
            
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              <label style={{ fontSize: "0.75rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-muted)" }}>District</label>
              <input
                name="district"
                placeholder="District"
                value={form.district}
                onChange={handleChange}
                required
              />
            </div>
            
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              <label style={{ fontSize: "0.75rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-muted)" }}>Village</label>
              <input
                name="village"
                placeholder="Village"
                value={form.village}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              <label style={{ fontSize: "0.8rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-muted)" }}>Farmer Type</label>
              <select
                name="farmerType"
                value={form.farmerType}
                onChange={handleChange}
                required
              >
                <option value="">Select Option</option>
                <option>New Farmer</option>
                <option>Experienced Farmer</option>
                <option>Retired Farmer</option>
              </select>
            </div>
            
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              <label style={{ fontSize: "0.8rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-muted)" }}>Experience (Years)</label>
              <input
                type="number"
                name="experience"
                placeholder="e.g. 5"
                value={form.experience}
                onChange={handleChange}
              />
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
            <label style={{ fontSize: "0.8rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-muted)" }}>Primary Crop</label>
            <input
              name="crop"
              placeholder="e.g. Rice, Sugarcane, Cotton"
              value={form.crop}
              onChange={handleChange}
            />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              <label style={{ fontSize: "0.8rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-muted)" }}>Irrigation Type</label>
              <select
                name="irrigation"
                value={form.irrigation}
                onChange={handleChange}
              >
                <option value="">Select Option</option>
                <option>Canal</option>
                <option>Borewell</option>
                <option>Rain-fed</option>
                <option>Drip</option>
              </select>
            </div>
            
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              <label style={{ fontSize: "0.8rem", fontWeight: "700", textTransform: "uppercase", color: "var(--text-muted)" }}>Soil Type</label>
              <select
                name="soilType"
                value={form.soilType}
                onChange={handleChange}
              >
                <option value="">Select Option</option>
                <option>Clay</option>
                <option>Loamy</option>
                <option>Sandy</option>
                <option>Red</option>
                <option>Black</option>
              </select>
            </div>
          </div>

          <button style={{ marginTop: "12px" }}>
            Save & Continue
          </button>
        </form>
      </div>
    </div>
  );
}

export default ProfileSetup;