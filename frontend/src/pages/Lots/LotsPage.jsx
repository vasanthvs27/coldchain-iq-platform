import React, { useState, useEffect } from 'react';
import { Boxes, Plus, Search, Calendar, Building2, X } from 'lucide-react';
import apiClient from '../../services/api';
import PageHeader from '../../components/common/PageHeader';
import StatusBadge from '../../components/common/StatusBadge';

export default function LotsPage() {
  const [lots, setLots] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newLot, setNewLot] = useState({
    lot_id: '',
    product_id: 'PROD-001',
    supplier_name: 'BioVax Pharma Ltd',
    manufacturing_date: new Date().toISOString().substring(0, 10),
    expiry_date: new Date(Date.now() + 31536000000).toISOString().substring(0, 10),
    quantity: 15000,
    unit: 'DOSES',
    lifecycle_status: 'RELEASED'
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [lRes, pRes] = await Promise.all([
        apiClient.get('/lots'),
        apiClient.get('/products')
      ]);
      if (lRes.success) setLots(lRes.data);
      if (pRes.success) setProducts(pRes.data);
    } catch (err) {
      console.error('Error fetching lots:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...newLot,
        lot_id: newLot.lot_id || `LOT-2026-${Math.floor(100000 + Math.random() * 900000)}`,
        manufacturing_date: new Date(newLot.manufacturing_date).toISOString(),
        expiry_date: new Date(newLot.expiry_date).toISOString(),
        quantity: parseInt(newLot.quantity),
      };
      const res = await apiClient.post('/lots', payload);
      if (res.success) {
        setCreateModalOpen(false);
        fetchData();
      }
    } catch (err) {
      alert(`Validation error: ${err.message}`);
    }
  };

  const filtered = lots.filter((l) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return l.lot_id?.toLowerCase().includes(q) || l.supplier_name?.toLowerCase().includes(q) || l.product_id?.toLowerCase().includes(q);
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Manufactured Lot & Batch Registry"
        subtitle="Batch traceability, supplier certification, and shelf-life monitoring for pharmaceutical lots"
        actions={
          <button
            onClick={() => setCreateModalOpen(true)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition"
          >
            <Plus className="w-4 h-4" />
            Register Lot
          </button>
        }
      />

      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search lot ID, supplier, or product..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          />
        </div>
        <span className="text-xs text-slate-500 font-medium">{filtered.length} lots registered</span>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
              <tr>
                <th className="py-3 px-4 font-semibold">Lot ID</th>
                <th className="py-3 px-4 font-semibold">Associated Product</th>
                <th className="py-3 px-4 font-semibold">Supplier</th>
                <th className="py-3 px-4 font-semibold">Manufacturing Date</th>
                <th className="py-3 px-4 font-semibold">Expiry Date</th>
                <th className="py-3 px-4 font-semibold">Quantity</th>
                <th className="py-3 px-4 font-semibold">Lifecycle Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="7" className="text-center py-10 text-slate-400">Loading lots...</td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan="7" className="text-center py-10 text-slate-400">No lots found.</td>
                </tr>
              ) : (
                filtered.map((lot) => (
                  <tr key={lot.lot_id} className="hover:bg-slate-50">
                    <td className="py-3 px-4 font-mono font-bold text-blue-600">{lot.lot_id}</td>
                    <td className="py-3 px-4 font-semibold text-slate-900">{lot.product_id}</td>
                    <td className="py-3 px-4 text-slate-700">{lot.supplier_name}</td>
                    <td className="py-3 px-4 text-slate-500">{new Date(lot.manufacturing_date).toLocaleDateString()}</td>
                    <td className="py-3 px-4 text-slate-500">{new Date(lot.expiry_date).toLocaleDateString()}</td>
                    <td className="py-3 px-4 font-semibold text-slate-800">
                      {lot.quantity?.toLocaleString()} {lot.unit}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={lot.lifecycle_status} />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {createModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-900/60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <h3 className="text-base font-bold text-slate-900">Register Manufactured Lot</h3>
              <button onClick={() => setCreateModalOpen(false)} className="text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreate} className="space-y-3 mt-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Product</label>
                <select
                  value={newLot.product_id}
                  onChange={(e) => setNewLot({ ...newLot, product_id: e.target.value })}
                  className="w-full border border-slate-200 rounded-lg p-2"
                >
                  {products.map((p) => (
                    <option key={p.product_id} value={p.product_id}>
                      {p.product_name} ({p.product_id})
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Supplier Name</label>
                <input
                  type="text"
                  value={newLot.supplier_name}
                  onChange={(e) => setNewLot({ ...newLot, supplier_name: e.target.value })}
                  className="w-full border border-slate-200 rounded-lg p-2"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Mfg Date</label>
                  <input
                    type="date"
                    value={newLot.manufacturing_date}
                    onChange={(e) => setNewLot({ ...newLot, manufacturing_date: e.target.value })}
                    className="w-full border border-slate-200 rounded-lg p-2"
                    required
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Expiry Date</label>
                  <input
                    type="date"
                    value={newLot.expiry_date}
                    onChange={(e) => setNewLot({ ...newLot, expiry_date: e.target.value })}
                    className="w-full border border-slate-200 rounded-lg p-2"
                    required
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Quantity</label>
                  <input
                    type="number"
                    value={newLot.quantity}
                    onChange={(e) => setNewLot({ ...newLot, quantity: e.target.value })}
                    className="w-full border border-slate-200 rounded-lg p-2"
                    required
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Unit</label>
                  <select
                    value={newLot.unit}
                    onChange={(e) => setNewLot({ ...newLot, unit: e.target.value })}
                    className="w-full border border-slate-200 rounded-lg p-2"
                  >
                    <option value="DOSES">DOSES</option>
                    <option value="VIALS">VIALS</option>
                    <option value="UNITS">UNITS</option>
                    <option value="CARTONS">CARTONS</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setCreateModalOpen(false)}
                  className="px-4 py-2 rounded-lg border border-slate-200 text-slate-600 font-semibold"
                >
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold">
                  Register Lot
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
