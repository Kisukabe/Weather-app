import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  delta?: string;
  deltaType?: 'positive' | 'negative' | 'neutral';
  icon: LucideIcon;
  iconColor?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  delta,
  deltaType = 'positive',
  icon: Icon,
  iconColor = 'text-sky-400',
}) => {
  return (
    <div className="glass-card glass-card-hover rounded-2xl p-5 border border-white/10 relative overflow-hidden group">
      {/* Subtle Background Glow */}
      <div className="absolute -right-8 -top-8 w-24 h-24 bg-sky-500/10 rounded-full blur-2xl group-hover:bg-sky-500/20 transition-all" />

      <div className="flex items-start justify-between relative z-10">
        <div>
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</p>
          <h3 className="text-2xl font-extrabold text-white mt-1 tracking-tight">{value}</h3>
          {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
        </div>

        <div className={`p-3 rounded-xl bg-slate-900/60 border border-white/5 ${iconColor}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      {delta && (
        <div className="mt-3 flex items-center gap-1.5 text-xs font-semibold">
          <span
            className={`px-2 py-0.5 rounded-full ${
              deltaType === 'positive'
                ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                : deltaType === 'negative'
                ? 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                : 'bg-slate-700/40 text-slate-300'
            }`}
          >
            {delta}
          </span>
          <span className="text-slate-400">so với dự báo thô</span>
        </div>
      )}
    </div>
  );
};
