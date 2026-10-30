import React, { useState, useEffect } from 'react';
import { BrainCircuit, Play, ShieldCheck, CheckCircle2, AlertTriangle, Layers } from 'lucide-react';
import apiClient from '../../services/api';
import PageHeader from '../../components/common/PageHeader';

export default function GroundTruthPage() {
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(false);

  const runEvaluation = async () => {
    setLoading(true);
    try {
      const res = await apiClient.post('/evaluation/run');
      if (res.success) setEvaluation(res.data);
    } catch (err) {
      console.error('Evaluation error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runEvaluation();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Ground Truth & Detection Performance Evaluation"
        subtitle="Offline statistical evaluation comparing operational detections against strictly isolated ground-truth fixtures"
        actions={
          <button
            onClick={runEvaluation}
            disabled={loading}
            className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition"
          >
            <Play className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Evaluate Detection Metrics
          </button>
        }
      />

      {/* Metrics Banner */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200">
          <span className="text-xs text-slate-500 font-semibold uppercase">Precision</span>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {evaluation?.overall_metrics?.precision ?? 0}%
          </div>
          <span className="text-[11px] text-slate-400">TP / (TP + FP)</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200">
          <span className="text-xs text-slate-500 font-semibold uppercase">Recall</span>
          <div className="text-2xl font-bold text-teal-600 mt-1">
            {evaluation?.overall_metrics?.recall ?? 0}%
          </div>
          <span className="text-[11px] text-slate-400">TP / (TP + FN)</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200">
          <span className="text-xs text-slate-500 font-semibold uppercase">F1-Score</span>
          <div className="text-2xl font-bold text-emerald-600 mt-1">
            {evaluation?.overall_metrics?.f1_score ?? 0}%
          </div>
          <span className="text-[11px] text-slate-400">Harmonic Mean</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200">
          <span className="text-xs text-slate-500 font-semibold uppercase">Accuracy</span>
          <div className="text-2xl font-bold text-slate-900 mt-1">
            {evaluation?.overall_metrics?.accuracy ?? 0}%
          </div>
          <span className="text-[11px] text-slate-400">{evaluation?.overall_metrics?.total_samples ?? 0} samples</span>
        </div>
      </div>

      {/* Confusion Matrix Section */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h3 className="text-sm font-bold text-slate-900 mb-1">Confusion Matrix</h3>
        <p className="text-xs text-slate-500 mb-5">
          Operational Detection Output vs Ground-Truth Anomaly Labels
        </p>
        <div className="grid grid-cols-2 gap-4 max-w-xl mx-auto">
          <div className="bg-emerald-50 border border-emerald-200 p-4 rounded-xl text-center">
            <span className="text-xs font-semibold text-emerald-800 uppercase">True Positive (TP)</span>
            <div className="text-3xl font-extrabold text-emerald-700 mt-1">
              {evaluation?.confusion_matrix?.true_positives ?? 0}
            </div>
            <p className="text-[10px] text-emerald-600 mt-1">Correctly flagged anomalies</p>
          </div>

          <div className="bg-rose-50 border border-rose-200 p-4 rounded-xl text-center">
            <span className="text-xs font-semibold text-rose-800 uppercase">False Positive (FP)</span>
            <div className="text-3xl font-extrabold text-rose-700 mt-1">
              {evaluation?.confusion_matrix?.false_positives ?? 0}
            </div>
            <p className="text-[10px] text-rose-600 mt-1">Normal records flagged incorrectly</p>
          </div>

          <div className="bg-slate-50 border border-slate-200 p-4 rounded-xl text-center">
            <span className="text-xs font-semibold text-slate-700 uppercase">False Negative (FN)</span>
            <div className="text-3xl font-extrabold text-slate-800 mt-1">
              {evaluation?.confusion_matrix?.false_negatives ?? 0}
            </div>
            <p className="text-[10px] text-slate-500 mt-1">Missed anomalies</p>
          </div>

          <div className="bg-blue-50 border border-blue-200 p-4 rounded-xl text-center">
            <span className="text-xs font-semibold text-blue-800 uppercase">True Negative (TN)</span>
            <div className="text-3xl font-extrabold text-blue-700 mt-1">
              {evaluation?.confusion_matrix?.true_negatives ?? 0}
            </div>
            <p className="text-[10px] text-blue-600 mt-1">Correctly verified compliant records</p>
          </div>
        </div>
      </div>

      {/* Per-Scenario Anomaly Breakdown Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 font-semibold text-xs text-slate-700">
          Detection Performance Across Five Mandatory Negative Scenarios
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
              <tr>
                <th className="py-3 px-4 font-semibold">Negative Scenario</th>
                <th className="py-3 px-4 font-semibold">True Positives</th>
                <th className="py-3 px-4 font-semibold">False Positives</th>
                <th className="py-3 px-4 font-semibold">False Negatives</th>
                <th className="py-3 px-4 font-semibold">Precision</th>
                <th className="py-3 px-4 font-semibold">Recall</th>
                <th className="py-3 px-4 font-semibold">F1-Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {evaluation?.anomaly_breakdown?.map((sc, idx) => (
                <tr key={idx} className="hover:bg-slate-50">
                  <td className="py-3 px-4 font-mono font-bold text-slate-900">{sc.scenario}</td>
                  <td className="py-3 px-4 text-emerald-700 font-semibold">{sc.true_positives}</td>
                  <td className="py-3 px-4 text-rose-600 font-semibold">{sc.false_positives}</td>
                  <td className="py-3 px-4 text-slate-500 font-semibold">{sc.false_negatives}</td>
                  <td className="py-3 px-4 font-bold text-blue-600">{sc.precision}%</td>
                  <td className="py-3 px-4 font-bold text-teal-600">{sc.recall}%</td>
                  <td className="py-3 px-4 font-bold text-emerald-600">{sc.f1_score}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
