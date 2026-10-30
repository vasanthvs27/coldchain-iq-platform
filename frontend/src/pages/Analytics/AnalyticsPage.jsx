import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, ThermometerSnowflake, FileCheck, Truck } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import apiClient from '../../services/api';
import PageHeader from '../../components/common/PageHeader';

export default function AnalyticsPage() {
  const [carrierData, setCarrierData] = useState([]);
  const [excursionsData, setExcursionsData] = useState([]);

  useEffect(() => {
    const fetchAnalytics = async () => {
      const [cRes, eRes] = await Promise.all([
        apiClient.get('/analytics/carriers'),
        apiClient.get('/analytics/excursions')
      ]);
      if (cRes.success) setCarrierData(cRes.data);
      if (eRes.success) setExcursionsData(eRes.data);
    };
    fetchAnalytics();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Predictive Cold Chain Analytics & Multi-Lane Insights"
        subtitle="Long-term temperature deviation distributions, carrier scorecard comparisons, and lane performance"
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900">Carrier Compliance Comparison (%)</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={carrierData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="carrier_name" tick={{ fontSize: 10 }} angle={-15} textAnchor="end" />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="compliance_score" name="Compliance %" fill="#2563EB" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900">Total Excursions by Product Formulation</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={excursionsData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="product_name" tick={{ fontSize: 10 }} angle={-15} textAnchor="end" />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="excursion_count" name="Excursions" fill="#0D9488" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
