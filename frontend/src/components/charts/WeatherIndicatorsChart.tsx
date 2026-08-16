import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { PredictionItem } from '../../types/weather';

interface WeatherIndicatorsChartProps {
  predictions: PredictionItem[];
}

export const WeatherIndicatorsChart: React.FC<WeatherIndicatorsChartProps> = ({
  predictions,
}) => {
  const data = predictions.map((item) => {
    const dateFormatted = new Date(item.date).toLocaleDateString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
    });

    return {
      date: dateFormatted,
      'Độ Ẩm (%)': item.humidity,
      'Độ Phủ Mây (%)': item.cloud_cover,
      'Xác Suất Mưa (%)': item.rain_probability,
    };
  });

  return (
    <div className="glass-card rounded-2xl p-5 border border-white/10 h-full flex flex-col justify-between">
      <div className="mb-4">
        <h3 className="text-base font-bold text-white">
          💧 Chỉ Số Khí Tượng Mở Rộng
        </h3>
        <p className="text-xs text-slate-400">
          Độ ẩm tương đối, độ che phủ của mây và xác suất xuất hiện mưa
        </p>
      </div>

      <div className="h-[280px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} tickLine={false} />
            <YAxis stroke="#94a3b8" fontSize={11} domain={[0, 100]} tickLine={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                borderRadius: '12px',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                fontSize: '12px',
              }}
            />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />

            <Bar dataKey="Xác Suất Mưa (%)" fill="#0284c7" radius={[4, 4, 0, 0]} opacity={0.6} />
            <Line
              type="monotone"
              dataKey="Độ Ẩm (%)"
              stroke="#38bdf8"
              strokeWidth={2.5}
              dot={{ r: 3 }}
            />
            <Line
              type="monotone"
              dataKey="Độ Phủ Mây (%)"
              stroke="#a855f7"
              strokeWidth={2}
              strokeDasharray="4 4"
              dot={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
