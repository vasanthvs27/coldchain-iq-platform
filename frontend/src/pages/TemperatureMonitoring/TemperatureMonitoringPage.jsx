import React, { useState, useEffect } from 'react';
import {
  ThermometerSnowflake,
  Search,
  Filter,
  RefreshCw,
  AlertTriangle,
  Radio,
  X
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import apiClient from '../../services/api';
import PageHeader from '../../components/common/PageHeader';
import StatusBadge from '../../components/common/StatusBadge';

export default function TemperatureMonitoringPage() {
  const [readings, setReadings] = useState([]);
  const [shipments, setShipments] = useState([]);
  const [selectedShipment, setSelectedShipment] = useState('');
  const [trendData, setTrendData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedReading, setSelectedReading] = useState(null);

  const loadShipments = async () => {
    try {
      const res = await apiClient.get('/shipments', { params: { page_size: 50 } });
      if (res.success && res.data.length > 0) {
        setShipments(res.data);
        setSelectedShipment(res.data[0].shipment_id);
      }
    } catch (err) {
      console.error('Error fetching shipments:', err);
    }
  };

  const loadTrendsAndReadings = async (shipmentId) => {
    if (!shipmentId) return;
    setLoading(true);
    try {
      const [trendRes, readRes] = await Promise.all([
        apiClient.get(`/temperature/shipments/${shipmentId}/trends`),
        apiClient.get('/temperature/readings', { params: { shipment_id: shipmentId, page_size: 100 } }),
      ]);
      if (trendRes.success) setTrendData(trendRes.data);
      if (readRes.success) setReadings(readRes.data);
    } catch (err) {
      console.error('Error loading temperature telemetry:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadShipments();
  }, []);

  useEffect(() => {
    if (selectedShipment) {
      loadTrendsAndReadings(selectedShipment);
    }
  }, [selectedShipment]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Active Temperature Telemetry & Sensor Monitoring"
        subtitle="10-minute automated logger pings, threshold boundaries, excursion markers, and gap intervals"
        actions={
          <div className="flex items-center gap-3">
            <select
              value={selectedShipment}
              onChange={(e) => setSelectedShipment(e.target.value)}
              className="text-xs border border-slate-200 rounded-lg px-3 py-2 bg-white font-semibold text-slate-800 focus:outline-none focus:border-blue-500 shadow-sm"
            >
              {shipments.map((s) => (
                <option key={s.shipment_id} value={s.shipment_id}>
                  {s.shipment_id} ({s.origin} → {s.destination})
                </option>
              ))}
            </select>
            <button
              onClick={() => loadTrendsAndReadings(selectedShipment)}
              disabled={loading}
              className="p-2 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 shadow-sm"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-600' : ''}`} />
            </button>
          </div>
        }
      />

      {/* Stats Header Bar */}
      {trendData?.stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-xl border border-slate-200">
            <span className="text-[11px] text-slate-500 font-medium">Readings Sampled</span>
            <div className="text-xl font-bold text-slate-900 mt-1">{trendData.stats.count}</div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200">
            <span className="text-[11px] text-slate-500 font-medium">Min / Max Observed</span>
            <div className="text-xl font-bold text-slate-900 mt-1">
              {trendData.stats.min_temp}°C / {trendData.stats.max_temp}°C
            </div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200">
            <span className="text-[11px] text-slate-500 font-medium">Average Journey Temp</span>
            <div className="text-xl font-bold text-blue-600 mt-1">{trendData.stats.avg_temp}°C</div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200">
            <span className="text-[11px] text-slate-500 font-medium">Validated Threshold</span>
            <div className="text-sm font-bold text-slate-800 mt-2">
              [{trendData.stats.target_min}°C, {trendData.stats.target_max}°C]
            </div>
          </div>
        </div>
      )}

      {/* Main Interactive Chart */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="text-sm font-bold text-slate-900">
              Shipment {selectedShipment} Telemetry Trend
            </h3>
            <p className="text-xs text-slate-500">
              Product: {trendData?.product?.product_name || 'Biologic'} • Range:{' '}
              {trendData?.stats?.target_min}°C to {trendData?.stats?.target_max}°C
            </p>
          </div>
          <div className="flex items-center gap-4 text-xs font-semibold">
            <span className="flex items-center gap-1.5 text-blue-600">
              <span className="w-3 h-0.5 bg-blue-600" /> Sensor Temperature
            </span>
            <span className="flex items-center gap-1.5 text-rose-600">
              <span className="w-3 h-0.5 bg-rose-600" /> Upper/Lower Threshold
            </span>
          </div>
        </div>

        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trendData?.readings || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis
                dataKey="recorded_at"
                tickFormatter={(v) => v ? v.substring(11, 16) : ''}
                tick={{ fontSize: 10 }}
              />
              <YAxis tick={{ fontSize: 10 }} unit="°C" />
              <Tooltip
                labelFormatter={(v) => `Recorded: ${new Date(v).toLocaleString()}`}
                formatter={(val) => [`${val}°C`, 'Temperature']}
              />
              {trendData?.stats?.target_min !== undefined && (
                <ReferenceLine
                  y={trendData.stats.target_min}
                  stroke="#DC2626"
                  strokeDasharray="4 4"
                  strokeWidth={1.5}
                  label={{ value: `Min ${trendData.stats.target_min}°C`, fill: '#DC2626', fontSize: 10 }}
                />
              )}
              {trendData?.stats?.target_max !== undefined && (
                <ReferenceLine
                  y={trendData.stats.target_max}
                  stroke="#DC2626"
                  strokeDasharray="4 4"
                  strokeWidth={1.5}
                  label={{ value: `Max ${trendData.stats.target_max}°C`, fill: '#DC2626', fontSize: 10 }}
                />
              )}
              <Line
                type="monotone"
                dataKey="corrected_temperature"
                stroke="#2563EB"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Telemetry Readings List & Detail Drawer */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <span className="font-semibold text-xs text-slate-700">Chronological Telemetry Stream</span>
          <span className="text-xs text-slate-500">{readings.length} readings loaded</span>
        </div>
        <div className="overflow-x-auto max-h-96">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 sticky top-0 border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Reading ID</th>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Measured (°C)</th>
                <th className="py-2.5 px-3">Corrected (°C)</th>
                <th className="py-2.5 px-3">Uncertainty</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3 text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {readings.map((r) => (
                <tr key={r.reading_id} className="hover:bg-slate-50/80">
                  <td className="py-2 px-3 font-mono font-medium text-slate-800">{r.reading_id}</td>
                  <td className="py-2 px-3 text-slate-600">{new Date(r.recorded_at).toLocaleString()}</td>
                  <td className="py-2 px-3 font-semibold text-slate-800">{r.measured_temperature}°C</td>
                  <td className="py-2 px-3 font-semibold text-blue-600">{r.corrected_temperature}°C</td>
                  <td className="py-2 px-3 text-slate-500">±{r.calibration_uncertainty}°C</td>
                  <td className="py-2 px-3">
                    <StatusBadge status={r.reading_status} />
                  </td>
                  <td className="py-2 px-3 text-right">
                    <button
                      onClick={() => setSelectedReading(r)}
                      className="text-blue-600 hover:text-blue-800 font-semibold text-[11px]"
                    >
                      Drawer →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Reading Detail Drawer */}
      {selectedReading && (
        <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-96 bg-white shadow-2xl border-l border-slate-200 p-6 flex flex-col justify-between animate-in slide-in-from-right duration-200">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-slate-200">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Telemetry Sample Detail</h3>
                <span className="font-mono text-[11px] text-blue-600 font-semibold">{selectedReading.reading_id}</span>
              </div>
              <button onClick={() => setSelectedReading(null)} className="text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="mt-5 space-y-4 text-xs">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-500 block mb-1">Status & Validity</span>
                <StatusBadge status={selectedReading.reading_status} />
              </div>

              <div>
                <span className="text-slate-500 block">Shipment ID</span>
                <span className="font-mono font-semibold text-slate-900">{selectedReading.shipment_id}</span>
              </div>

              <div>
                <span className="text-slate-500 block">Logger ID</span>
                <span className="font-mono font-semibold text-blue-600">{selectedReading.logger_id}</span>
              </div>

              <div>
                <span className="text-slate-500 block">Recorded At (UTC)</span>
                <span className="font-semibold text-slate-800">{new Date(selectedReading.recorded_at).toISOString()}</span>
              </div>

              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-100">
                <div>
                  <span className="text-slate-500 block">Measured</span>
                  <span className="text-sm font-bold text-slate-800">{selectedReading.measured_temperature}°C</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Corrected</span>
                  <span className="text-sm font-bold text-blue-600">{selectedReading.corrected_temperature}°C</span>
                </div>
              </div>

              <div>
                <span className="text-slate-500 block">Calibration Uncertainty</span>
                <span className="font-semibold text-slate-700">±{selectedReading.calibration_uncertainty}°C</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => setSelectedReading(null)}
            className="w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-lg text-xs"
          >
            Close Drawer
          </button>
        </div>
      )}
    </div>
  );
}
