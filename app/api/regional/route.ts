import pool from '@/lib/db';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const result = await pool.query(
      'SELECT s.state, s.parameter, AVG(r.value) as avg_value, COUNT(DISTINCT s.station_code) as station_count FROM stations s JOIN readings r ON s.station_code = r.station_code GROUP BY s.state, s.parameter ORDER BY s.state'
    );
    return NextResponse.json(result.rows);
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Query failed' }, { status: 500 });
  }
}
