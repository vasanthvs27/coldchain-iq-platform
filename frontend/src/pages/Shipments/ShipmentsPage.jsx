import React, { useState, useEffect } from 'react';
import {
  Truck,
  Search,
  Filter,
  Plus,
  Eye,
  FileCheck,
  ChevronRight,
  X,
  ThermometerSnowflake,
  MapPin,
  GitCommit,
  Cpu,
  ShieldAlert,
  History,
  Download,
  AlertTriangle,
  Calendar,
  CheckCircle2
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

export default function ShipmentsPage() {
  const [shipments, setShipments] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [statusFilter, setStatusFilter] = useState('');
  const [complianceFilter, setComplianceFilter] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  // Detail Modal / Drawer state
  const [selectedShipmentId, setSelectedShipmentId] = useState(null);
  const [shipmentDetails, setShipmentDetails] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [detailsLoading, setDetailsLoading] = useState(false);

  // Create Shipment Modal
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newShipment, setNewShipment] = useState({
    shipment_id: '',
    product_id: 'PROD-002',
    lot_id: '',
    packaging_id: 'PKG-001',
    origin: 'Boston, MA',
    destination: 'Basel, CH',
    carrier_name: 'FedEx ColdChain Direct',
    planned_departure: new Date().toISOString().substring(0, 16),
    expected_arrival: new Date(Date.now() + 86400000).toISOString().substring(0, 16)
  });
  const [products, setProducts] = useState([]);
  const [lots, setLots] = useState([]);
  const [packagings, setPackagings] = useState([]);

  const fetchShipments = async () => {
    setLoading(true);
    try {
      const params = {
        page,
        page_size: pageSize,
      };
      if (statusFilter) params.status = statusFilter;
      if (complianceFilter) params.compliance = complianceFilter;

      const res = await apiClient.get('/shipments', { params });
      if (res.success) {
        setShipments(res.data);
        setTotal(res.meta?.total || res.data.length);
      }
    } catch (err) {
      console.error('Failed to load shipments:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShipments();
  }, [page, statusFilter, complianceFilter]);

  const loadReferenceData = async () => {
    try {
      const [pRes, lRes, pkgRes] = await Promise.all([
        apiClient.get('/products'),
        apiClient.get('/lots'),
        apiClient.get('/packaging'),
      ]);
      if (pRes.success) setProducts(pRes.data);
      if (lRes.success) setLots(lRes.data);
      if (pkgRes.success) setPackagings(pkgRes.data);
    } catch (err) {
      console.error('Error loading reference data:', err);
    }
  };

  const openDetails = async (shipmentId) => {
    setSelectedShipmentId(shipmentId);
    setActiveTab('overview');
    setDetailsLoading(true);
    try {
      const res = await apiClient.get(`/shipments/${shipmentId}/timeline`);
      if (res.success) {
        setShipmentDetails(res.data);
      }
    } catch (err) {
      console.error('Failed to load shipment details bundle:', err);
    } finally {
      setDetailsLoading(false);
    }
  };

  const handleCreateShipment = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...newShipment,
        shipment_id: newShipment.shipment_id || `SHP-2026-${Math.floor(100000 + Math.random() * 900000)}`,
        planned_departure: new Date(newShipment.planned_departure).toISOString(),
        expected_arrival: new Date(newShipment.expected_arrival).toISOString(),
      };
      const res = await apiClient.post('/shipments', payload);
      if (res.success) {
        setCreateModalOpen(false);
        fetchShipments();
      }
    } catch (err) {
      alert(`Creation error: ${err.message}`);
    }
  };

  const filteredShipments = shipments.filter((s) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      s.shipment_id?.toLowerCase().includes(q) ||
      s.origin?.toLowerCase().includes(q) ||
      s.destination?.toLowerCase().includes(q) ||
      s.carrier_name?.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Shipment Management & Integrity Tracking"
        subtitle="End-to-end journey compliance, temperature telemetry, route dwell, and chain-of-custody"
        actions={
          <button
            onClick={() => {
              loadReferenceData();
              setCreateModalOpen(true);
            }}
            className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition"
          >
            <Plus className="w-4 h-4" />
            Dispatch New Shipment
          </button>
        }
      />

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by ID, Origin, Dest, Carrier..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          />
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs border border-slate-200 rounded-lg px-2.5 py-2 text-slate-700 bg-white focus:outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="">All Shipment Statuses</option>
            <option value="SCHEDULED">SCHEDULED</option>
            <option value="IN_TRANSIT">IN_TRANSIT</option>
            <option value="DELIVERED">DELIVERED</option>
            <option value="QUARANTINED">QUARANTINED</option>
          </select>

          {/* Compliance Filter */}
          <select
            value={complianceFilter}
            onChange={(e) => {
              setComplianceFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs border border-slate-200 rounded-lg px-2.5 py-2 text-slate-700 bg-white focus:outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="">All Compliance Statuses</option>
            <option value="COMPLIANT">COMPLIANT</option>
            <option value="NON_COMPLIANT">NON_COMPLIANT</option>
            <option value="INCONCLUSIVE">INCONCLUSIVE</option>
            <option value="UNDER_REVIEW">UNDER_REVIEW</option>
          </select>
        </div>
      </div>

      {/* Shipments Data Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
              <tr>
                <th className="py-3 px-4 font-semibold">Shipment ID</th>
                <th className="py-3 px-4 font-semibold">Product & Lot</th>
                <th className="py-3 px-4 font-semibold">Route (Origin → Dest)</th>
                <th className="py-3 px-4 font-semibold">Carrier</th>
                <th className="py-3 px-4 font-semibold">Departure</th>
                <th className="py-3 px-4 font-semibold">Shipment Status</th>
                <th className="py-3 px-4 font-semibold">Compliance Status</th>
                <th className="py-3 px-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="8" className="text-center py-10 text-slate-400">
                    Loading shipment registry...
                  </td>
                </tr>
              ) : filteredShipments.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center py-10 text-slate-400">
                    No shipments found matching criteria.
                  </td>
                </tr>
              ) : (
                filteredShipments.map((s) => (
                  <tr key={s.shipment_id} className="hover:bg-slate-50/60 transition">
                    <td className="py-3 px-4 font-mono font-semibold text-blue-600">
                      {s.shipment_id}
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-900">{s.product_name || s.product_id}</div>
                      <div className="text-[10px] text-slate-400 font-mono">{s.lot_id}</div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="text-slate-800 font-medium">{s.origin}</div>
                      <div className="text-[11px] text-slate-500">→ {s.destination}</div>
                    </td>
                    <td className="py-3 px-4 text-slate-600">{s.carrier_name}</td>
                    <td className="py-3 px-4 text-slate-500">
                      {s.planned_departure ? new Date(s.planned_departure).toLocaleDateString() : '—'}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={s.shipment_status} />
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={s.compliance_status} />
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => openDetails(s.shipment_id)}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 font-semibold text-[11px] transition"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="p-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <span>Showing {filteredShipments.length} of {total} shipments</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="px-2.5 py-1 rounded border border-slate-200 disabled:opacity-40"
            >
              Previous
            </button>
            <span className="font-semibold text-slate-700">Page {page}</span>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={page * pageSize >= total}
              className="px-2.5 py-1 rounded border border-slate-200 disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {/* Comprehensive Shipment Inspection Drawer / Modal */}
      {selectedShipmentId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-900/60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-5xl max-h-[90vh] flex flex-col overflow-hidden border border-slate-200 animate-in fade-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/50">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-blue-600 text-white">
                  <Truck className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-base font-bold text-slate-900 font-mono">{selectedShipmentId}</h2>
                    {shipmentDetails?.overview && (
                      <StatusBadge status={shipmentDetails.overview.compliance_status} />
                    )}
                  </div>
                  <p className="text-xs text-slate-500">
                    {shipmentDetails?.overview?.product?.product_name || 'Temperature Sensitive Biologic'} • Lot:{' '}
                    {shipmentDetails?.overview?.lot_id}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedShipmentId(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Navigation Tabs */}
            <div className="flex border-b border-slate-200 px-6 bg-white overflow-x-auto gap-4 text-xs font-semibold">
              {[
                { id: 'overview', label: 'Overview', icon: Truck },
                { id: 'temperature', label: 'Temperature History', icon: ThermometerSnowflake },
                { id: 'route', label: 'Route & Stops', icon: MapPin },
                { id: 'custody', label: 'Custody Chain', icon: GitCommit },
                { id: 'loggers', label: 'Loggers', icon: Cpu },
                { id: 'excursions', label: 'Excursions', icon: ShieldAlert },
                { id: 'compliance', label: 'Compliance Report', icon: FileCheck },
                { id: 'audit', label: 'Audit Trail', icon: History },
              ].map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-2 py-3 border-b-2 font-medium transition whitespace-nowrap ${
                      isActive
                        ? 'border-blue-600 text-blue-600 font-bold'
                        : 'border-transparent text-slate-500 hover:text-slate-800'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {tab.label}
                  </button>
                );
              })}
            </div>

            {/* Tab Body Viewport */}
            <div className="flex-1 overflow-y-auto p-6 bg-slate-50/50">
              {detailsLoading ? (
                <div className="text-center py-20 text-slate-400">Loading comprehensive timeline...</div>
              ) : (
                <>
                  {/* TAB 1: OVERVIEW */}
                  {activeTab === 'overview' && (
                    <div className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-white p-4 rounded-xl border border-slate-200">
                          <span className="text-xs font-semibold text-slate-500">Product Profile</span>
                          <div className="text-sm font-bold text-slate-900 mt-1">
                            {shipmentDetails?.overview?.product?.product_name}
                          </div>
                          <div className="text-xs text-slate-500 mt-0.5">
                            Category: {shipmentDetails?.overview?.product?.product_category}
                          </div>
                          <div className="mt-2 text-xs font-semibold text-blue-600">
                            Required: {shipmentDetails?.overview?.product?.minimum_temperature}°C to{' '}
                            {shipmentDetails?.overview?.product?.maximum_temperature}°C
                          </div>
                        </div>

                        <div className="bg-white p-4 rounded-xl border border-slate-200">
                          <span className="text-xs font-semibold text-slate-500">Route & Carrier</span>
                          <div className="text-sm font-bold text-slate-900 mt-1">
                            {shipmentDetails?.overview?.origin} → {shipmentDetails?.overview?.destination}
                          </div>
                          <div className="text-xs text-slate-500 mt-0.5">
                            Carrier: {shipmentDetails?.overview?.carrier_name}
                          </div>
                          <div className="text-xs text-slate-500 mt-1 font-mono">
                            Dep: {shipmentDetails?.overview?.actual_departure || shipmentDetails?.overview?.planned_departure}
                          </div>
                        </div>

                        <div className="bg-white p-4 rounded-xl border border-slate-200">
                          <span className="text-xs font-semibold text-slate-500">Thermal Packaging</span>
                          <div className="text-sm font-bold text-slate-900 mt-1">
                            {shipmentDetails?.overview?.packaging?.packaging_name}
                          </div>
                          <div className="text-xs text-slate-500 mt-0.5">
                            Type: {shipmentDetails?.overview?.packaging?.packaging_type}
                          </div>
                          <div className="text-xs text-teal-600 font-semibold mt-1">
                            Validated Duration: {shipmentDetails?.overview?.packaging?.validated_duration}h
                          </div>
                        </div>
                      </div>

                      {/* Quick Summary Banner */}
                      <div className="bg-white p-5 rounded-xl border border-slate-200 flex items-center justify-between">
                        <div>
                          <div className="text-xs font-semibold text-slate-500">Formal Compliance Decision</div>
                          <div className="text-lg font-bold text-slate-900 mt-1 flex items-center gap-2">
                            <StatusBadge status={shipmentDetails?.overview?.compliance_status} />
                            <span>Score: {shipmentDetails?.compliance_report?.compliance_score ?? 100}%</span>
                          </div>
                        </div>
                        <button
                          onClick={() => setActiveTab('compliance')}
                          className="px-3 py-1.5 rounded-lg bg-blue-600 text-white text-xs font-semibold hover:bg-blue-700"
                        >
                          View Certified Report
                        </button>
                      </div>
                    </div>
                  )}

                  {/* TAB 2: TEMPERATURE HISTORY */}
                  {activeTab === 'temperature' && (
                    <div className="space-y-4">
                      <div className="bg-white p-5 rounded-xl border border-slate-200">
                        <div className="flex items-center justify-between mb-4">
                          <div>
                            <h3 className="text-sm font-bold text-slate-900">Telemetry Temperature Trend Chart</h3>
                            <p className="text-xs text-slate-500">Timestamped readings with product validation thresholds</p>
                          </div>
                          <div className="flex items-center gap-3 text-xs">
                            <span className="flex items-center gap-1.5 text-blue-600 font-semibold">
                              <span className="w-3 h-0.5 bg-blue-600" /> Temperature
                            </span>
                            <span className="flex items-center gap-1.5 text-rose-500 font-semibold">
                              <span className="w-3 h-0.5 bg-rose-500" /> Thresholds
                            </span>
                          </div>
                        </div>

                        <div className="h-72">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={shipmentDetails?.readings || []}>
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
                              {shipmentDetails?.overview?.product?.minimum_temperature && (
                                <ReferenceLine
                                  y={shipmentDetails.overview.product.minimum_temperature}
                                  stroke="#DC2626"
                                  strokeDasharray="3 3"
                                  label={{ value: 'Min Temp', fill: '#DC2626', fontSize: 10 }}
                                />
                              )}
                              {shipmentDetails?.overview?.product?.maximum_temperature && (
                                <ReferenceLine
                                  y={shipmentDetails.overview.product.maximum_temperature}
                                  stroke="#DC2626"
                                  strokeDasharray="3 3"
                                  label={{ value: 'Max Temp', fill: '#DC2626', fontSize: 10 }}
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

                      {/* Raw Telemetry Table */}
                      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                        <div className="p-3 bg-slate-50 border-b border-slate-200 font-semibold text-xs text-slate-700">
                          Recorded Samples ({shipmentDetails?.readings?.length || 0})
                        </div>
                        <div className="max-h-60 overflow-y-auto">
                          <table className="w-full text-left text-xs">
                            <thead className="bg-slate-50 text-slate-500">
                              <tr>
                                <th className="py-2 px-3">Reading ID</th>
                                <th className="py-2 px-3">Timestamp</th>
                                <th className="py-2 px-3">Measured (°C)</th>
                                <th className="py-2 px-3">Corrected (°C)</th>
                                <th className="py-2 px-3">Uncertainty</th>
                                <th className="py-2 px-3">Status</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                              {shipmentDetails?.readings?.map((r) => (
                                <tr key={r.reading_id} className="hover:bg-slate-50">
                                  <td className="py-1.5 px-3 font-mono text-[11px] text-slate-600">{r.reading_id}</td>
                                  <td className="py-1.5 px-3 text-slate-600">{new Date(r.recorded_at).toLocaleString()}</td>
                                  <td className="py-1.5 px-3 font-semibold text-slate-800">{r.measured_temperature}°C</td>
                                  <td className="py-1.5 px-3 font-semibold text-blue-600">{r.corrected_temperature}°C</td>
                                  <td className="py-1.5 px-3 text-slate-500">±{r.calibration_uncertainty}°C</td>
                                  <td className="py-1.5 px-3">
                                    <StatusBadge status={r.reading_status} />
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* TAB 3: ROUTE & STOPS */}
                  {activeTab === 'route' && (
                    <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
                      <h3 className="text-sm font-bold text-slate-900">Route Waypoints & Dwell Tracking</h3>
                      <div className="space-y-4">
                        {shipmentDetails?.route_stops?.map((stop, idx) => (
                          <div key={stop.route_stop_id} className="flex items-start gap-4 p-3 rounded-lg border border-slate-200/80 bg-slate-50/50">
                            <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold flex items-center justify-center text-xs">
                              {stop.stop_sequence}
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center justify-between">
                                <span className="font-bold text-slate-900 text-xs">{stop.stop_name}</span>
                                <StatusBadge status={stop.status} />
                              </div>
                              <div className="text-xs text-slate-500 mt-1">
                                Type: <span className="font-semibold text-slate-700">{stop.stop_type}</span> • Dwell:{' '}
                                <span className={`font-semibold ${stop.dwell_duration > 240 ? 'text-rose-600' : 'text-slate-700'}`}>
                                  {stop.dwell_duration} mins
                                </span>
                              </div>
                              <div className="text-[11px] text-slate-400 mt-0.5">
                                Arr: {new Date(stop.planned_arrival).toLocaleString()} • Dep:{' '}
                                {stop.departure_time ? new Date(stop.departure_time).toLocaleString() : 'In Progress'}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* TAB 4: CUSTODY TIMELINE */}
                  {activeTab === 'custody' && (
                    <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
                      <h3 className="text-sm font-bold text-slate-900">Chain of Custody Verification</h3>
                      <div className="space-y-3">
                        {shipmentDetails?.custody_events?.map((ev) => (
                          <div key={ev.custody_event_id} className="p-3 rounded-lg border border-slate-200 flex items-center justify-between">
                            <div>
                              <div className="text-xs font-bold text-slate-900">{ev.event_type}</div>
                              <div className="text-xs text-slate-600 mt-0.5">
                                <span className="font-semibold">{ev.previous_custodian}</span> →{' '}
                                <span className="font-semibold">{ev.new_custodian}</span>
                              </div>
                              <div className="text-[11px] text-slate-400">
                                Location: {ev.location} • {new Date(ev.handoff_timestamp).toLocaleString()}
                              </div>
                            </div>
                            <div className="text-right">
                              <StatusBadge status={ev.verification_status} />
                              <div className="text-[10px] text-slate-400 mt-1">{ev.acknowledgement_status}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* TAB 5: LOGGERS */}
                  {activeTab === 'loggers' && (
                    <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
                      <h3 className="text-sm font-bold text-slate-900">Assigned Loggers</h3>
                      <div className="space-y-3">
                        {shipmentDetails?.loggers?.map((l) => (
                          <div key={l.assignment_id} className="p-3 rounded-lg border border-slate-200 flex items-center justify-between">
                            <div>
                              <div className="font-mono text-xs font-bold text-blue-600">{l.logger_id}</div>
                              <div className="text-xs text-slate-500">
                                Assigned: {new Date(l.assigned_at).toLocaleString()}
                              </div>
                              <div className="text-[11px] text-slate-400">{l.assignment_notes}</div>
                            </div>
                            <StatusBadge status={l.status} />
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* TAB 6: EXCURSIONS */}
                  {activeTab === 'excursions' && (
                    <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
                      <h3 className="text-sm font-bold text-slate-900">Observed Temperature Excursions</h3>
                      {shipmentDetails?.excursions?.length === 0 ? (
                        <div className="text-center py-10 text-emerald-600 text-xs font-semibold">
                          ✓ No temperature excursions detected during this journey.
                        </div>
                      ) : (
                        <div className="space-y-3">
                          {shipmentDetails?.excursions?.map((ex) => (
                            <div key={ex.excursion_id} className="p-4 rounded-xl border border-rose-200 bg-rose-50/30">
                              <div className="flex items-center justify-between">
                                <span className="font-mono text-xs font-bold text-rose-700">{ex.excursion_id}</span>
                                <StatusBadge status={ex.severity} />
                              </div>
                              <div className="text-xs text-slate-800 font-semibold mt-1">
                                {ex.issue_type} • Duration: {ex.calculated_duration} mins
                              </div>
                              <div className="text-xs text-slate-600 mt-0.5">
                                Observed Range: [{ex.minimum_observed_temperature}°C, {ex.maximum_observed_temperature}°C]
                              </div>
                              <div className="text-[11px] text-slate-500 mt-2 font-mono">
                                Evidence: {ex.evidence_reference}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* TAB 7: COMPLIANCE REPORT */}
                  {activeTab === 'compliance' && (
                    <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-6">
                      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
                        <div>
                          <h3 className="text-base font-bold text-slate-900 font-mono">
                            {shipmentDetails?.compliance_report?.report_id || `COMP-${selectedShipmentId}`}
                          </h3>
                          <p className="text-xs text-slate-500">
                            Formal 12-Step Compliance Intelligence Certificate • Policy {shipmentDetails?.compliance_report?.policy_version}
                          </p>
                        </div>
                        <StatusBadge status={shipmentDetails?.compliance_report?.compliance_status} />
                      </div>

                      {/* Score Cards */}
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                        <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                          <span className="text-[11px] text-slate-500">Compliance Score</span>
                          <div className="text-lg font-bold text-slate-900">
                            {shipmentDetails?.compliance_report?.compliance_score}%
                          </div>
                        </div>
                        <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                          <span className="text-[11px] text-slate-500">Total / Missing Readings</span>
                          <div className="text-lg font-bold text-slate-900">
                            {shipmentDetails?.compliance_report?.total_readings} /{' '}
                            {shipmentDetails?.compliance_report?.missing_readings}
                          </div>
                        </div>
                        <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                          <span className="text-[11px] text-slate-500">Max Excursion Duration</span>
                          <div className="text-lg font-bold text-slate-900">
                            {shipmentDetails?.compliance_report?.maximum_excursion_duration} mins
                          </div>
                        </div>
                        <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                          <span className="text-[11px] text-slate-500">Custody Completeness</span>
                          <div className="text-lg font-bold text-slate-900">
                            {shipmentDetails?.compliance_report?.custody_completeness}%
                          </div>
                        </div>
                      </div>

                      {/* Reason Codes */}
                      <div>
                        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                          Evaluated Reason Codes
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {shipmentDetails?.compliance_report?.reason_codes?.length === 0 ? (
                            <span className="text-xs text-emerald-600 font-medium">✓ No violations flagged</span>
                          ) : (
                            shipmentDetails?.compliance_report?.reason_codes?.map((rc, idx) => (
                              <span key={idx} className="px-2.5 py-1 rounded bg-amber-50 text-amber-800 border border-amber-200 text-xs font-mono font-semibold">
                                {rc}
                              </span>
                            ))
                          )}
                        </div>
                      </div>

                      {/* Traceable Evidence References */}
                      <div>
                        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                          Traceable Evidence References
                        </h4>
                        <div className="space-y-1.5">
                          {shipmentDetails?.compliance_report?.evidence_references?.map((ev, idx) => (
                            <div key={idx} className="text-xs bg-slate-50 p-2.5 rounded border border-slate-200 text-slate-700 font-mono">
                              • {ev}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* TAB 8: AUDIT HISTORY */}
                  {activeTab === 'audit' && (
                    <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
                      <h3 className="text-sm font-bold text-slate-900">Immutable Audit Trail</h3>
                      <div className="space-y-2">
                        {shipmentDetails?.audit_history?.length === 0 ? (
                          <div className="text-xs text-slate-500 py-4 text-center">No historical updates recorded.</div>
                        ) : (
                          shipmentDetails?.audit_history?.map((a) => (
                            <div key={a.event_id} className="p-3 rounded border border-slate-200 text-xs text-slate-700">
                              <span className="font-semibold text-slate-900">{a.action}</span> by user {a.user_id} on{' '}
                              {new Date(a.created_at).toLocaleString()}
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Dispatch New Shipment Modal */}
      {createModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-900/60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-6 border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between pb-4 border-b border-slate-200">
              <h3 className="text-base font-bold text-slate-900">Dispatch New Shipment</h3>
              <button onClick={() => setCreateModalOpen(false)} className="text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateShipment} className="space-y-4 mt-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Product</label>
                <select
                  value={newShipment.product_id}
                  onChange={(e) => {
                    const pid = e.target.value;
                    const matchingLots = lots.filter((l) => l.product_id === pid);
                    setNewShipment({
                      ...newShipment,
                      product_id: pid,
                      lot_id: matchingLots[0]?.lot_id || '',
                    });
                  }}
                  className="w-full border border-slate-200 rounded-lg p-2 focus:ring-2 focus:ring-blue-500/20"
                >
                  {products.map((p) => (
                    <option key={p.product_id} value={p.product_id}>
                      {p.product_name} ({p.minimum_temperature}°C to {p.maximum_temperature}°C)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Manufactured Lot</label>
                <select
                  value={newShipment.lot_id}
                  onChange={(e) => setNewShipment({ ...newShipment, lot_id: e.target.value })}
                  className="w-full border border-slate-200 rounded-lg p-2 focus:ring-2 focus:ring-blue-500/20"
                  required
                >
                  <option value="">Select Lot</option>
                  {lots
                    .filter((l) => l.product_id === newShipment.product_id)
                    .map((l) => (
                      <option key={l.lot_id} value={l.lot_id}>
                        {l.lot_id} ({l.supplier_name})
                      </option>
                    ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Thermal Packaging</label>
                <select
                  value={newShipment.packaging_id}
                  onChange={(e) => setNewShipment({ ...newShipment, packaging_id: e.target.value })}
                  className="w-full border border-slate-200 rounded-lg p-2 focus:ring-2 focus:ring-blue-500/20"
                >
                  {packagings.map((pkg) => (
                    <option key={pkg.packaging_id} value={pkg.packaging_id}>
                      {pkg.packaging_name} ({pkg.validated_duration}h validated)
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Origin</label>
                  <input
                    type="text"
                    value={newShipment.origin}
                    onChange={(e) => setNewShipment({ ...newShipment, origin: e.target.value })}
                    className="w-full border border-slate-200 rounded-lg p-2"
                    required
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Destination</label>
                  <input
                    type="text"
                    value={newShipment.destination}
                    onChange={(e) => setNewShipment({ ...newShipment, destination: e.target.value })}
                    className="w-full border border-slate-200 rounded-lg p-2"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Carrier Name</label>
                <input
                  type="text"
                  value={newShipment.carrier_name}
                  onChange={(e) => setNewShipment({ ...newShipment, carrier_name: e.target.value })}
                  className="w-full border border-slate-200 rounded-lg p-2"
                  required
                />
              </div>

              <div className="flex justify-end gap-2 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setCreateModalOpen(false)}
                  className="px-4 py-2 rounded-lg border border-slate-200 text-slate-600 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700"
                >
                  Confirm Dispatch
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
