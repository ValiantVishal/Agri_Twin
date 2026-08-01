import React from "react";
import { useTranslation } from "react-i18next";
import { Cloud, CloudLightning, Trash2, Edit3, AlertTriangle } from "lucide-react";

export default function PlotList({ plots, onEdit, onDelete }) {
  const { t } = useTranslation();

  if (plots.length === 0) {
    return (
      <div className="empty-state">
        <p>{t("no_plots")}</p>
      </div>
    );
  }

  return (
    <div className="plots-grid">
      {plots.map((plot) => (
        <div key={plot.id} className="plot-card">
          <div className="plot-card-header">
            <h3>{plot.plot_name}</h3>
            <span className={`status-badge ${plot.synced ? "synced" : "unsynced"}`}>
              {plot.synced ? <Cloud size={14} /> : <CloudLightning size={14} />}
              {plot.synced ? t("synced") : t("unsynced")}
            </span>
          </div>
          <div className="plot-card-body">
            <div className="metric-row">
              <span>{t("area")}:</span>
              <strong>{plot.area_acres.toFixed(2)} {t("acres")} ({plot.area_cents.toFixed(1)} {t("cents")})</strong>
            </div>
            <div className="metric-row">
              <span>{t("perimeter")}:</span>
              <strong>{plot.perimeter_m.toFixed(1)} {t("meters")}</strong>
            </div>
            {plot.warning && (
              <div className="drift-warning">
                <AlertTriangle size={16} />
                <span>{plot.warning}</span>
              </div>
            )}
          </div>
          <div className="plot-card-actions">
            <button className="btn btn-outline" onClick={() => onEdit(plot)}>
              <Edit3 size={16} />
              <span>{t("edit_plot")}</span>
            </button>
            <button className="btn btn-danger-icon" onClick={() => { if (confirm(t("confirm_delete_plot"))) onDelete(plot.id); }}>
              <Trash2 size={16} />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
