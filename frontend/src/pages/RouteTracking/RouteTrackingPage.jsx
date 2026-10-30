import React, { useState, useEffect } from 'react';
import { MapPin, Search, Clock, Navigation } from 'lucide-react';
import apiClient from '../../services/api';
import PageHeader from '../../components/common/PageHeader';
import StatusBadge from '../../components/common/StatusBadge';

export default function RouteTrackingPage() {
  const [stops, setStops] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchStops = async () => {
    setLoading(true);
    try {
      const shpRes = await apiClient.get('/shipments', { params: { page_size: 1 } });
      if (shpRes.success && shpRes.data.length > 0) {
        const sid = shpRes.data[0].shipment_id;
        const res = await apiClient.get(`/routes/${sid}`);
        if (res.success) setStops(res.data);
      }
    } catch (err) {
      console.error('Failed to load route stops:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStops();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Route Tracking & Waypoint Dwell Analysis"
        subtitle="Transit stops, chronological sequence, planned vs actual arrival, and excessive dwell duration detection"
      />

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 font-semibold text-xs text-slate-700">
          Route Waypoint Records
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
              <tr>
                <th className="py-3 px-4 font-semibold">Sequence</th>
                <th className="py-3 px-4 font-semibold">Stop ID</th>
                <th className="py-3 px-4 font-semibold">Stop Name</th>
                <th className="py-3 px-4 font-semibold">Stop Type</th>
                <th className="py-3 px-4 font-semibold">Planned Arrival</th>
                <th className="py-3 px-4 font-semibold">Actual Arrival</th>
                <th className="py-3 px-4 font-semibold">Dwell (mins)</th>
                <th className="py-3 px-4 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {stops.map((st) => (
                <tr key={st.route_stop_id} className="hover:bg-slate-50">
                  <td className="py-3 px-4 font-bold text-blue-600">{st.stop_sequence}</td>
                  <td className="py-3 px-4 font-mono text-slate-600">{st.route_stop_id}</td>
                  <td className="py-3 px-4 font-semibold text-slate-900">{st.stop_name}</td>
                  <td className="py-3 px-4 text-slate-700">{st.stop_type}</td>
                  <td className="py-3 px-4 text-slate-500">{new Date(st.planned_arrival).toLocaleString()}</td>
                  <td className="py-3 px-4 text-slate-500">{st.actual_arrival ? new Date(st.actual_arrival).toLocaleString() : '—'}</td>
                  <td className="py-3 px-4 font-bold text-slate-800">
                    <span className={st.dwell_duration > 240 ? 'text-rose-600' : ''}>{st.dwell_duration}m</span>
                  </td>
                  <td className="py-3 px-4">
                    <StatusBadge status={st.status} />
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
