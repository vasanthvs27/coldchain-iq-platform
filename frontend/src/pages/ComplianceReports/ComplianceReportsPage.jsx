import React, { useState, useEffect } from 'react';
import { FileCheck, Search, Download, ShieldCheck, AlertOctagon, CheckCircle2 } from 'lucide-react';
import apiClient from '../../services/api';
import PageHeader from '../../components/common/PageHeader';
import StatusBadge from '../../components/common/StatusBadge';

export default function ComplianceReportsPage() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');

  const fetchReports = async () => {
    setLoading(true);
    try {
      const params = {};
      if (statusFilter) params.status = statusFilter;
      const res = await apiClient.get('/compliance/reports', { params });
      if (res.success) setReports(res.data);
    } catch (err) {
      console.error('Failed to load compliance reports:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [statusFilter]);

  const handleExportCertificate = async (reportId) => {
    try {
      const res = await apiClient.post(`/compliance/reports/${reportId}/export`);
      if (res.success) {
        const jsonStr = JSON.stringify(res.data, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Compliance_Certificate_${reportId}.json`;
        a.click();
      }
    } catch (err) {
      alert(`Export failed: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Formal Compliance Decisions & Certificates"
        subtitle="12-step evidence-based release determinations, reason codes, and exportable regulatory audit certificates"
      />

      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex items-center justify-between gap-4">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="text-xs border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-700 font-semibold focus:outline-none focus:border-blue-500"
        >
          <option value="">All Decisions</option>
          <option value="COMPLIANT">COMPLIANT</option>
          <option value="NON_COMPLIANT">NON_COMPLIANT</option>
          <option value="INCONCLUSIVE">INCONCLUSIVE</option>
          <option value="UNDER_REVIEW">UNDER_REVIEW</option>
        </select>
        <span className="text-xs text-slate-500 font-medium">{reports.length} compliance reports</span>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
              <tr>
                <th className="py-3 px-4 font-semibold">Report ID</th>
                <th className="py-3 px-4 font-semibold">Shipment ID</th>
                <th className="py-3 px-4 font-semibold">Compliance Status</th>
                <th className="py-3 px-4 font-semibold">Score</th>
                <th className="py-3 px-4 font-semibold">Excursions</th>
                <th className="py-3 px-4 font-semibold">Missing Pings</th>
                <th className="py-3 px-4 font-semibold">Policy Version</th>
                <th className="py-3 px-4 font-semibold text-right">Certificate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="8" className="text-center py-10 text-slate-400">Loading reports...</td>
                </tr>
              ) : reports.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center py-10 text-slate-400">No compliance reports found.</td>
                </tr>
              ) : (
                reports.map((rep) => (
                  <tr key={rep.report_id} className="hover:bg-slate-50">
                    <td className="py-3 px-4 font-mono font-bold text-blue-600">{rep.report_id}</td>
                    <td className="py-3 px-4 font-mono text-slate-800">{rep.shipment_id}</td>
                    <td className="py-3 px-4">
                      <StatusBadge status={rep.compliance_status} />
                    </td>
                    <td className="py-3 px-4 font-bold text-slate-900">{rep.compliance_score}%</td>
                    <td className="py-3 px-4 font-semibold text-slate-700">{rep.excursion_count}</td>
                    <td className="py-3 px-4 text-slate-600">{rep.missing_readings}</td>
                    <td className="py-3 px-4 font-mono text-slate-500">{rep.policy_version}</td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleExportCertificate(rep.report_id)}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 font-semibold text-[11px]"
                      >
                        <Download className="w-3.5 h-3.5" />
                        Export
                      </button>
                    </td>
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
