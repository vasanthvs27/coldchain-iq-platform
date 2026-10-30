import React, { useState, useEffect } from 'react';
import { ShieldAlert, Search, Filter, AlertTriangle, Eye, CheckCircle2, X } from 'lucide-react';
import apiClient from '../../services/api';
import PageHeader from '../../components/common/PageHeader';
import StatusBadge from '../../components/common/StatusBadge';

export default function ExcursionsPage() {
  const [excursions, setExcursions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('');
  const [selectedExcursion, setSelectedExcursion] = useState(null);
  const [investigationNotes, setInvestigationNotes] = useState('');

  const fetchExcursions = async () => {
    setLoading(true);
    try {
      const params = {};
      if (severityFilter) params.severity = severityFilter;
      const res = await apiClient.get('/excursions', { params });
      if (res.success) setExcursions(res.data);
    } catch (err) {
      console.error('Failed to load excursions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExcursions();
  }, [severityFilter]);

  const handleUpdateInvestigation = async (e) => {
    e.preventDefault();
    if (!selectedExcursion) return;
    try {
      const res = await apiClient.put(`/excursions/${selectedExcursion.excursion_id}/investigation`, {
        investigation_status: 'RESOLVED',
        evidence_reference: `${selectedExcursion.evidence_reference || ''} [Note: ${investigationNotes}]`,
      });
      if (res.success) {
        setSelectedExcursion(null);
        setInvestigationNotes('');
        fetchExcursions();
      }
    } catch (err) {
      alert(`Update failed: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Temperature Excursion Investigations"
        subtitle="Forensic evidence, duration calculations, root-cause investigation records, and compliance impact"
      />

      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex items-center justify-between gap-4">
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="text-xs border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-700 font-semibold focus:outline-none focus:border-blue-500"
        >
          <option value="">All Severities</option>
          <option value="CRITICAL">CRITICAL</option>
          <option value="HIGH">HIGH</option>
          <option value="MEDIUM">MEDIUM</option>
          <option value="LOW">LOW</option>
        </select>
        <span className="text-xs text-slate-500 font-medium">{excursions.length} excursions logged</span>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
              <tr>
                <th className="py-3 px-4 font-semibold">Excursion ID</th>
                <th className="py-3 px-4 font-semibold">Shipment / Lot</th>
                <th className="py-3 px-4 font-semibold">Issue Type</th>
                <th className="py-3 px-4 font-semibold">Duration (mins)</th>
                <th className="py-3 px-4 font-semibold">Observed Min/Max</th>
                <th className="py-3 px-4 font-semibold">Severity</th>
                <th className="py-3 px-4 font-semibold">Decision</th>
                <th className="py-3 px-4 font-semibold text-right">Investigation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="8" className="text-center py-10 text-slate-400">Loading excursions...</td>
                </tr>
              ) : excursions.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center py-10 text-slate-400">No excursions found.</td>
                </tr>
              ) : (
                excursions.map((ex) => (
                  <tr key={ex.excursion_id} className="hover:bg-slate-50">
                    <td className="py-3 px-4 font-mono font-bold text-rose-600">{ex.excursion_id}</td>
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-900">{ex.shipment_id}</div>
                      <div className="text-[10px] text-slate-400 font-mono">{ex.lot_id}</div>
                    </td>
                    <td className="py-3 px-4 font-medium text-slate-800">{ex.issue_type}</td>
                    <td className="py-3 px-4 font-bold text-slate-900">{ex.calculated_duration}m</td>
                    <td className="py-3 px-4 text-slate-700">
                      [{ex.minimum_observed_temperature}°C, {ex.maximum_observed_temperature}°C]
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={ex.severity} />
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={ex.compliance_decision} />
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => setSelectedExcursion(ex)}
                        className="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-[11px] font-semibold"
                      >
                        Investigate
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Investigation Modal */}
      {selectedExcursion && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-900/60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-6 border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <h3 className="text-base font-bold text-slate-900">Excursion Investigation Workflow</h3>
              <button onClick={() => setSelectedExcursion(null)} className="text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="mt-4 space-y-3 text-xs">
              <div className="p-3 bg-rose-50 rounded-lg border border-rose-100 text-rose-800 font-mono">
                {selectedExcursion.excursion_id} • Duration: {selectedExcursion.calculated_duration} mins
              </div>

              <div>
                <span className="font-semibold text-slate-700 block">Forensic Telemetry Evidence</span>
                <p className="text-slate-600 bg-slate-50 p-2.5 rounded border border-slate-200 mt-1 font-mono">
                  {selectedExcursion.evidence_reference || 'Telemetry reading range'}
                </p>
              </div>

              <form onSubmit={handleUpdateInvestigation} className="space-y-3 pt-2">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">CAPA / Root Cause Notes</label>
                  <textarea
                    value={investigationNotes}
                    onChange={(e) => setInvestigationNotes(e.target.value)}
                    placeholder="Enter root cause analysis (e.g., dry ice sublimation, refrigeration unit breakdown, customs inspection delay)..."
                    className="w-full border border-slate-200 rounded-lg p-2.5 focus:ring-2 focus:ring-blue-500/20"
                    rows={3}
                    required
                  />
                </div>

                <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
                  <button
                    type="button"
                    onClick={() => setSelectedExcursion(null)}
                    className="px-4 py-2 rounded-lg border border-slate-200 text-slate-600 font-semibold"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold">
                    Sign Off & Resolve
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
