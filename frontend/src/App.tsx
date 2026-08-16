import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { PipelineControlPage } from './pages/PipelineControlPage';
import { SystemLogsPage } from './pages/SystemLogsPage';
import { weatherApi } from './services/api';
import {
  HealthResponse,
  MetricsResponse,
  PredictionsResponse,
  PipelineStatusResponse,
  PipelineHistoryResponse,
} from './types/weather';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'pipeline' | 'logs'>('dashboard');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [predictions, setPredictions] = useState<PredictionsResponse | null>(null);
  const [pipelineStatus, setPipelineStatus] = useState<PipelineStatusResponse | null>(null);
  const [pipelineHistory, setPipelineHistory] = useState<PipelineHistoryResponse | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>('xgboost');
  const [loading, setLoading] = useState<boolean>(false);

  const loadAllData = async () => {
    try {
      setLoading(true);
      const [h, m, p, s, hist] = await Promise.allSettled([
        weatherApi.getHealth(),
        weatherApi.getMetrics(),
        weatherApi.getPredictions(),
        weatherApi.getPipelineStatus(),
        weatherApi.getPipelineHistory(15),
      ]);

      if (h.status === 'fulfilled') setHealth(h.value);
      if (m.status === 'fulfilled') {
        setMetrics(m.value);
        if (m.value?.best_model) setSelectedModel(m.value.best_model);
      }
      if (p.status === 'fulfilled') setPredictions(p.value);
      if (s.status === 'fulfilled') setPipelineStatus(s.value);
      if (hist.status === 'fulfilled') setPipelineHistory(hist.value);
    } catch (err) {
      console.error('Lỗi khi nạp dữ liệu từ backend API:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  return (
    <div className="min-h-screen pb-16">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        health={health}
        loading={loading}
        onRefresh={loadAllData}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {activeTab === 'dashboard' && (
          <DashboardPage
            predictionsData={predictions}
            metricsData={metrics}
            selectedModel={selectedModel}
            setSelectedModel={setSelectedModel}
          />
        )}

        {activeTab === 'pipeline' && (
          <PipelineControlPage
            status={pipelineStatus}
            history={pipelineHistory}
            onRefresh={loadAllData}
          />
        )}

        {activeTab === 'logs' && <SystemLogsPage />}
      </main>

      {/* Footer */}
      <footer className="mt-16 text-center text-xs text-slate-500 py-6 border-t border-white/5">
        <p>Weather MLOps Bias Correction System &copy; 2026. Xây dựng bằng React + Vite + TailwindCSS.</p>
        <p className="mt-1 text-[11px] text-slate-600">Trọng tâm khí tượng: Thành phố Hồ Chí Minh (TP.HCM)</p>
      </footer>
    </div>
  );
};
