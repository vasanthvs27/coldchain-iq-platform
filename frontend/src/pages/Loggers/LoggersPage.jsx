import React, { useState, useEffect } from 'react';
import { Cpu, Search, Battery, Clock, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';
import apiClient from '../../services/api';
import PageHeader from '../../components/common/PageHeader';
import StatusBadge from '../../components/common/StatusBadge';

export default function LoggersPage() {
  const [loggers, setLoggers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchLoggers = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/loggers', { params: { page, page_size: 25 } });
      if (res.success) {
        setLoggers(res.data);
        setTotal(res.meta?.total || res.data.length);
      }
    } catch (err) {
      console.error('Failed to load loggers:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLoggers();
  }, [page]);

  const filtered = loggers.filter((l) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return l.logger_id?.toLowerCase().includes(q) || l.serial_number?.toLowerCase().includes(q) || l.model?.toLowerCase().includes(q);
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="IoT Data Loggers & Calibration Fleet"
        subtitle="Active temperature telemetry sensors, NIST-traceable calibration dates, and battery telemetry"
      />

      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search logger ID, serial number, model..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          />
        </div>
        <span className="text-xs text-slate-500 font-medium">Fleet of {total} Loggers</span>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
              <tr>
                <th className="py-3 px-4 font-semibold">Logger ID</th>
                <th className="py-3 px-4 font-semibold">Serial Number</th>
                <th className="py-3 px-4 font-semibold">Model</th>
                <th className="py-3 px-4 font-semibold">Calibration Date</th>
                <th className="py-3 px-4 font-semibold">Calibration Expiry</th>
                <th className="py-3 px-4 font-semibold">Tolerance / Uncertainty</th>
                <th className="py-3 px-4 font-semibold">Battery</th>
                <th className="py-3 px-4 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="8" className="text-center py-10 text-slate-400">Loading logger fleet...</td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center py-10 text-slate-400">No data loggers found.</td>
                </tr>
              ) : (
                filtered.map((log) => {
                  const isExpired = new Date(log.calibration_expiry) < new Date();
                  return (
                    <tr key={log.logger_id} className="hover:bg-slate-50">
                      <td className="py-3 px-4 font-mono font-bold text-blue-600">{log.logger_id}</td>
                      <td className="py-3 px-4 font-mono text-slate-700">{log.serial_number}</td>
                      <td className="py-3 px-4 text-slate-800 font-medium">{log.model}</td>
                      <td className="py-3 px-4 text-slate-500">{new Date(log.calibration_date).toLocaleDateString()}</td>
                      <td className="py-3 px-4">
                        <span className={`font-semibold ${isExpired ? 'text-rose-600' : 'text-slate-700'}`}>
                          {new Date(log.calibration_expiry).toLocaleDateString()}
                        </span>
                        {isExpired && <span className="text-[10px] text-rose-500 block">EXPIRED</span>}
                      </td>
                      <td className="py-3 px-4 text-slate-600 font-mono">
                        ±{log.accuracy_tolerance}°C (uncert. ±{log.measurement_uncertainty}°C)
                      </td>
                      <td className="py-3 px-4 font-semibold text-slate-700">
                        {log.battery_status}%
                      </td>
                      <td className="py-3 px-4">
                        <StatusBadge status={isExpired ? 'EXPIRED' : log.logger_status} />
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
