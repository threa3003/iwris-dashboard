'use client';

import { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface RegionalData {
  state: string;
  parameter: string;
  avg_value: number;
  station_count: number;
}

export default function RegionalPage() {
  const [data, setData] = useState<RegionalData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/regional')
      .then((res) => res.json())
      .then((rows) => {
        setData(rows);
        setLoading(false);
      });
  }, []);

  if (loading) return <div style={{ padding: 20 }}>Loading regional data...</div>;

  const groundwaterData = data
    .filter((d) => d.parameter === 'groundwater')
    .map((d) => ({ state: d.state, value: Number(d.avg_value) }));

  const rainfallData = data
    .filter((d) => d.parameter === 'rainfall')
    .map((d) => ({ state: d.state, value: Number(d.avg_value) }));

  return (
    <div style={{ padding: 20 }}>
      <h1>Regional Comparison</h1>

      <h2>Average Groundwater Level by State</h2>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={groundwaterData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="state" angle={-45} textAnchor="end" interval={0} height={100} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="value" fill="#2563eb" name="Avg Groundwater" />
        </BarChart>
      </ResponsiveContainer>

      <h2>Average Rainfall by State</h2>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={rainfallData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="state" angle={-45} textAnchor="end" interval={0} height={100} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="value" fill="#16a34a" name="Avg Rainfall" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
