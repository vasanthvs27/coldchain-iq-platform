import React, { useState, useEffect } from 'react';
import { CheckCircle2, AlertTriangle, XCircle, RefreshCw, Play, ShieldAlert } from 'lucide-react';
import apiClient from '../../services/api';
import PageHeader from '../../components/common/PageHeader';
import StatusBadge from '../../components/common/StatusBadge';

export default function DataValidationPage() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const runValidations = async () => {
    setLoading(true);
    try {
      const res = await apiClient.post('/validation/run');
      if (res.success) setReport(res.data);
    } catch (err) {
      console.error('Validation error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runValidations();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Data Validation Center & Anomaly Reconciliation"
        subtitle="Structural integrity, primary & foreign keys, allowable enumerations, chronological timelines, and derived metric reconciliation"
        actions={
          <button
            onClick={runValidations}
            disabled={loading}
            className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition"
          >
            <Play className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Run Full Validation Suite
          </button>
        }
      />

      {/* Summary Cards */}
      {report?.summary && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-xl border border-slate-200">
            <span className="text-xs text-slate-500 font-semibold">Total Rules Tested</span>
            <div className="text-2xl font-bold text-slate-900 mt-1">{report.summary.total_rules}</div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-emerald-200 bg-emerald-50/20">
            <span className="text-xs text-emerald-700 font-semibold">Rules Passed</span>
            <div className="text-2xl font-bold text-emerald-700 mt-1">{report.summary.passed}</div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-amber-200 bg-amber-50/20">
            <span className="text-xs text-amber-700 font-semibold">Expected Injected Anomalies</span>
            <div className="text-2xl font-bold text-amber-700 mt-1">{report.summary.warnings}</div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200">
            <span className="text-xs text-slate-500 font-semibold">Unexpected System Failures</span>
            <div className="text-2xl font-bold text-slate-900 mt-1">{report.summary.failed}</div>
          </div>
        </div>
      )}

      {/* Rules Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 font-semibold text-xs text-slate-700 flex items-center justify-between">
          <span>Integrity Rules Evaluation</span>
          <span className="text-slate-500">Timestamp: {report?.validation_timestamp}</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
              <tr>
                <th className="py-3 px-4 font-semibold">Rule Name</th>
                <th className="py-3 px-4 font-semibold">Status</th>
                <th className="py-3 px-4 font-semibold">Evaluated</th>
                <th className="py-3 px-4 font-semibold">Passed</th>
                <th className="py-3 px-4 font-semibold">Failed</th>
                <th className="py-3 px-4 font-semibold">Expected Anomalies</th>
                <th className="py-3 px-4 font-semibold">Unexpected Failures</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="7" className="text-center py-10 text-slate-400">Running validation algorithms...</td>
                </tr>
              ) : (
                report?.results?.map((r, idx) => (
                  <tr key={idx} className="hover:bg-slate-50">
                    <td className="py-3 px-4 font-semibold text-slate-900">{r.rule_name}</td>
                    <td className="py-3 px-4">
                      <StatusBadge status={r.status} />
                    </td>
                    <td className="py-3 px-4 text-slate-700">{r.total_evaluated}</td>
                    <td className="py-3 px-4 font-semibold text-emerald-600">{r.passed_count}</td>
                    <td className="py-3 px-4 font-semibold text-rose-600">{r.failed_count}</td>
                    <td className="py-3 px-4 text-amber-600 font-semibold">{r.expected_anomalies}</td>
                    <td className="py-3 px-4 text-slate-600 font-semibold">{r.unexpected_failures}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
