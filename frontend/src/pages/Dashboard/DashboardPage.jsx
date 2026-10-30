import React, { useState, useEffect } from 'react';
import {
  Truck,
  ShieldCheck,
  ShieldAlert,
  AlertOctagon,
  Radio,
  Clock,
  RefreshCw,
  TrendingUp,
  Download,
  Activity,
  Layers,
  Thermometer
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import apiClient from '../../services/api';
import PageHeader from '../../components/common/PageHeader';
import StatCard from '../../components/dashboard/StatCard';
import StatusBadge from '../../components/common/StatusBadge';

export default function DashboardPage() {
  const [overview, setOverview] = useState(null);
  const [complianceSummary, setComplianceSummary] = useState([]);
  const [excursionSummary, setExcursionSummary] = useState([]);
  const [carrierMetrics, setCarrierMetrics] = useState([]);
  const [routeDwell, setRouteDwell] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [ovRes, compRes, excRes, carrRes, dwellRes] = await Promise.all([
        apiClient.get('/dashboard/overview'),
        apiClient.get('/dashboard/compliance-summary'),
        apiClient.get('/dashboard/excursion-summary'),
        apiClient.get('/dashboard/shipment-trends'),
        apiClient.get('/dashboard/temperature-trends'),
      ]);

      if (ovRes.success) setOverview(ovRes.data);
      if (compRes.success) setComplianceSummary(compRes.data);
      if (excRes.success) setExcursionSummary(excRes.data);
      if (carrRes.success) setCarrierMetrics(carrRes.data);
      if (dwellRes.success) setRouteDwell(dwellRes.data);
    } catch (err) {
      console.error('Failed to load dashboard metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const COMPLIANCE_COLORS = {
    COMPLIANT: '#16A34A',
    NON_COMPLIANT: '#DC2626',
    INCONCLUSIVE: '#F59E0B',
    UNDER_REVIEW: '#2563EB',
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Executive Intelligence Dashboard"
        subtitle="Real-time pharmaceutical cold chain telemetry, temperature compliance, and exception analytics"
        actions={
          <button
            onClick={fetchDashboardData}
            disabled={loading}
            className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-white border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 shadow-sm transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-blue-600' : ''}`} />
            Refresh Data
          </button>
        }
      />

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Shipments"
          value={overview?.total_shipments ?? 0}
          icon={Truck}
          color="blue"
          subtitle={`${overview?.active_shipments ?? 0} active in transit`}
        />
        <StatCard
          title="Compliant Shipments"
          value={overview?.compliant_shipments ?? 0}
          icon={ShieldCheck}
          color="emerald"
          trend={`${overview?.compliance_rate ?? 0}% Rate`}
          subtitle="Meets all temperature policies"
        />
        <StatCard
          title="Non-Compliant Excursions"
          value={overview?.non_compliant_shipments ?? 0}
          icon={ShieldAlert}
          color="rose"
          subtitle={`${overview?.critical_excursions ?? 0} critical violations`}
        />
        <StatCard
          title="Inconclusive & Gaps"
          value={overview?.inconclusive_shipments ?? 0}
          icon={AlertOctagon}
          color="amber"
          subtitle={`${overview?.missing_telemetry_readings ?? 0} missing telemetry intervals`}
        />
      </div>

      {/* Secondary KPI Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 rounded-lg bg-teal-50 text-teal-600 border border-teal-100">
            <Thermometer className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-500 font-medium">Telemetry Readings Ingested</div>
            <div className="text-xl font-bold text-slate-900">
              {overview?.total_telemetry_readings?.toLocaleString() ?? 0}
            </div>
            <div className="text-[11px] text-teal-600 font-medium">10-minute automated logging</div>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 rounded-lg bg-blue-50 text-blue-600 border border-blue-100">
            <Radio className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-500 font-medium">Under Investigation</div>
            <div className="text-xl font-bold text-slate-900">
              {overview?.under_review_shipments ?? 0}
            </div>
            <div className="text-[11px] text-blue-600 font-medium">Custody gaps & unassigned loggers</div>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 rounded-lg bg-amber-50 text-amber-600 border border-amber-100">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-500 font-medium">Calibration Attention</div>
            <div className="text-xl font-bold text-slate-900">
              {overview?.logger_calibration_issues ?? 0}
            </div>
            <div className="text-[11px] text-amber-600 font-medium">Loggers requiring recertification</div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Compliance Distribution Chart */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h2 className="text-sm font-bold text-slate-900 mb-1">Compliance Decision Distribution</h2>
          <p className="text-xs text-slate-500 mb-4">Evidence-based distribution across all completed shipment journeys</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={complianceSummary}
                  dataKey="count"
                  nameKey="status"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  innerRadius={45}
                  paddingAngle={4}
                  label={({ status, percent }) => `${status} (${(percent * 100).toFixed(0)}%)`}
                >
                  {complianceSummary.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COMPLIANCE_COLORS[entry.status] || '#94A3B8'}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Excursions by Product Chart */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h2 className="text-sm font-bold text-slate-900 mb-1">Temperature Excursions by Product</h2>
          <p className="text-xs text-slate-500 mb-4">Observed excursions exceeding upper or lower validated thresholds</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={excursionSummary} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="product_name" tick={{ fontSize: 10 }} interval={0} angle={-15} textAnchor="end" />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="excursion_count" name="Excursions" fill="#2563EB" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Carrier Performance & Route Dwell Table */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Carrier Reliability */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h2 className="text-sm font-bold text-slate-900 mb-1">Carrier Reliability & Risk Rating</h2>
          <p className="text-xs text-slate-500 mb-4">Compliance score and violation rate tracked by freight carrier</p>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 border-y border-slate-200">
                <tr>
                  <th className="py-2.5 px-3 font-semibold">Carrier</th>
                  <th className="py-2.5 px-3 font-semibold">Shipments</th>
                  <th className="py-2.5 px-3 font-semibold">Compliance %</th>
                  <th className="py-2.5 px-3 font-semibold">Risk Rating</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {carrierMetrics.map((c, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/50">
                    <td className="py-2.5 px-3 font-medium text-slate-900">{c.carrier_name}</td>
                    <td className="py-2.5 px-3 text-slate-600">{c.total_shipments}</td>
                    <td className="py-2.5 px-3 font-semibold text-slate-800">{c.compliance_score}%</td>
                    <td className="py-2.5 px-3">
                      <StatusBadge status={c.risk_rating} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Route Dwell Time Breakdown */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h2 className="text-sm font-bold text-slate-900 mb-1">Transit Dwell Duration Analysis</h2>
          <p className="text-xs text-slate-500 mb-4">Average dwell duration in minutes across transit hubs, airports, and warehouses</p>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={routeDwell} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="stop_type" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="average_dwell_minutes" name="Avg Dwell (min)" fill="#0D9488" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
