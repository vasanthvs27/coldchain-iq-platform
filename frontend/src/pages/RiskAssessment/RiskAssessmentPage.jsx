import React, { useState, useEffect } from 'react';
import { AlertTriangle, ShieldAlert, Truck, BarChart2 } from 'lucide-react';
import apiClient from '../../services/api';
import PageHeader from '../../components/common/PageHeader';
import StatusBadge from '../../components/common/StatusBadge';

export default function RiskAssessmentPage() {
  const [riskData, setRiskData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRisk = async () => {
      try {
        const res = await apiClient.get('/analytics/risk');
        if (res.success) setRiskData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRisk();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Shipment Risk & Carrier Reliability Assessment"
        subtitle="Predictive vulnerability modeling, carrier failure rates, route hazard scoring, and lane reliability"
      />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200">
          <span className="text-xs text-slate-500 font-semibold uppercase">Total Carriers Evaluated</span>
          <div className="text-2xl font-bold text-slate-900 mt-1">{riskData?.carrier_profiles?.length || 0}</div>
        </div>
        <div className="bg-white p-5 rounded-xl border border-rose-200 bg-rose-50/20">
          <span className="text-xs text-rose-700 font-semibold uppercase">High-Risk Freight Carriers</span>
          <div className="text-2xl font-bold text-rose-700 mt-1">{riskData?.high_risk_carrier_count || 0}</div>
        </div>
        <div className="bg-white p-5 rounded-xl border border-emerald-200 bg-emerald-50/20">
          <span className="text-xs text-emerald-700 font-semibold uppercase">Overall Fleet Health</span>
          <div className="text-2xl font-bold text-emerald-700 mt-1">OPTIMAL</div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 font-semibold text-xs text-slate-700">
          Carrier Risk Scorecard
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
              <tr>
                <th className="py-3 px-4 font-semibold">Carrier Name</th>
                <th className="py-3 px-4 font-semibold">Total Handled</th>
                <th className="py-3 px-4 font-semibold">Compliant Released</th>
                <th className="py-3 px-4 font-semibold">Violations / Excursions</th>
                <th className="py-3 px-4 font-semibold">Score</th>
                <th className="py-3 px-4 font-semibold">Risk Rating</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {riskData?.carrier_profiles?.map((c, idx) => (
                <tr key={idx} className="hover:bg-slate-50">
                  <td className="py-3 px-4 font-bold text-slate-900">{c.carrier_name}</td>
                  <td className="py-3 px-4 text-slate-700">{c.total_shipments}</td>
                  <td className="py-3 px-4 font-semibold text-emerald-600">{c.compliant_shipments}</td>
                  <td className="py-3 px-4 font-semibold text-rose-600">{c.violations}</td>
                  <td className="py-3 px-4 font-bold text-blue-600">{c.compliance_score}%</td>
                  <td className="py-3 px-4">
                    <StatusBadge status={c.risk_rating} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
