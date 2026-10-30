import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import DashboardLayout from './layouts/DashboardLayout';

// Core Pages
import DashboardPage from './pages/Dashboard/DashboardPage';
import ShipmentsPage from './pages/Shipments/ShipmentsPage';
import ProductsPage from './pages/Products/ProductsPage';
import LotsPage from './pages/Lots/LotsPage';
import PackagingPage from './pages/Packaging/PackagingPage';
import LoggersPage from './pages/Loggers/LoggersPage';
import TemperatureMonitoringPage from './pages/TemperatureMonitoring/TemperatureMonitoringPage';

// Telemetry & Logistics
import RouteTrackingPage from './pages/RouteTracking/RouteTrackingPage';
import CustodyEventsPage from './pages/CustodyEvents/CustodyEventsPage';
import ThresholdPoliciesPage from './pages/ThresholdPolicies/ThresholdPoliciesPage';
import DataGapsPage from './pages/DataGaps/DataGapsPage';
import CalibrationPage from './pages/Calibration/CalibrationPage';

// Compliance & Risk
import ExcursionsPage from './pages/Excursions/ExcursionsPage';
import ComplianceReportsPage from './pages/ComplianceReports/ComplianceReportsPage';
import RiskAssessmentPage from './pages/RiskAssessment/RiskAssessmentPage';
import AnalyticsPage from './pages/Analytics/AnalyticsPage';

// Intelligence & Engine
import DataGeneratorPage from './pages/DataGenerator/DataGeneratorPage';
import DataValidationPage from './pages/DataValidation/DataValidationPage';
import GroundTruthPage from './pages/GroundTruth/GroundTruthPage';
import ReproducibilityPage from './pages/Reproducibility/ReproducibilityPage';
import AuditTrailPage from './pages/AuditTrail/AuditTrailPage';
import SettingsPage from './pages/Settings/SettingsPage';

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <DashboardLayout>
          <Routes>
            {/* Core Platform */}
            <Route path="/" element={<DashboardPage />} />
            <Route path="/shipments" element={<ShipmentsPage />} />
            <Route path="/temperature" element={<TemperatureMonitoringPage />} />
            <Route path="/excursions" element={<ExcursionsPage />} />
            <Route path="/compliance" element={<ComplianceReportsPage />} />

            {/* Telemetry & Logistics */}
            <Route path="/routes" element={<RouteTrackingPage />} />
            <Route path="/custody" element={<CustodyEventsPage />} />
            <Route path="/loggers" element={<LoggersPage />} />
            <Route path="/data-gaps" element={<DataGapsPage />} />
            <Route path="/calibration" element={<CalibrationPage />} />

            {/* Master Data */}
            <Route path="/products" element={<ProductsPage />} />
            <Route path="/lots" element={<LotsPage />} />
            <Route path="/packaging" element={<PackagingPage />} />
            <Route path="/policies" element={<ThresholdPoliciesPage />} />

            {/* Intelligence & Analytics */}
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/risk" element={<RiskAssessmentPage />} />
            <Route path="/generator" element={<DataGeneratorPage />} />
            <Route path="/validation" element={<DataValidationPage />} />
            <Route path="/ground-truth" element={<GroundTruthPage />} />
            <Route path="/reproducibility" element={<ReproducibilityPage />} />
            <Route path="/audit" element={<AuditTrailPage />} />
            <Route path="/settings" element={<SettingsPage />} />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </DashboardLayout>
      </AuthProvider>
    </Router>
  );
}
