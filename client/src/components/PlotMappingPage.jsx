import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { usePlotTracker } from "../hooks/usePlotTracker";
import { plotService, getProfile } from "../api/plotService";
import PlotMapView from "./PlotMapView";
import PlotList from "./PlotList";
import "../css/PlotMappingPage.css";

import {
  Compass,
  MapPin,
  Save,
  RotateCcw,
  Navigation,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  LogOut,
} from "lucide-react";

export default function PlotMappingPage() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();

  const {
    points,
    setPoints,
    isTracking,
    isClosed,
    setIsClosed,
    currentPosition,
    gpsAccuracy,
    error,
    setError,
    selfIntersecting,
    metrics,
    startTracking,
    stopTracking,
    dropPin,
    closePlot,
    resetTracker,
    deletePoint,
    nudgePoint,
  } = usePlotTracker();

  const [plotName, setPlotName] = useState("");
  const [savedPlots, setSavedPlots] = useState([]);
  const [onlineStatus, setOnlineStatus] = useState(navigator.onLine);
  const [farmerName, setFarmerName] = useState("");
  const [editPlotId, setEditPlotId] = useState(null);
  const [syncingStatus, setSyncingStatus] = useState(false);
  const [serverWarning, setServerWarning] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

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
    const fetchUserData = async () => {
      try {
        const response = await getProfile();
        setFarmerName(response.data.name);
        if (response.data.language === "Tamil" || response.data.language === "English") {
          i18n.changeLanguage(response.data.language);
        }
      } catch (err) {
        console.error("Unable to load profile", err);
      }
      await loadPlots();
    };
    fetchUserData();
  }, []);

  const loadPlots = async () => {
    try {
      const list = await plotService.getPlots();
      setSavedPlots(list);
    } catch (e) {
      console.error("Error loading plots", e);
    }
  };

  const triggerManualSync = async () => {
    if (!onlineStatus) return;
    setSyncingStatus(true);
    try {
      const count = await plotService.syncOfflineQueue();
      if (count > 0) {
        setSuccessMessage(`${t("syncing_now")} (${count} plots synced)`);
        setTimeout(() => setSuccessMessage(""), 4000);
      }
      await loadPlots();
    } catch (e) {
      console.error("Sync failed", e);
    } finally {
      setSyncingStatus(false);
    }
  };

  const handleSavePlot = async () => {
    if (!plotName.trim()) {
      alert("Please enter a plot name.");
      return;
    }
    if (points.length < 3) {
      alert(t("min_points_warning"));
      return;
    }
    if (!isClosed) setIsClosed(true);

    const plotData = {
      id: editPlotId || crypto.randomUUID(),
      plot_name: plotName,
      points,
      area_sqm: metrics.areaSqm,
      area_acres: metrics.areaAcres,
      area_cents: metrics.areaCents,
      perimeter_m: metrics.perimeterM,
    };

    try {
      if (editPlotId) {
        const updated = await plotService.updatePlot(editPlotId, plotData);
        setServerWarning(updated.warning || "");
      } else {
        const saved = await plotService.savePlotLocally(plotData);
        setServerWarning(saved.warning || "");
      }
      setSuccessMessage(onlineStatus ? t("success_save") : t("offline_save"));
      setTimeout(() => setSuccessMessage(""), 5000);
      resetTracker();
      setPlotName("");
      setEditPlotId(null);
      await loadPlots();
    } catch (err) {
      alert("Error saving plot. Try again.");
    }
  };

  const handleEditPlot = (plot) => {
    resetTracker();
    setEditPlotId(plot.id);
    setPlotName(plot.plot_name);
    setPoints(plot.points);
    setIsClosed(true);
    setServerWarning("");
  };

  const handleDeletePlot = async (id) => {
    try {
      await plotService.deletePlot(id);
      await loadPlots();
      if (editPlotId === id) {
        resetTracker();
        setPlotName("");
        setEditPlotId(null);
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="plot-mapping-container">
      <header className="mapping-header">
        <button className="btn-back" onClick={() => navigate("/dashboard")}>
          <LogOut size={16} style={{ transform: "rotate(180deg)" }} />
          <span>{t("back_to_dashboard")}</span>
        </button>
        <h1>{t("title")} {farmerName ? `(${farmerName})` : ""}</h1>
        <div className="header-controls">
          <span className={`status-badge ${onlineStatus ? "synced" : "unsynced"}`} onClick={triggerManualSync}>
            {onlineStatus ? <CheckCircle size={14} /> : <AlertTriangle size={14} />}
            {onlineStatus ? "Online" : "Offline"}
            {syncingStatus && <RefreshCw size={12} className="spin" />}
          </span>
          <select className="lang-select" onChange={(e) => i18n.changeLanguage(e.target.value)} value={i18n.language}>
            <option value="English">English</option>
            <option value="Tamil">தமிழ்</option>
          </select>
        </div>
      </header>
      <div className="mapping-grid">
        <aside className="control-panel">
          <div className="glass-card">
            <h2>{editPlotId ? t("remapping_mode") : "Record Boundary"}</h2>
            <input
              type="text"
              className="plot-name-input"
              placeholder={t("plot_name_placeholder")}
              value={plotName}
              onChange={(e) => setPlotName(e.target.value)}
            />
            <div className="gps-metrics">
              <div className="metric-badge">
                <span className="label">{t("area")} ({t("acres")})</span>
                <span className="val highlight">{metrics.areaAcres.toFixed(2)}</span>
              </div>
              <div className="metric-badge">
                <span className="label">{t("area")} ({t("cents")})</span>
                <span className="val highlight">{metrics.areaCents.toFixed(1)}</span>
              </div>
              <div className="metric-badge">
                <span className="label">{t("perimeter")}</span>
                <span className="val">{metrics.perimeterM.toFixed(1)} m</span>
              </div>
              <div className="metric-badge">
                <span className="label">{t("accuracy")}</span>
                <span className={`val ${gpsAccuracy > 10 ? "danger" : ""}`}>
                  {gpsAccuracy ? `${gpsAccuracy.toFixed(1)}m` : "--"}
                </span>
              </div>
            </div>
            {error && <div className="alert-box alert-danger">{t(error) || error}</div>}
            {gpsAccuracy > 10 && <div className="alert-box alert-warning">{t("accuracy_warning")}</div>}
            {selfIntersecting && <div className="alert-box alert-warning">{t("self_intersecting_warning")}</div>}
            {serverWarning && <div className="alert-box alert-warning">{serverWarning}</div>}
            {successMessage && <div className="alert-box alert-success">{successMessage}</div>}
            <div className="action-buttons">
              {!isTracking && !isClosed && (
                <button className="btn btn-primary" onClick={startTracking}>
                  <Compass />{t("start_walk")}
                </button>
              )}
              {isTracking && (
                <button className="btn btn-secondary" onClick={stopTracking}>
                  <Compass className="spin" />{t("stop_walk")}
                </button>
              )}
              {(!isClosed || isTracking) && (
                <button className="btn btn-secondary" onClick={dropPin} disabled={!currentPosition}>
                  <MapPin />{t("drop_pin")}
                </button>
              )}
              {points.length >= 3 && !isClosed && (
                <button className="btn btn-secondary" onClick={closePlot}>
                  <Navigation />{t("close_plot")}
                </button>
              )}
              {points.length >= 3 && (isClosed || !isTracking) && (
                <button className="btn btn-save" onClick={handleSavePlot} disabled={selfIntersecting}>
                  <Save />{t("save_plot")}
                </button>
              )}
              {(points.length > 0 || editPlotId) && (
                <button className="btn btn-danger" onClick={() => { resetTracker(); setPlotName(""); setEditPlotId(null); setServerWarning(""); }}>
                  <RotateCcw />{t("reset")}
                </button>
              )}
            </div>
          </div>
        </aside>
        <main className="map-card">
          <PlotMapView
            points={points}
            currentPosition={currentPosition}
            isClosed={isClosed}
            onDeletePoint={deletePoint}
            onNudgePoint={nudgePoint}
          />
        </main>
        <section className="saved-plots-section glass-card">
          <h2>{t("saved_plots")}</h2>
          <PlotList plots={savedPlots} onEdit={handleEditPlot} onDelete={handleDeletePlot} />
        </section>
      </div>
    </div>
  );
}
