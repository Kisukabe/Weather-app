import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { PredictionItem } from '../../types/weather';

interface TemperatureChartProps {
  predictions: PredictionItem[];
  selectedModel: string;
}

export const TemperatureChart: React.FC<TemperatureChartProps> = ({
  predictions,
  selectedModel,
}) => {
  // Format dữ liệu cho Recharts
  const data = predictions.map((item) => {
    const modelPred = item.models?.[selectedModel];
    const corrected = modelPred?.corrected_temp_max ?? item.corrected_temp_max;
    const raw = item.raw_forecast_temp_max;

    const dateFormatted = new Date(item.date).toLocaleDateString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
    });

    return {
      date: dateFormatted,
      fullDate: item.date,
      'Dự Báo Thô (Open-Meteo)': Number(raw.toFixed(1)),
      [`Hiệu Chỉnh (${selectedModel.toUpperCase()})`]: Number(corrected.toFixed(1)),
      saiSo: Number((corrected - raw).toFixed(1)),
    };
  });

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass-card rounded-xl p-3 border border-white/10 shadow-2xl text-xs space-y-1">
          <p className="font-bold text-white mb-1.5">{label}</p>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
            <span className="text-slate-300">Dự báo thô:</span>
            <strong className="text-white ml-auto">{payload[0]?.value}°C</strong>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
            <span className="text-slate-300">Hiệu chỉnh ML:</span>
            <strong className="text-emerald-400 ml-auto">{payload[1]?.value}°C</strong>
          </div>
          {payload[1] && payload[0] && (
            <p className="text-[10px] text-slate-400 pt-1 border-t border-white/5">
              Sai số hiệu chỉnh: <strong>{(payload[1].value - payload[0].value).toFixed(1)}°C</strong>
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-card rounded-2xl p-5 border border-white/10">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-white">
            📈 Biểu Đồ So Sánh Nhiệt Độ Dự Báo Thô vs Sau Hiệu Chỉnh
          </h3>
          <p className="text-xs text-slate-400">
            Nhiệt độ cao nhất trong ngày (°C) theo mô hình <strong>{selectedModel.toUpperCase()}</strong>
          </p>
        </div>
      </div>

      <div className="h-[360px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorRaw" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorCorrected" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} tickLine={false} />
            <YAxis stroke="#94a3b8" fontSize={11} domain={['auto', 'auto']} tickLine={false} />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
              iconType="circle"
            />

            <Area
              type="monotone"
              dataKey="Dự Báo Thô (Open-Meteo)"
              stroke="#f43f5e"
              strokeWidth={2}
              strokeDasharray="4 4"
              fillOpacity={1}
              fill="url(#colorRaw)"
            />
            <Area
              type="monotone"
              dataKey={`Hiệu Chỉnh (${selectedModel.toUpperCase()})`}
              stroke="#10b981"
              strokeWidth={3}
              fillOpacity={1}
              fill="url(#colorCorrected)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
