import React, { useState, useEffect } from 'react';
import { Box, Plus, Search, ShieldCheck, Clock, X } from 'lucide-react';
import apiClient from '../../services/api';
import PageHeader from '../../components/common/PageHeader';
import StatusBadge from '../../components/common/StatusBadge';

export default function PackagingPage() {
  const [packagings, setPackagings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchPackaging = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/packaging');
      if (res.success) setPackagings(res.data);
    } catch (err) {
      console.error('Failed to load packaging:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPackaging();
  }, []);

  const filtered = packagings.filter((p) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return p.packaging_name?.toLowerCase().includes(q) || p.packaging_id?.toLowerCase().includes(q) || p.insulation_type?.toLowerCase().includes(q);
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Thermal Packaging & Shippers"
        subtitle="Passive & active cold chain shippers, vacuum insulated panels, and validated durations"
      />

      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search packaging unit..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          />
        </div>
        <span className="text-xs text-slate-500 font-medium">{filtered.length} packaging units</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {loading ? (
          <div className="col-span-full py-12 text-center text-slate-400 text-xs">Loading packaging catalog...</div>
        ) : (
          filtered.map((pkg) => (
            <div key={pkg.packaging_id} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition">
              <div className="flex items-start justify-between">
                <div>
                  <span className="font-mono text-[11px] font-bold text-blue-600">{pkg.packaging_id}</span>
                  <h3 className="text-sm font-bold text-slate-900 mt-0.5">{pkg.packaging_name}</h3>
                </div>
                <StatusBadge status={pkg.status || 'QUALIFIED'} />
              </div>

              <div className="mt-4 p-3 rounded-lg bg-teal-50/50 border border-teal-100 flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-700">Validated Transit</span>
                <span className="font-bold text-teal-700 flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  {pkg.validated_duration} hours
                </span>
              </div>

              <div className="mt-3 space-y-1 text-xs text-slate-500">
                <div>
                  Thermal Bound: <span className="font-semibold text-slate-800">{pkg.minimum_temperature}°C to {pkg.maximum_temperature}°C</span>
                </div>
                <div>
                  Insulation: <span className="font-semibold text-slate-800">{pkg.insulation_type}</span>
                </div>
                <div>
                  Container Type: <span className="font-semibold text-slate-800">{pkg.packaging_type}</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
