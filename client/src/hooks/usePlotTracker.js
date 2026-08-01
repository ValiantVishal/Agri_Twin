import { useState, useEffect, useRef } from "react";
import * as turf from "@turf/turf";

export const usePlotTracker = (config = { minDistance: 5, minTime: 10 }) => {
  const [points, setPoints] = useState([]);
  const [isTracking, setIsTracking] = useState(false);
  const [isClosed, setIsClosed] = useState(false);
  const [currentPosition, setCurrentPosition] = useState(null);
  const [gpsAccuracy, setGpsAccuracy] = useState(null);
  const [error, setError] = useState(null);
  const [selfIntersecting, setSelfIntersecting] = useState(false);

  const [metrics, setMetrics] = useState({
    areaSqm: 0,
    areaAcres: 0,
    areaCents: 0,
    perimeterM: 0,
  });

  const watchIdRef = useRef(null);
  const lastLoggedRef = useRef(null);

  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const from = turf.point([lon1, lat1]);
    const to = turf.point([lon2, lat2]);
    return turf.distance(from, to, { units: "meters" });
  };

  useEffect(() => {
    if (points.length < 3) {
      setMetrics({ areaSqm: 0, areaAcres: 0, areaCents: 0, perimeterM: 0 });
      setSelfIntersecting(false);
      return;
    }

    try {
      const coords = points.map((p) => [p.lng, p.lat]);
      const closedCoords = [...coords, coords[0]];

      const poly = turf.polygon([closedCoords]);
      const area = turf.area(poly);
      const line = turf.lineString(closedCoords);
      const perimeter = turf.length(line, { units: "meters" });

      const kinks = turf.kinks(poly);
      setSelfIntersecting(kinks.features.length > 0);

      const acres = area / 4046.8564224;
      setMetrics({
        areaSqm: area,
        areaAcres: acres,
        areaCents: acres * 100,
        perimeterM: perimeter,
      });
    } catch (e) {
      console.error("Error calculating metrics", e);
    }
  }, [points]);

  const logPoint = (lat, lng) => {
    const newPoint = { lat, lng, timestamp: new Date().toISOString() };
    setPoints((prev) => {
      if (prev.length > 0) {
        const last = prev[prev.length - 1];
        if (last.lat === lat && last.lng === lng) return prev;
      }
      return [...prev, newPoint];
    });
    lastLoggedRef.current = { lat, lng, time: Date.now() };
  };

  const startTracking = () => {
    if (!navigator.geolocation) {
      setError("gps_unsupported");
      return;
    }

    setError(null);
    setIsTracking(true);
    setIsClosed(false);

    watchIdRef.current = navigator.geolocation.watchPosition(
      (position) => {
        const { latitude, longitude, accuracy } = position.coords;
        setCurrentPosition({ lat: latitude, lng: longitude });
        setGpsAccuracy(accuracy);

        if (isTracking && !isClosed) {
          let shouldLog = false;
          const now = Date.now();

          if (!lastLoggedRef.current) {
            shouldLog = true;
          } else {
            const dist = calculateDistance(
              lastLoggedRef.current.lat,
              lastLoggedRef.current.lng,
              latitude,
              longitude
            );
            const timePassed = (now - lastLoggedRef.current.time) / 1000;

            if (dist >= config.minDistance || timePassed >= config.minTime) {
              shouldLog = true;
            }
          }

          if (shouldLog) {
            logPoint(latitude, longitude);
          }
        }
      },
      (err) => {
        setError(err.code === 1 ? "gps_permission_denied" : err.message);
        setIsTracking(false);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  };

  const stopTracking = () => {
    if (watchIdRef.current) {
      navigator.geolocation.clearWatch(watchIdRef.current);
      watchIdRef.current = null;
    }
    setIsTracking(false);
  };

  const dropPin = () => {
    if (currentPosition) {
      logPoint(currentPosition.lat, currentPosition.lng);
    } else {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude, accuracy } = position.coords;
          setCurrentPosition({ lat: latitude, lng: longitude });
          setGpsAccuracy(accuracy);
          logPoint(latitude, longitude);
        },
        (err) => setError(err.code === 1 ? "gps_permission_denied" : err.message),
        { enableHighAccuracy: true }
      );
    }
  };

  const closePlot = () => {
    if (points.length < 3) {
      setError("min_points_warning");
      return;
    }
    setIsClosed(true);
    stopTracking();
  };

  const resetTracker = () => {
    stopTracking();
    setPoints([]);
    setIsClosed(false);
    lastLoggedRef.current = null;
    setError(null);
    setSelfIntersecting(false);
    setMetrics({ areaSqm: 0, areaAcres: 0, areaCents: 0, perimeterM: 0 });
  };

  const deletePoint = (index) => {
    setPoints((prev) => prev.filter((_, i) => i !== index));
  };

  const nudgePoint = (index, newLat, newLng) => {
    setPoints((prev) => {
      const copy = [...prev];
      copy[index] = { ...copy[index], lat: parseFloat(newLat), lng: parseFloat(newLng) };
      return copy;
    });
  };

  useEffect(() => {
    return () => {
      if (watchIdRef.current) navigator.geolocation.clearWatch(watchIdRef.current);
    };
  }, []);

  return {
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
  };
};
