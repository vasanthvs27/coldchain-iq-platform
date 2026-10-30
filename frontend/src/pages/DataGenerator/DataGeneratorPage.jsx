import React, { useState, useEffect } from 'react';
import { Database, Play, RefreshCw, CheckCircle2, ShieldAlert, Cpu, Truck } from 'lucide-react';
import apiClient from '../../services/api';
import PageHeader from '../../components/common/PageHeader';
import StatusBadge from '../../components/common/StatusBadge';

export default function DataGeneratorPage() {
  const [mode, setMode] = useState('STARTER');
  const [seed, setSeed] = useState(20261022);
  const [shipments, setShipments] = useState(50);
  const [loggers, setLoggers] = useState(25);
  const [interval, setIntervalMinutes] = useState(10);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [recentRuns, setRecentRuns] = useState([]);

  const loadRecentRuns = async () => {
    try {
      const res = await apiClient.get('/generator/runs');
      if (res.success) setRecentRuns(res.data);
    } catch (err) {
      console.error('Failed to load generator runs:', err);
    }
  };

  useEffect(() => {
    loadRecentRuns();
  }, []);

  const handleRunGenerator = async () => {
    setRunning(true);
    setResult(null);
    try {
      const res = await apiClient.post('/generator/run', {
        mode,
        seed: parseInt(seed),
        shipment_count: parseInt(shipments),
        logger_count: parseInt(loggers),
        reading_interval_minutes: parseInt(interval),
      });
      if (res.success) {
        setResult(res.data);
        loadRecentRuns();
      }
    } catch (err) {
      alert(`Generation failed: ${err.message}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Synthetic Cold Chain Data Generation Engine"
        subtitle="Deterministic synthetic generation with fixed random seed (20261022), 10-minute intervals, and controlled anomaly injection"
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-1 bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          <h2 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-2 flex items-center gap-2">
            <Database className="w-4 h-4 text-blue-600" />
            Generation Parameters
          </h2>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Execution Mode</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => {
                  setMode('STARTER');
                  setShipments(50);
                  setLoggers(25);
                }}
                className={`py-2 text-xs font-semibold rounded-lg border transition ${
                  mode === 'STARTER'
                    ? 'bg-blue-50 border-blue-600 text-blue-700'
                    : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                Starter Mode
              </button>
              <button
                type="button"
                onClick={() => {
                  setMode('FULL');
                  setShipments(5000);
                  setLoggers(1000);
                }}
                className={`py-2 text-xs font-semibold rounded-lg border transition ${
                  mode === 'FULL'
                    ? 'bg-blue-50 border-blue-600 text-blue-700'
                    : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                Full Mode (5,000)
              </button>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Random Seed (Fixed)</label>
            <input
              type="number"
              value={seed}
              onChange={(e) => setSeed(e.target.value)}
              className="w-full text-xs font-mono font-semibold border border-slate-200 rounded-lg p-2 bg-slate-50"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Shipment Target</label>
              <input
                type="number"
                value={shipments}
                onChange={(e) => setShipments(e.target.value)}
                className="w-full text-xs border border-slate-200 rounded-lg p-2"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Logger Count</label>
              <input
                type="number"
                value={loggers}
                onChange={(e) => setLoggers(e.target.value)}
                className="w-full text-xs border border-slate-200 rounded-lg p-2"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Reading Interval (Minutes)</label>
            <input
              type="number"
              value={interval}
              onChange={(e) => setIntervalMinutes(e.target.value)}
              className="w-full text-xs border border-slate-200 rounded-lg p-2"
            />
          </div>

          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-[11px] text-slate-600 space-y-1">
            <span className="font-semibold text-slate-800 block">Five Negative Scenarios Injected:</span>
            <div>1. UNASSIGNED_LOGGER</div>
            <div>2. POLICY_MISMATCH</div>
            <div>3. MISSING_DATA</div>
            <div>4. CUSTODY_GAP</div>
            <div>5. CROSS_SHIPMENT_DURATION</div>
          </div>

          <button
            onClick={handleRunGenerator}
            disabled={running}
            className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg text-xs flex items-center justify-center gap-2 shadow-sm transition disabled:opacity-50"
          >
            {running ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Generating Synthetic Records...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Execute Generation Pipeline
              </>
            )}
          </button>
        </div>

        {/* Results & History Panel */}
        <div className="lg:col-span-2 space-y-6">
          {result && (
            <div className="bg-emerald-50/50 border border-emerald-200 rounded-xl p-5 space-y-3">
              <div className="flex items-center gap-2 text-emerald-800 font-bold text-sm">
                <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                Synthetic Dataset Generation Succeeded
              </div>
              <div className="text-xs text-slate-600 font-mono">Run ID: {result.run_id}</div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2">
                {Object.entries(result.summary || {}).map(([k, v]) => (
                  <div key={k} className="bg-white p-2.5 rounded border border-emerald-100">
                    <span className="text-[10px] text-slate-400 capitalize">{k.replace('_', ' ')}</span>
                    <div className="text-sm font-bold text-slate-800">{Number(v).toLocaleString()}</div>
                  </div>
                ))}
              </div>
              <div className="text-[11px] text-slate-500 pt-1 font-mono">
                Isolated Ground Truth: {result.ground_truth_files?.csv}
              </div>
            </div>
          )}

          {/* Historical Runs Table */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-4 bg-slate-50 border-b border-slate-200 font-semibold text-xs text-slate-700 flex items-center justify-between">
              <span>Execution Runs History</span>
              <button onClick={loadRecentRuns} className="text-blue-600 hover:text-blue-800 font-medium text-[11px]">
                Refresh
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
                  <tr>
                    <th className="py-2.5 px-3">Run ID</th>
                    <th className="py-2.5 px-3">Mode</th>
                    <th className="py-2.5 px-3">Seed</th>
                    <th className="py-2.5 px-3">Shipments</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3">Started</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {recentRuns.map((r) => (
                    <tr key={r.run_id} className="hover:bg-slate-50">
                      <td className="py-2.5 px-3 font-mono font-semibold text-blue-600">{r.run_id}</td>
                      <td className="py-2.5 px-3 font-semibold text-slate-800">{r.mode}</td>
                      <td className="py-2.5 px-3 font-mono text-slate-600">{r.seed}</td>
                      <td className="py-2.5 px-3 text-slate-700">{r.shipment_count}</td>
                      <td className="py-2.5 px-3">
                        <StatusBadge status={r.status} />
                      </td>
                      <td className="py-2.5 px-3 text-slate-500">{new Date(r.started_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
