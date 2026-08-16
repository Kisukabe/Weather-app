import React from 'react';
import { Sparkles, Thermometer, Award, TrendingDown, Table } from 'lucide-react';
import { PredictionsResponse, MetricsResponse } from '../types/weather';
import { MetricCard } from '../components/MetricCard';
import { ModelSelector } from '../components/ModelSelector';
import { WeatherCard } from '../components/WeatherCard';
import { TemperatureChart } from '../components/charts/TemperatureChart';
import { WeatherIndicatorsChart } from '../components/charts/WeatherIndicatorsChart';
import { ModelComparisonChart } from '../components/charts/ModelComparisonChart';

interface DashboardPageProps {
  predictionsData: PredictionsResponse | null;
  metricsData: MetricsResponse | null;
  selectedModel: string;
  setSelectedModel: (model: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  predictionsData,
  metricsData,
  selectedModel,
  setSelectedModel,
}) => {
  const rawMae = metricsData?.raw_forecast_metrics.mae ?? 0.0;
  const modelsComp = metricsData?.models_comparison ?? {};
  const currentModelMetrics = modelsComp[selectedModel] || metricsData?.corrected_forecast_metrics;
  const corrMae = currentModelMetrics?.mae ?? 0.0;
  const improvement = currentModelMetrics?.mae_reduction_percentage ?? metricsData?.improvement.mae_reduction_percentage ?? 0.0;
  const bestModel = metricsData?.best_model ?? 'XGBoost';

  const predictions = predictionsData?.predictions ?? [];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* 1. Top KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Mô Hình Tối Ưu Nhất"
          value={bestModel.toUpperCase()}
          subtitle="Tự động chọn theo MAE thấp nhất"
          icon={Award}
          iconColor="text-amber-400"
        />
        <MetricCard
          title="MAE Dự Báo Thô"
          value={`${rawMae.toFixed(2)}°C`}
          subtitle="Sai số gốc từ Open-Meteo"
          icon={Thermometer}
          iconColor="text-rose-400"
        />
        <MetricCard
          title={`MAE Hiệu Chỉnh (${selectedModel.toUpperCase()})`}
          value={`${corrMae.toFixed(2)}°C`}
          subtitle="Sau khi áp dụng mô hình ML"
          delta={`${improvement >= 0 ? '-' : '+'}${Math.abs(improvement).toFixed(1)}%`}
          deltaType={improvement >= 0 ? 'positive' : 'negative'}
          icon={Sparkles}
          iconColor="text-emerald-400"
        />
        <MetricCard
          title="Mức Độ Giảm Sai Số"
          value={`${improvement >= 0 ? '+' : ''}${improvement.toFixed(1)}%`}
          subtitle="Hiệu quả cải thiện dự báo"
          icon={TrendingDown}
          iconColor="text-sky-400"
        />
      </div>

      {/* 2. Model Selector */}
      <ModelSelector
        selectedModel={selectedModel}
        onSelectModel={setSelectedModel}
        modelsComparison={modelsComp}
      />

      {/* 3. Main Temperature Chart */}
      {predictions.length > 0 ? (
        <TemperatureChart predictions={predictions} selectedModel={selectedModel} />
      ) : (
        <div className="glass-card rounded-2xl p-8 text-center text-slate-400">
          Chưa có dữ liệu dự báo. Vui lòng chạy Pipeline!
        </div>
      )}

      {/* 4. Secondary Charts Grid */}
      {predictions.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <WeatherIndicatorsChart predictions={predictions} />
          <ModelComparisonChart modelsComparison={modelsComp} />
        </div>
      )}

      {/* 5. 16-Day Weather Cards Grid */}
      {predictions.length > 0 && (
        <div>
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            🌤️ Dự Báo Chi Tiết 16 Ngày Tới (TP. Hồ Chí Minh)
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-8 gap-3">
            {predictions.slice(0, 16).map((item, idx) => (
              <WeatherCard
                key={item.date}
                prediction={item}
                selectedModel={selectedModel}
                isToday={idx === 0}
              />
            ))}
          </div>
        </div>
      )}

      {/* 6. Detailed Forecast Data Table */}
      {predictions.length > 0 && (
        <div className="glass-card rounded-2xl p-6 border border-white/10">
          <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
            <Table className="w-5 h-5 text-sky-400" />
            Bảng Dữ Liệu Khí Tượng Đa Chỉ Số
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-white/10">
                <tr>
                  <th className="py-3 px-4">Ngày</th>
                  <th className="py-3 px-4">Dự Báo Thô</th>
                  <th className="py-3 px-4">Sau Hiệu Chỉnh</th>
                  <th className="py-3 px-4">Sai Số (Bias)</th>
                  <th className="py-3 px-4">Độ Ẩm</th>
                  <th className="py-3 px-4">Mây Phủ</th>
                  <th className="py-3 px-4">Xác Suất Mưa</th>
                  <th className="py-3 px-4">Trạng Thái</th>
                  <th className="py-3 px-4">Nắng (h)</th>
                  <th className="py-3 px-4">Chỉ Số UV</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {predictions.slice(0, 16).map((row) => {
                  const modelPred = row.models?.[selectedModel];
                  const corr = modelPred?.corrected_temp_max ?? row.corrected_temp_max;
                  const bias = modelPred?.predicted_bias ?? row.predicted_bias;

                  return (
                    <tr key={row.date} className="hover:bg-white/5 transition-colors">
                      <td className="py-3 px-4 font-semibold text-white">{row.date}</td>
                      <td className="py-3 px-4 text-rose-400 font-medium">{row.raw_forecast_temp_max.toFixed(1)}°C</td>
                      <td className="py-3 px-4 text-emerald-400 font-bold">{corr.toFixed(1)}°C</td>
                      <td className="py-3 px-4 font-mono">{bias > 0 ? `+${bias.toFixed(2)}` : bias.toFixed(2)}°C</td>
                      <td className="py-3 px-4">{row.humidity}%</td>
                      <td className="py-3 px-4">{row.cloud_cover}%</td>
                      <td className="py-3 px-4">{row.rain_probability}%</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${row.will_rain ? 'bg-sky-500/20 text-sky-400 border border-sky-500/30' : 'bg-slate-800 text-slate-400'}`}>
                          {row.rain_status}
                        </span>
                      </td>
                      <td className="py-3 px-4">{row.sunshine_duration_hours}h</td>
                      <td className="py-3 px-4 font-semibold text-amber-400">{row.uv_index}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
