import React, { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  Polygon,
  ScaleControl,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useTranslation } from "react-i18next";

import markerIconUrl from "leaflet/dist/images/marker-icon.png";
import markerShadowUrl from "leaflet/dist/images/marker-shadow.png";

const defaultIcon = L.icon({
  iconUrl: markerIconUrl,
  shadowUrl: markerShadowUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

const livePosIcon = L.divIcon({
  html: `<div class="live-pulse-container"><div class="live-pulse-dot"></div><div class="live-pulse-ring"></div></div>`,
  className: "live-position-div-icon",
  iconSize: [20, 20],
  iconAnchor: [10, 10],
});

const createNumberedIcon = (num) => {
  return L.divIcon({
    html: `<div class="vertex-badge">${num}</div>`,
    className: "vertex-badge-container",
    iconSize: [22, 22],
    iconAnchor: [11, 11],
  });
};

function ChangeView({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center) map.setView(center, map.getZoom());
  }, [center, map]);
  return null;
}

export default function PlotMapView({
  points,
  currentPosition,
  isClosed,
  onDeletePoint,
  onNudgePoint,
}) {
  const { t } = useTranslation();
  const [mapCenter, setMapCenter] = useState([10.787, 79.1378]);
  const [nudgeForm, setNudgeForm] = useState({ index: null, lat: "", lng: "" });

  useEffect(() => {
    if (currentPosition) {
      setMapCenter([currentPosition.lat, currentPosition.lng]);
    } else if (points.length > 0) {
      setMapCenter([points[0].lat, points[0].lng]);
    }
  }, [currentPosition]);

  const handleNudgeSubmit = (e) => {
    e.preventDefault();
    if (nudgeForm.index !== null && nudgeForm.lat && nudgeForm.lng) {
      onNudgePoint(nudgeForm.index, nudgeForm.lat, nudgeForm.lng);
      setNudgeForm({ index: null, lat: "", lng: "" });
    }
  };

  const polylineCoords = points.map((p) => [p.lat, p.lng]);

  return (
    <div style={{ height: "100%", width: "100%", position: "relative" }}>
      <MapContainer
        center={mapCenter}
        zoom={17}
        scrollWheelZoom={true}
        style={{ height: "100%", width: "100%", zIndex: 1 }}
      >
        <ChangeView center={currentPosition ? [currentPosition.lat, currentPosition.lng] : null} />
        <TileLayer
          attribution='&copy; OpenStreetMap'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ScaleControl position="bottomleft" />
        {currentPosition && (
          <Marker position={[currentPosition.lat, currentPosition.lng]} icon={livePosIcon}>
            <Popup>You are here</Popup>
          </Marker>
        )}
        {points.length > 0 && !isClosed && (
          <Polyline positions={polylineCoords} pathOptions={{ color: "#22c55e", weight: 4 }} />
        )}
        {points.length > 0 && isClosed && (
          <Polygon
            positions={polylineCoords}
            pathOptions={{ color: "#16a34a", fillColor: "#4ade80", fillOpacity: 0.35, weight: 4 }}
          />
        )}
        {points.map((p, index) => (
          <Marker key={index} position={[p.lat, p.lng]} icon={createNumberedIcon(index + 1)}>
            <Popup>
              <div>
                <h3>Point #{index + 1}</h3>
                <p>Lat: {p.lat.toFixed(6)}</p>
                <p>Lng: {p.lng.toFixed(6)}</p>
                <div style={{ display: "flex", gap: "8px", marginTop: "8px" }}>
                  <button onClick={() => onDeletePoint(index)}>{t("delete_point")}</button>
                  <button onClick={() => setNudgeForm({ index, lat: p.lat, lng: p.lng })}>{t("nudge_point")}</button>
                </div>
                {nudgeForm.index === index && (
                  <form onSubmit={handleNudgeSubmit} style={{ marginTop: "8px" }}>
                    <input
                      type="number"
                      step="any"
                      value={nudgeForm.lat}
                      onChange={(e) => setNudgeForm({ ...nudgeForm, lat: e.target.value })}
                      required
                    />
                    <input
                      type="number"
                      step="any"
                      value={nudgeForm.lng}
                      onChange={(e) => setNudgeForm({ ...nudgeForm, lng: e.target.value })}
                      required
                    />
                    <button type="submit">{t("save_btn")}</button>
                  </form>
                )}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
