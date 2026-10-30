import React, { useState, useEffect } from 'react';
import { Radio, AlertTriangle, Search, CheckCircle2 } from 'lucide-react';
import apiClient from '../../services/api';
import PageHeader from '../../components/common/PageHeader';

export default function DataGapsPage() {
  const [shipments, setShipments] = useState([]);
  const [selectedShipment, setSelectedShipment] = useState('');
  const [gapAnalysis, setGapAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchShipments = async () => {
      const res = await apiClient.get('/shipments', { params: { page_size: 20 } });
      if (res.success && res.data.length > 0) {
        setShipments(res.data);
        setSelectedShipment(res.data[0].shipment_id);
      }
    };
    fetchShipments();
  }, []);

  useEffect(() => {
    if (!selectedShipment) return;
    const fetchGaps = async () => {
      setLoading(true);
      try {
        const res = await apiClient.get(`/temperature/shipments/${selectedShipment}/gaps`);
        if (res.success) setGapAnalysis(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchGaps();
  }, [selectedShipment]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Missing Telemetry Data Gap Detection"
        subtitle="10-minute automated telemetry interval surveillance, telemetry dropouts, and completeness audit"
        actions={
          <select
            value={selectedShipment}
            onChange={(e) => setSelectedShipment(e.target.value)}
            className="text-xs border border-slate-200 rounded-lg px-3 py-2 bg-white font-semibold text-slate-800"
          >
            {shipments.map((s) => (
              <option key={s.shipment_id} value={s.shipment_id}>
                {s.shipment_id} ({s.origin} → {s.destination})
              </option>
            ))}
          </select>
        }
      />

      {gapAnalysis && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-xl border border-slate-200">
            <span className="text-[11px] text-slate-500">Expected Readings</span>
            <div className="text-xl font-bold text-slate-900 mt-1">{gapAnalysis.expected_reading_count}</div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200">
            <span className="text-[11px] text-slate-500">Actual Readings Ingested</span>
            <div className="text-xl font-bold text-slate-900 mt-1">{gapAnalysis.actual_reading_count}</div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200">
            <span className="text-[11px] text-slate-500">Missing Readings Count</span>
            <div className="text-xl font-bold text-rose-600 mt-1">{gapAnalysis.missing_reading_count}</div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200">
            <span className="text-[11px] text-slate-500">Evidence Completeness</span>
            <div className="text-xl font-bold text-blue-600 mt-1">{gapAnalysis.completeness_pct}%</div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
        <h3 className="text-sm font-bold text-slate-900">Identified Communication Outages</h3>
        {gapAnalysis?.gaps?.length === 0 ? (
          <div className="py-8 text-center text-xs font-semibold text-emerald-600">
            ✓ Complete 10-minute continuous telemetry stream. No data gaps detected.
          </div>
        ) : (
          <div className="space-y-3">
            {gapAnalysis?.gaps?.map((g, idx) => (
              <div key={idx} className="p-4 rounded-xl border border-amber-200 bg-amber-50/30 flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-amber-900">
                    {g.issue_code || 'MISSING_DATA'} • {g.missing_readings_in_gap} missing readings
                  </div>
                  <div className="text-xs text-slate-600 mt-0.5">
                    Gap Duration: <span className="font-semibold">{g.gap_duration_minutes} minutes</span>
                  </div>
                  <div className="text-[11px] text-slate-500 mt-1 font-mono">
                    From {new Date(g.gap_start).toLocaleString()} to {new Date(g.gap_end).toLocaleString()}
                  </div>
                </div>
                <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200">
                  {g.severity}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
