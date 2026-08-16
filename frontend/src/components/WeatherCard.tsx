import React from 'react';
import { Sun, Cloud, CloudRain, Droplets, SunMedium, Umbrella } from 'lucide-react';
import { PredictionItem } from '../types/weather';

interface WeatherCardProps {
  prediction: PredictionItem;
  selectedModel: string;
  isToday?: boolean;
}

export const WeatherCard: React.FC<WeatherCardProps> = ({
  prediction,
  selectedModel,
  isToday = false,
}) => {
  // Lấy nhiệt độ hiệu chỉnh theo mô hình được chọn
  const modelPred = prediction.models?.[selectedModel];
  const correctedTemp = modelPred?.corrected_temp_max ?? prediction.corrected_temp_max;
  const rawTemp = prediction.raw_forecast_temp_max;
  const biasDiff = correctedTemp - rawTemp;

  // Format ngày tháng
  const dateObj = new Date(prediction.date);
  const dayName = isToday
    ? 'Hôm nay'
    : dateObj.toLocaleDateString('vi-VN', { weekday: 'short' });
  const formattedDate = dateObj.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });

  // Chọn icon khí tượng
  const WeatherIcon = prediction.will_rain
    ? CloudRain
    : prediction.cloud_cover > 60
    ? Cloud
    : Sun;

  const iconColor = prediction.will_rain
    ? 'text-sky-400'
    : prediction.cloud_cover > 60
    ? 'text-slate-300'
    : 'text-amber-400';

  return (
    <div
      className={`glass-card glass-card-hover rounded-2xl p-4 border transition-all flex flex-col justify-between ${
        isToday ? 'border-sky-500/50 bg-sky-950/20 ring-1 ring-sky-500/40' : 'border-white/10'
      }`}
    >
      <div>
        {/* Date & Rain Badge */}
        <div className="flex items-center justify-between gap-1 mb-2">
          <div>
            <span className="text-xs font-bold text-white uppercase tracking-wider">{dayName}</span>
            <p className="text-[11px] text-slate-400">{formattedDate}</p>
          </div>

          {prediction.will_rain ? (
            <span className="flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-sky-500/20 text-sky-300 border border-sky-500/30">
              <Umbrella className="w-3 h-3" />
              Mưa ({prediction.rain_probability}%)
            </span>
          ) : (
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-400">
              Không mưa
            </span>
          )}
        </div>

        {/* Icon & Main Temp */}
        <div className="flex items-center justify-between my-3">
          <div className="flex items-baseline gap-1.5">
            <span className="text-2xl font-extrabold text-white">{correctedTemp.toFixed(1)}°</span>
            <span className="text-xs text-slate-400 font-medium">/ {rawTemp.toFixed(1)}°</span>
          </div>

          <div className={`p-2 rounded-xl bg-slate-900/60 border border-white/5 ${iconColor}`}>
            <WeatherIcon className="w-6 h-6" />
          </div>
        </div>

        {/* Bias Correction Tag */}
        <div className="text-[11px] font-medium flex items-center justify-between mb-3 text-slate-400">
          <span>Sai số hiệu chỉnh:</span>
          <span className={`font-semibold ${biasDiff > 0 ? 'text-amber-400' : biasDiff < 0 ? 'text-sky-400' : 'text-slate-400'}`}>
            {biasDiff > 0 ? `+${biasDiff.toFixed(1)}°C` : `${biasDiff.toFixed(1)}°C`}
          </span>
        </div>
      </div>

      {/* Footer Metrics: Humidity, UV, Cloud */}
      <div className="grid grid-cols-3 gap-1 pt-2.5 border-t border-white/5 text-[10px] text-slate-400 text-center">
        <div className="flex flex-col items-center">
          <Droplets className="w-3 h-3 text-sky-400 mb-0.5" />
          <span>{prediction.humidity}%</span>
        </div>
        <div className="flex flex-col items-center">
          <Cloud className="w-3 h-3 text-slate-400 mb-0.5" />
          <span>{prediction.cloud_cover}%</span>
        </div>
        <div className="flex flex-col items-center">
          <SunMedium className="w-3 h-3 text-amber-400 mb-0.5" />
          <span>UV {prediction.uv_index}</span>
        </div>
      </div>
    </div>
  );
};
