import React, { useState, useEffect } from 'react';
import { Sliders, Search, ShieldCheck } from 'lucide-react';
import apiClient from '../../services/api';
import PageHeader from '../../components/common/PageHeader';
import StatusBadge from '../../components/common/StatusBadge';

export default function ThresholdPoliciesPage() {
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchPolicies = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/policies');
      if (res.success) setPolicies(res.data);
    } catch (err) {
      console.error('Failed to load threshold policies:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPolicies();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Temperature Threshold Policies"
        subtitle="Versioned temperature tolerances, minimum and maximum bounds, and allowed excursion durations"
      />

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
              <tr>
                <th className="py-3 px-4 font-semibold">Policy ID</th>
                <th className="py-3 px-4 font-semibold">Product ID</th>
                <th className="py-3 px-4 font-semibold">Temperature Limits</th>
                <th className="py-3 px-4 font-semibold">Allowed Excursion (mins)</th>
                <th className="py-3 px-4 font-semibold">Version</th>
                <th className="py-3 px-4 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {policies.map((pol) => (
                <tr key={pol.policy_id} className="hover:bg-slate-50">
                  <td className="py-3 px-4 font-mono font-bold text-blue-600">{pol.policy_id}</td>
                  <td className="py-3 px-4 font-semibold text-slate-900">{pol.product_id}</td>
                  <td className="py-3 px-4 font-bold text-blue-700">
                    {pol.minimum_temperature}°C to {pol.maximum_temperature}°C
                  </td>
                  <td className="py-3 px-4 text-slate-800 font-semibold">{pol.allowed_excursion_duration} mins</td>
                  <td className="py-3 px-4 font-mono text-slate-600">{pol.policy_version}</td>
                  <td className="py-3 px-4">
                    <StatusBadge status={pol.policy_status} />
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
