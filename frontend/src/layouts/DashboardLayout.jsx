import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Package,
  Boxes,
  Truck,
  Box,
  Cpu,
  ThermometerSnowflake,
  MapPin,
  GitCommit,
  ShieldAlert,
  FileCheck,
  AlertTriangle,
  Radio,
  Sliders,
  BarChart3,
  Database,
  CheckCircle2,
  BrainCircuit,
  RefreshCw,
  History,
  Settings,
  Menu,
  X,
  ChevronDown,
  ShieldCheck,
  Building2,
  Clock
} from 'lucide-react';
import { useAuth, ROLES } from '../contexts/AuthContext';

export default function DashboardLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, activeRole, switchRole } = useAuth();
  const location = useLocation();

  const navSections = [
    {
      title: 'CORE PLATFORM',
      items: [
        { name: 'Executive Dashboard', path: '/', icon: LayoutDashboard },
        { name: 'Shipments', path: '/shipments', icon: Truck },
        { name: 'Temperature Monitoring', path: '/temperature', icon: ThermometerSnowflake },
        { name: 'Excursions', path: '/excursions', icon: ShieldAlert },
        { name: 'Compliance Reports', path: '/compliance', icon: FileCheck },
      ]
    },
    {
      title: 'TELEMETRY & LOGISTICS',
      items: [
        { name: 'Route Tracking', path: '/routes', icon: MapPin },
        { name: 'Custody Chain', path: '/custody', icon: GitCommit },
        { name: 'Data Loggers', path: '/loggers', icon: Cpu },
        { name: 'Data Gaps', path: '/data-gaps', icon: Radio },
        { name: 'Logger Calibration', path: '/calibration', icon: Clock },
      ]
    },
    {
      title: 'MASTER DATA',
      items: [
        { name: 'Products', path: '/products', icon: Package },
        { name: 'Lots & Batches', path: '/lots', icon: Boxes },
        { name: 'Thermal Packaging', path: '/packaging', icon: Box },
        { name: 'Threshold Policies', path: '/policies', icon: Sliders },
      ]
    },
    {
      title: 'INTELLIGENCE & ENGINE',
      items: [
        { name: 'Analytics & Risk', path: '/analytics', icon: BarChart3 },
        { name: 'Shipment Risk', path: '/risk', icon: AlertTriangle },
        { name: 'Synthetic Generator', path: '/generator', icon: Database },
        { name: 'Data Validation', path: '/validation', icon: CheckCircle2 },
        { name: 'Ground Truth Eval', path: '/ground-truth', icon: BrainCircuit },
        { name: 'Reproducibility', path: '/reproducibility', icon: RefreshCw },
        { name: 'Audit Trail', path: '/audit', icon: History },
        { name: 'Settings', path: '/settings', icon: Settings },
      ]
    }
  ];

  return (
    <div className="min-h-screen flex bg-surface">
      {/* Mobile Sidebar Backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-navy-900 text-slate-300 flex flex-col transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-0 max-lg:-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center justify-between px-5 border-b border-navy-800 bg-navy-900/80">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-blue-600 to-teal-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
              <ThermometerSnowflake className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <span className="font-bold text-lg text-white tracking-tight">ColdChain<span className="text-teal-400">IQ</span></span>
              <span className="block text-[10px] text-slate-400 -mt-1 font-medium tracking-wider">PLATFORM</span>
            </div>
          </Link>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-slate-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation Links */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
          {navSections.map((section, idx) => (
            <div key={idx}>
              <div className="px-3 mb-2 text-[10px] font-bold text-slate-400 tracking-wider">
                {section.title}
              </div>
              <div className="space-y-1">
                {section.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path;
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      onClick={() => setSidebarOpen(false)}
                      className={`flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all duration-150 ${
                        isActive
                          ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 font-semibold'
                          : 'text-slate-400 hover:text-white hover:bg-navy-800/60'
                      }`}
                    >
                      <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                      <span>{item.name}</span>
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Database Status Footer */}
        <div className="p-3 border-t border-navy-800 bg-navy-900/60">
          <div className="bg-navy-800/80 rounded-lg p-2.5 flex items-center gap-2 border border-navy-700/50">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <div className="flex-1">
              <div className="text-[11px] font-semibold text-slate-200">Supabase DB Engine</div>
              <div className="text-[10px] text-emerald-400 font-mono">Connected • RLS Active</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 lg:px-8 z-30 sticky top-0 shadow-sm">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="hidden sm:flex items-center gap-2 text-xs font-medium text-slate-500">
              <span>ColdChain IQ</span>
              <span>/</span>
              <span className="text-slate-900 font-semibold capitalize">
                {location.pathname === '/' ? 'Dashboard' : location.pathname.substring(1).replace('-', ' ')}
              </span>
            </div>
          </div>

          {/* Right Header: Role Switcher & User Profile */}
          <div className="flex items-center gap-3">
            {/* Actor Role Selector */}
            <div className="flex items-center gap-2 bg-slate-100/90 hover:bg-slate-100 border border-slate-200 rounded-lg px-2.5 py-1.5 transition">
              <Building2 className="w-3.5 h-3.5 text-blue-600" />
              <span className="text-xs font-medium text-slate-600 hidden md:inline">Actor Role:</span>
              <select
                value={activeRole}
                onChange={(e) => switchRole(e.target.value)}
                className="bg-transparent text-xs font-semibold text-slate-800 focus:outline-none cursor-pointer"
              >
                {ROLES.map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
            </div>

            {/* User Profile Badge */}
            <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
              <div className="w-8 h-8 rounded-full bg-blue-100 border border-blue-200 text-blue-700 font-bold text-xs flex items-center justify-center">
                {user?.full_name ? user.full_name[0] : 'S'}
              </div>
              <div className="hidden md:block text-left">
                <div className="text-xs font-semibold text-slate-800 leading-tight">{user?.full_name || 'Sarah Jenkins'}</div>
                <div className="text-[10px] text-slate-500">{activeRole}</div>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content Viewport */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto space-y-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
