import pool from '@/lib/db';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const result = await pool.query(
      'SELECT station_code, station_name, parameter, state, district, latitude, longitude, data_status FROM stations WHERE latitude IS NOT NULL AND longitude IS NOT NULL'
    );
    return NextResponse.json(result.rows);
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Database query failed' }, { status: 500 });
  }
}
