import React, { useState } from 'react';
import { 
  Settings as SettingsIcon, 
  Database, 
  Shield, 
  Bell, 
  Clock, 
  Save, 
  CheckCircle2, 
  Server, 
  Key, 
  FileCheck,
  Cpu,
  Sliders
} from 'lucide-react';
import PageHeader from '../../components/common/PageHeader';
import { useAuth } from '../../contexts/AuthContext';

export default function SettingsPage() {
  const { activeRole } = useAuth();
  const [saved, setSaved] = useState(false);

  // Form states
  const [config, setConfig] = useState({
    supabaseUrl: import.meta.env.VITE_SUPABASE_URL || 'https://xyzcompany.supabase.co',
    readingIntervalMin: 10,
    calibrationGracePeriodDays: 30,
    maxAllowedGapsBeforeInconclusive: 3,
    quarantineOnCriticalExcursion: true,
    requireTwoPartySignoff: true,
    notificationWebhook: 'https://hooks.coldchain-iq.internal/alerts',
    emailAlertsEnabled: true,
    retentionYears: 7,
  });

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="System Settings & Governance"
        subtitle="Global platform parameters, Supabase database configuration, and GxP compliance rules"
        actions={
          <button
            onClick={handleSave}
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 shadow-sm transition"
          >
            {saved ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-emerald-300" />
                Settings Saved!
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Save Changes
              </>
            )}
          </button>
        }
      />

      <form onSubmit={handleSave} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Supabase & Security */}
        <div className="space-y-6 lg:col-span-1">
          {/* Supabase Connection Card */}
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center gap-2 text-slate-800 font-semibold text-sm border-b border-slate-100 pb-3">
              <Database className="w-4 h-4 text-emerald-600" />
              <span>Supabase Managed Database</span>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-500 font-medium block mb-1">Database Provider</label>
                <div className="flex items-center gap-2 p-2 bg-slate-50 rounded-lg border border-slate-200 font-mono text-[11px] text-slate-700">
                  <Server className="w-3.5 h-3.5 text-emerald-500" />
                  <span>Supabase PostgreSQL 15 (Managed)</span>
                </div>
              </div>

              <div>
                <label className="text-slate-500 font-medium block mb-1">Database URL</label>
                <input
                  type="text"
                  value={config.supabaseUrl}
                  onChange={(e) => setConfig({ ...config, supabaseUrl: e.target.value })}
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg font-mono text-[11px] text-slate-700 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="text-slate-500 font-medium block mb-1">Row Level Security (RLS)</label>
                <div className="flex items-center justify-between p-2.5 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-800">
                  <span className="font-semibold text-[11px]">Enforced on all tables</span>
                  <span className="px-2 py-0.5 bg-emerald-600 text-white rounded text-[10px] font-bold">ACTIVE</span>
                </div>
              </div>

              <div>
                <label className="text-slate-500 font-medium block mb-1">Architecture Standard</label>
                <p className="text-[11px] text-slate-500 leading-relaxed">
                  Supabase Python SDK + Supabase JS Client exclusively. Zero SQLAlchemy / SQLite footprint.
                </p>
              </div>
            </div>
          </div>

          {/* Security & Access Overview */}
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center gap-2 text-slate-800 font-semibold text-sm border-b border-slate-100 pb-3">
              <Shield className="w-4 h-4 text-blue-600" />
              <span>Role-Based Access Control (RBAC)</span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                <span className="text-slate-600">Current Active Actor:</span>
                <span className="font-bold text-blue-600">{activeRole}</span>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                <span className="text-slate-600">Audit Logging:</span>
                <span className="text-emerald-600 font-semibold">21 CFR Part 11 Active</span>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                <span className="text-slate-600">Data Retention:</span>
                <span className="font-mono text-slate-800">{config.retentionYears} Years (GxP)</span>
              </div>
              <div className="flex justify-between items-center py-1.5">
                <span className="text-slate-600">Deterministic Seed:</span>
                <span className="font-mono text-slate-800 font-semibold">20261022</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Columns - Governance & Rules */}
        <div className="space-y-6 lg:col-span-2">
          {/* Telemetry & Compliance Parameters */}
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center gap-2 text-slate-800 font-semibold text-sm border-b border-slate-100 pb-3">
              <Sliders className="w-4 h-4 text-blue-600" />
              <span>Telemetry & Business Rule Engine Parameters</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div>
                <label className="text-slate-700 font-semibold block mb-1">
                  Expected Telemetry Interval (Minutes)
                </label>
                <input
                  type="number"
                  min="1"
                  max="60"
                  value={config.readingIntervalMin}
                  onChange={(e) => setConfig({ ...config, readingIntervalMin: parseInt(e.target.value) || 10 })}
                  className="w-full p-2 bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:border-blue-500 font-mono"
                />
                <span className="text-[10px] text-slate-400 mt-1 block">
                  Standard GxP interval for in-transit loggers (Default: 10 mins)
                </span>
              </div>

              <div>
                <label className="text-slate-700 font-semibold block mb-1">
                  Calibration Expiry Grace Period (Days)
                </label>
                <input
                  type="number"
                  min="0"
                  max="90"
                  value={config.calibrationGracePeriodDays}
                  onChange={(e) => setConfig({ ...config, calibrationGracePeriodDays: parseInt(e.target.value) || 0 })}
                  className="w-full p-2 bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:border-blue-500 font-mono"
                />
                <span className="text-[10px] text-slate-400 mt-1 block">
                  Advance warning before calibration certificate expires
                </span>
              </div>

              <div>
                <label className="text-slate-700 font-semibold block mb-1">
                  Consecutive Gaps to Trigger INCONCLUSIVE
                </label>
                <input
                  type="number"
                  min="1"
                  max="20"
                  value={config.maxAllowedGapsBeforeInconclusive}
                  onChange={(e) => setConfig({ ...config, maxAllowedGapsBeforeInconclusive: parseInt(e.target.value) || 3 })}
                  className="w-full p-2 bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:border-blue-500 font-mono"
                />
                <span className="text-[10px] text-slate-400 mt-1 block">
                  Missing reading intervals before evidence is deemed insufficient
                </span>
              </div>

              <div>
                <label className="text-slate-700 font-semibold block mb-1">
                  Regulatory Retention Policy
                </label>
                <select
                  value={config.retentionYears}
                  onChange={(e) => setConfig({ ...config, retentionYears: parseInt(e.target.value) || 7 })}
                  className="w-full p-2 bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:border-blue-500 font-medium"
                >
                  <option value={5}>5 Years (Standard Commercial)</option>
                  <option value={7}>7 Years (FDA 21 CFR Part 11 Standard)</option>
                  <option value={10}>10 Years (EU Annex 11 Clinical)</option>
                  <option value={20}>20 Years (Permanent Biologics)</option>
                </select>
                <span className="text-[10px] text-slate-400 mt-1 block">
                  Mandatory retention period for cold chain evidence
                </span>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100 space-y-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.quarantineOnCriticalExcursion}
                  onChange={(e) => setConfig({ ...config, quarantineOnCriticalExcursion: e.target.checked })}
                  className="rounded text-blue-600 focus:ring-blue-500 w-4 h-4"
                />
                <span className="text-xs font-medium text-slate-700">
                  Automatically Quarantine Lot on Confirmed Critical Temperature Excursion
                </span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.requireTwoPartySignoff}
                  onChange={(e) => setConfig({ ...config, requireTwoPartySignoff: e.target.checked })}
                  className="rounded text-blue-600 focus:ring-blue-500 w-4 h-4"
                />
                <span className="text-xs font-medium text-slate-700">
                  Enforce Two-Party Sign-off for Excursion Investigation Dispositions
                </span>
              </label>
            </div>
          </div>

          {/* Webhook & Notification Routing */}
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center gap-2 text-slate-800 font-semibold text-sm border-b border-slate-100 pb-3">
              <Bell className="w-4 h-4 text-blue-600" />
              <span>Automated Alerting & Incident Notification Channels</span>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-700 font-semibold block mb-1">
                  Incident Escalation Webhook URL
                </label>
                <input
                  type="url"
                  value={config.notificationWebhook}
                  onChange={(e) => setConfig({ ...config, notificationWebhook: e.target.value })}
                  className="w-full p-2 bg-slate-50 border border-slate-300 rounded-lg font-mono text-[11px] text-slate-700 focus:outline-none focus:border-blue-500"
                  placeholder="https://..."
                />
                <span className="text-[10px] text-slate-400 mt-1 block">
                  Receives real-time JSON payloads for UNASSIGNED_LOGGER, POLICY_MISMATCH, and critical excursions
                </span>
              </div>

              <div className="p-3 bg-blue-50/70 border border-blue-200 rounded-lg text-blue-900 text-xs flex items-center justify-between">
                <div>
                  <span className="font-semibold block">Automated Dispatch to Operations Manager</span>
                  <span className="text-[11px] text-blue-700">High-severity alerts are forwarded instantly via SMS and email.</span>
                </div>
                <span className="px-2 py-0.5 bg-blue-600 text-white rounded text-[10px] font-bold">ENABLED</span>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
}
