import { useCallback, useEffect, useState } from "react";

export type GeoCoords = { lat: number; lon: number };

export function useGeoLocation(): {
  coords: GeoCoords | null;
  error: string | null;
  loading: boolean;
  refresh: () => void;
} {
  const [coords, setCoords] = useState<GeoCoords | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const mapGeoError = (err: GeolocationPositionError): string => {
    switch (err.code) {
      case err.PERMISSION_DENIED:
        return "Location permission denied. Enable location access or enter city manually.";
      case err.POSITION_UNAVAILABLE:
        return "Location is currently unavailable. Try again or enter city manually.";
      case err.TIMEOUT:
        return "Location request timed out. Please retry.";
      default:
        return "Unable to fetch GPS location. Please try again.";
    }
  };

  const refresh = useCallback(() => {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by this browser.");
      return;
    }
    setLoading(true);
    setError(null);
    const onSuccess = (pos: GeolocationPosition) => {
      setCoords({ lat: pos.coords.latitude, lon: pos.coords.longitude });
      setLoading(false);
    };

    const onFailure = (err: GeolocationPositionError) => {
      // Retry once with lower accuracy to avoid provider/network-service hiccups.
      navigator.geolocation.getCurrentPosition(
        onSuccess,
        (fallbackErr) => {
          setError(mapGeoError(fallbackErr));
          setLoading(false);
        },
        { enableHighAccuracy: false, timeout: 12000, maximumAge: 180000 },
      );
    };

    navigator.geolocation.getCurrentPosition(
      onSuccess,
      onFailure,
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 },
    );
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { coords, error, loading, refresh };
}
