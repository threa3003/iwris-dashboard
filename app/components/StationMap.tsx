'use client';

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import StationChart from './StationChart';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

interface Station {
  station_code: string;
  station_name: string;
  parameter: string;
  state: string;
  district: string;
  latitude: number;
  longitude: number;
  data_status: string;
}

export default function StationMap() {
  const [stations, setStations] = useState<Station[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/stations')
      .then((res) => res.json())
      .then((data) => {
        setStations(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setStations([]);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading map...</div>;

  return (
    <MapContainer
      center={[22.5, 80]}
      zoom={5}
      style={{ height: '100vh', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />
      <MarkerClusterGroup>
        {stations
          .filter((s) => s.latitude && s.longitude)
          .map((s) => (
            <Marker key={s.station_code} position={[s.latitude, s.longitude]}>
              <Popup minWidth={280}>
                <strong>{s.station_name}</strong>
                <br />
                {s.parameter} — {s.district}, {s.state}
                <br />
                {s.data_status}
                <StationChart stationCode={s.station_code} />
              </Popup>
            </Marker>
          ))}
      </MarkerClusterGroup>
    </MapContainer>
  );
}
