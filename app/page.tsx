'use client';

import dynamic from 'next/dynamic';
import Link from 'next/link';

const StationMap = dynamic(() => import('./components/StationMap'), {
  ssr: false,
});

export default function Home() {
  return (
    <div>
      <div style={{ position: 'absolute', top: 10, right: 10, zIndex: 1000 }}>
        <Link href="/regional" style={{ background: 'white', padding: '8px 16px', borderRadius: 4, textDecoration: 'none', color: '#000', fontWeight: 600 }}>
          Regional Comparison →
        </Link>
      </div>
      <StationMap />
    </div>
  );
}