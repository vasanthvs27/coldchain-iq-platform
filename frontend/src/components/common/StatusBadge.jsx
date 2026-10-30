import React from 'react';

export default function StatusBadge({ status, type = 'compliance' }) {
  const norm = (status || '').toUpperCase().trim();

  let style = 'bg-slate-100 text-slate-700 border-slate-200';

  if (norm === 'COMPLIANT' || norm === 'VALID' || norm === 'ACTIVE' || norm === 'DELIVERED' || norm === 'PASSED' || norm === 'RELEASED') {
    style = 'bg-emerald-50 text-emerald-700 border-emerald-200';
  } else if (norm === 'NON_COMPLIANT' || norm === 'CRITICAL' || norm === 'FAILED' || norm === 'EXPIRED') {
    style = 'bg-rose-50 text-rose-700 border-rose-200';
  } else if (norm === 'INCONCLUSIVE' || norm === 'WARNING' || norm === 'HIGH' || norm === 'MEDIUM') {
    style = 'bg-amber-50 text-amber-700 border-amber-200';
  } else if (norm === 'UNDER_REVIEW' || norm === 'IN_TRANSIT' || norm === 'IN_PROGRESS' || norm === 'SCHEDULED' || norm === 'LOW') {
    style = 'bg-blue-50 text-blue-700 border-blue-200';
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold border ${style}`}>
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current opacity-80" />
      {status || 'UNKNOWN'}
    </span>
  );
}
