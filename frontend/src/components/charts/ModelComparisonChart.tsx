import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from 'recharts';
import { MetricValues } from '../../types/weather';

interface ModelComparisonChartProps {
  modelsComparison: Record<string, MetricValues>;
}

export const ModelComparisonChart: React.FC<ModelComparisonChartProps> = ({
  modelsComparison,
}) => {
  const modelLabels: Record<string, string> = {
    xgboost: 'XGBoost',
    lightgbm: 'LightGBM',
    random_forest: 'Random Forest',
    linear_regression: 'Ridge',
  };

  const data = Object.entries(modelsComparison).map(([key, val]) => ({
    name: modelLabels[key] || key.toUpperCase(),
    key,
    'Mức Giảm MAE (%)': Number((val.mae_reduction_percentage ?? 0).toFixed(1)),
    'MAE (°C)': Number(val.mae.toFixed(2)),
  }));

  return (
    <div className="glass-card rounded-2xl p-5 border border-white/10 h-full flex flex-col justify-between">
      <div className="mb-4">
        <h3 className="text-base font-bold text-white">
          🏆 So Sánh Hiệu Quả 4 Mô Hình ML
        </h3>
        <p className="text-xs text-slate-400">
          Tỷ lệ giảm sai số MAE so với dự báo thô (Càng cao càng tốt)
        </p>
      </div>

      <div className="h-[280px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} tickLine={false} />
            <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} unit="%" />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                borderRadius: '12px',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                fontSize: '12px',
              }}
            />

            <Bar dataKey="Mức Giảm MAE (%)" radius={[6, 6, 0, 0]}>
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry['Mức Giảm MAE (%)'] >= 0 ? '#10b981' : '#f43f5e'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
