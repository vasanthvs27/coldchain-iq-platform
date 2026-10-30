import React, { useState, useEffect } from 'react';
import { Package, Plus, Search, Thermometer, ShieldCheck, X } from 'lucide-react';
import apiClient from '../../services/api';
import PageHeader from '../../components/common/PageHeader';
import StatusBadge from '../../components/common/StatusBadge';

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newProduct, setNewProduct] = useState({
    product_id: '',
    product_name: '',
    product_category: 'VACCINE_ULTRA_COLD',
    minimum_temperature: -80,
    maximum_temperature: -60,
    allowed_excursion_duration: 30,
    shelf_life_days: 180,
    description: '',
  });

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/products');
      if (res.success) setProducts(res.data);
    } catch (err) {
      console.error('Failed to load products:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...newProduct,
        product_id: newProduct.product_id || `PROD-${Math.floor(100 + Math.random() * 900)}`,
        minimum_temperature: parseFloat(newProduct.minimum_temperature),
        maximum_temperature: parseFloat(newProduct.maximum_temperature),
        allowed_excursion_duration: parseInt(newProduct.allowed_excursion_duration),
        shelf_life_days: parseInt(newProduct.shelf_life_days),
      };
      const res = await apiClient.post('/products', payload);
      if (res.success) {
        setCreateModalOpen(false);
        fetchProducts();
      }
    } catch (err) {
      alert(`Validation error: ${err.message}`);
    }
  };

  const filtered = products.filter((p) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return p.product_name?.toLowerCase().includes(q) || p.product_id?.toLowerCase().includes(q) || p.product_category?.toLowerCase().includes(q);
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Product Catalog & Temperature Profiles"
        subtitle="Master pharmaceutical formulas, validated temperature tolerances, and allowable excursion durations"
        actions={
          <button
            onClick={() => setCreateModalOpen(true)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition"
          >
            <Plus className="w-4 h-4" />
            Add New Product
          </button>
        }
      />

      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search products by name or ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          />
        </div>
        <span className="text-xs text-slate-500 font-medium">{filtered.length} products listed</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {loading ? (
          <div className="col-span-full py-12 text-center text-slate-400 text-xs">Loading products...</div>
        ) : (
          filtered.map((prod) => (
            <div key={prod.product_id} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition">
              <div className="flex items-start justify-between">
                <div>
                  <span className="font-mono text-[11px] font-bold text-blue-600">{prod.product_id}</span>
                  <h3 className="text-sm font-bold text-slate-900 mt-0.5">{prod.product_name}</h3>
                </div>
                <StatusBadge status={prod.status || 'ACTIVE'} />
              </div>

              <div className="mt-4 p-3 rounded-lg bg-blue-50/50 border border-blue-100 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Thermometer className="w-4 h-4 text-blue-600" />
                  <span className="text-xs font-semibold text-slate-700">Validated Range</span>
                </div>
                <span className="text-xs font-bold text-blue-700">
                  {prod.minimum_temperature}°C to {prod.maximum_temperature}°C
                </span>
              </div>

              <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-slate-500">
                <div>
                  Allowed Excursion: <span className="font-semibold text-slate-800">{prod.allowed_excursion_duration}m</span>
                </div>
                <div>
                  Shelf Life: <span className="font-semibold text-slate-800">{prod.shelf_life_days} days</span>
                </div>
              </div>

              <p className="text-[11px] text-slate-500 mt-3 line-clamp-2">{prod.description}</p>
            </div>
          ))
        )}
      </div>

      {createModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-900/60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <h3 className="text-base font-bold text-slate-900">Add Product Profile</h3>
              <button onClick={() => setCreateModalOpen(false)} className="text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreate} className="space-y-3 mt-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Product Name</label>
                <input
                  type="text"
                  value={newProduct.product_name}
                  onChange={(e) => setNewProduct({ ...newProduct, product_name: e.target.value })}
                  className="w-full border border-slate-200 rounded-lg p-2"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Min Temp (°C)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={newProduct.minimum_temperature}
                    onChange={(e) => setNewProduct({ ...newProduct, minimum_temperature: e.target.value })}
                    className="w-full border border-slate-200 rounded-lg p-2"
                    required
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Max Temp (°C)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={newProduct.maximum_temperature}
                    onChange={(e) => setNewProduct({ ...newProduct, maximum_temperature: e.target.value })}
                    className="w-full border border-slate-200 rounded-lg p-2"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Allowed Excursion (mins)</label>
                <input
                  type="number"
                  value={newProduct.allowed_excursion_duration}
                  onChange={(e) => setNewProduct({ ...newProduct, allowed_excursion_duration: e.target.value })}
                  className="w-full border border-slate-200 rounded-lg p-2"
                  required
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Description</label>
                <textarea
                  value={newProduct.description}
                  onChange={(e) => setNewProduct({ ...newProduct, description: e.target.value })}
                  className="w-full border border-slate-200 rounded-lg p-2"
                  rows={2}
                />
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
                  Save Product
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
