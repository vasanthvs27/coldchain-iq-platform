import React, { useState, useEffect } from 'react';
import { GitCommit, Search, ShieldCheck, AlertTriangle } from 'lucide-react';
import apiClient from '../../services/api';
import PageHeader from '../../components/common/PageHeader';
import StatusBadge from '../../components/common/StatusBadge';

export default function CustodyEventsPage() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/custody', { params: { page_size: 50 } });
      if (res.success) setEvents(res.data);
    } catch (err) {
      console.error('Failed to load custody events:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Chain of Custody Events & Transfer Audit"
        subtitle="Handoff transactions between suppliers, carriers, customs handlers, and destination receivers"
      />

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 font-semibold text-xs text-slate-700">
          Custody Transfer Records
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
              <tr>
                <th className="py-3 px-4 font-semibold">Event ID</th>
                <th className="py-3 px-4 font-semibold">Shipment ID</th>
                <th className="py-3 px-4 font-semibold">Previous Custodian</th>
                <th className="py-3 px-4 font-semibold">New Custodian</th>
                <th className="py-3 px-4 font-semibold">Location</th>
                <th className="py-3 px-4 font-semibold">Handoff Timestamp</th>
                <th className="py-3 px-4 font-semibold">Event Type</th>
                <th className="py-3 px-4 font-semibold">Verification Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {events.map((ev) => (
                <tr key={ev.custody_event_id} className="hover:bg-slate-50">
                  <td className="py-3 px-4 font-mono font-bold text-blue-600">{ev.custody_event_id}</td>
                  <td className="py-3 px-4 font-mono text-slate-800">{ev.shipment_id}</td>
                  <td className="py-3 px-4 text-slate-700">{ev.previous_custodian}</td>
                  <td className="py-3 px-4 text-slate-900 font-semibold">{ev.new_custodian}</td>
                  <td className="py-3 px-4 text-slate-600">{ev.location}</td>
                  <td className="py-3 px-4 text-slate-500">{new Date(ev.handoff_timestamp).toLocaleString()}</td>
                  <td className="py-3 px-4 font-medium text-slate-800">{ev.event_type}</td>
                  <td className="py-3 px-4">
                    <StatusBadge status={ev.verification_status} />
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
