import pool from '@/lib/db';
import { NextResponse } from 'next/server';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ station_code: string }> }
) {
  const { station_code } = await params;
  try {
    const result = await pool.query(
      'SELECT date, value FROM readings WHERE station_code = $1 ORDER BY date ASC',
      [station_code]
    );
    return NextResponse.json(result.rows);
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Query failed' }, { status: 500 });
  }
}
