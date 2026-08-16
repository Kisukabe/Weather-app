import React from 'react';
import { Cpu, Zap, Trees, Activity, Check } from 'lucide-react';
import { MetricValues } from '../types/weather';

interface ModelSelectorProps {
  selectedModel: string;
  onSelectModel: (modelKey: string) => void;
  modelsComparison: Record<string, MetricValues>;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  selectedModel,
  onSelectModel,
  modelsComparison,
}) => {
  const models = [
    {
      id: 'xgboost',
      name: 'XGBoost',
      tag: 'Khuyên Dùng',
      tagColor: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      icon: Zap,
      desc: 'Gradient Boosting chuẩn xác cao nhất cho chuỗi thời gian',
    },
    {
      id: 'lightgbm',
      name: 'LightGBM',
      tag: 'Tốc Độ',
      tagColor: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
      icon: Cpu,
      desc: 'Tối ưu tốc độ suy luận và tiết kiệm RAM',
    },
    {
      id: 'random_forest',
      name: 'Random Forest',
      tag: 'Ổn Định',
      tagColor: 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30',
      icon: Trees,
      desc: 'Ensemble cổ điển, kháng quá khớp tốt',
    },
    {
      id: 'linear_regression',
      name: 'Ridge Regression',
      tag: 'Baseline',
      tagColor: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
      icon: Activity,
      desc: 'Mô hình tuyến tính cơ sở phục vụ đối chuẩn',
    },
  ];

  return (
    <div className="glass-card rounded-2xl p-5 border border-white/10 mb-8">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-4">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Cpu className="w-5 h-5 text-sky-400" />
            Chọn Mô Hình Hiệu Chỉnh (Model Registry)
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Thay đổi thuật toán Machine Learning để so sánh kết quả hiệu chỉnh thời gian thực.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {models.map((m) => {
          const isSelected = selectedModel === m.id;
          const Icon = m.icon;
          const metric = modelsComparison[m.id];
          const mae = metric?.mae ?? 0.0;
          const improvement = metric?.mae_reduction_percentage ?? 0.0;

          return (
            <button
              key={m.id}
              onClick={() => onSelectModel(m.id)}
              className={`p-4 rounded-xl border text-left transition-all relative overflow-hidden flex flex-col justify-between ${
                isSelected
                  ? 'bg-sky-500/10 border-sky-500 shadow-lg shadow-sky-500/10 ring-1 ring-sky-500'
                  : 'bg-slate-900/40 border-white/5 hover:bg-slate-900/70 hover:border-white/20'
              }`}
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <div className={`p-1.5 rounded-lg ${isSelected ? 'bg-sky-500 text-white' : 'bg-slate-800 text-slate-400'}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="text-sm font-bold text-white">{m.name}</span>
                  </div>

                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${m.tagColor}`}>
                    {m.tag}
                  </span>
                </div>

                <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">{m.desc}</p>
              </div>

              <div className="mt-3 pt-2.5 border-t border-white/5 flex items-center justify-between text-xs">
                <span className="text-slate-400">MAE: <strong className="text-white">{mae.toFixed(2)}°C</strong></span>
                <span className={`font-semibold ${improvement >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {improvement >= 0 ? `+${improvement.toFixed(1)}%` : `${improvement.toFixed(1)}%`}
                </span>
              </div>

              {isSelected && (
                <div className="absolute top-2 right-2">
                  <div className="w-4 h-4 rounded-full bg-sky-500 flex items-center justify-center">
                    <Check className="w-2.5 h-2.5 text-white" />
                  </div>
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};
