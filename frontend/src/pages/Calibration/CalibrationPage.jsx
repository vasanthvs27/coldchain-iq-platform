import React, { useState, useEffect } from 'react';
import { Clock, AlertTriangle, ShieldCheck, CheckCircle2 } from 'lucide-react';
import apiClient from '../../services/api';
import PageHeader from '../../components/common/PageHeader';
import StatusBadge from '../../components/common/StatusBadge';

export default function CalibrationPage() {
  const [loggers, setLoggers] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchLoggers = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/loggers', { params: { page_size: 50 } });
      if (res.success) setLoggers(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLoggers();
  }, []);

  const expiredCount = loggers.filter((l) => new Date(l.calibration_expiry) < new Date()).length;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Logger Calibration & NIST Traceability Monitoring"
        subtitle="Calibration validity, expiry countdown, sensor measurement uncertainty, and calibration due tracking"
      />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <span className="text-xs text-slate-500 font-semibold">Total Fleet Monitored</span>
          <div className="text-2xl font-bold text-slate-900 mt-1">{loggers.length}</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-emerald-200 bg-emerald-50/20">
          <span className="text-xs text-emerald-700 font-semibold">Valid Calibrations</span>
          <div className="text-2xl font-bold text-emerald-700 mt-1">{loggers.length - expiredCount}</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-rose-200 bg-rose-50/20">
          <span className="text-xs text-rose-700 font-semibold">Calibration Expired / Due</span>
          <div className="text-2xl font-bold text-rose-700 mt-1">{expiredCount}</div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
              <tr>
                <th className="py-3 px-4 font-semibold">Logger ID</th>
                <th className="py-3 px-4 font-semibold">Model</th>
                <th className="py-3 px-4 font-semibold">Calibration Date</th>
                <th className="py-3 px-4 font-semibold">Expiry Date</th>
                <th className="py-3 px-4 font-semibold">Tolerance</th>
                <th className="py-3 px-4 font-semibold">Uncertainty</th>
                <th className="py-3 px-4 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loggers.map((l) => {
                const isExp = new Date(l.calibration_expiry) < new Date();
                return (
                  <tr key={l.logger_id} className="hover:bg-slate-50">
                    <td className="py-3 px-4 font-mono font-bold text-blue-600">{l.logger_id}</td>
                    <td className="py-3 px-4 font-medium text-slate-800">{l.model}</td>
                    <td className="py-3 px-4 text-slate-500">{new Date(l.calibration_date).toLocaleDateString()}</td>
                    <td className="py-3 px-4">
                      <span className={`font-semibold ${isExp ? 'text-rose-600' : 'text-slate-800'}`}>
                        {new Date(l.calibration_expiry).toLocaleDateString()}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-600">±{l.accuracy_tolerance}°C</td>
                    <td className="py-3 px-4 text-slate-600">±{l.measurement_uncertainty}°C</td>
                    <td className="py-3 px-4">
                      <StatusBadge status={isExp ? 'EXPIRED' : 'VALID'} />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
