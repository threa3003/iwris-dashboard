'use client';

import { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface Reading {
  date: string;
  value: number;
}

export default function StationChart({ stationCode }: { stationCode: string }) {
  const [readings, setReadings] = useState<Reading[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/readings/${stationCode}`)
      .then((res) => res.json())
      .then((data) => {
        setReadings(data);
        setLoading(false);
      });
  }, [stationCode]);

  if (loading) return <div>Loading chart...</div>;
  if (readings.length === 0) return <div>No readings available for this station.</div>;

  return (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={readings}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="value" stroke="#2563eb" dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}