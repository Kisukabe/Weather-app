import React, { useState, useEffect } from 'react';
import { Terminal, Search, RefreshCw, Sliders, ShieldCheck } from 'lucide-react';
import { weatherApi } from '../services/api';

export const SystemLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<string[]>([]);
  const [totalLines, setTotalLines] = useState(0);
  const [lineLimit, setLineLimit] = useState(100);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const data = await weatherApi.getLogs(lineLimit);
      setLogs(data.logs || []);
      setTotalLines(data.total_lines || 0);
    } catch (err) {
      console.error('Lỗi khi tải logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [lineLimit]);

  useEffect(() => {
    let interval: any;
    if (autoRefresh) {
      interval = setInterval(fetchLogs, 4000);
    }
    return () => clearInterval(interval);
  }, [autoRefresh, lineLimit]);

  const filteredLogs = logs.filter((line) =>
    line.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Controls Bar */}
      <div className="glass-card rounded-2xl p-6 border border-white/10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Terminal className="w-6 h-6 text-sky-400" />
            Giám Sát Log Hệ Thống Thời Gian Thực
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Đọc log xoay vòng (Log Rotation tối đa 50MB) từ backend FastAPI & PySpark engine.
          </p>
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer bg-slate-900/60 px-3 py-2 rounded-xl border border-white/5">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-slate-700 text-sky-500 focus:ring-0"
            />
            <span>Tự động làm mới (4s)</span>
          </label>

          <button
            onClick={fetchLogs}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold border border-white/10 transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-sky-400' : ''}`} />
            Làm Mới
          </button>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="glass-card rounded-2xl p-4 border border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Lọc theo từ khóa (ERROR, Stage, PySpark)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-900/80 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
        </div>

        <div className="flex items-center gap-4 text-xs text-slate-400 w-full sm:w-auto justify-between sm:justify-end">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4" />
            <span>Hiển thị: </span>
            <select
              value={lineLimit}
              onChange={(e) => setLineLimit(Number(e.target.value))}
              className="bg-slate-900 border border-white/10 rounded-lg px-2 py-1 text-white text-xs focus:outline-none"
            >
              <option value={50}>50 dòng</option>
              <option value={100}>100 dòng</option>
              <option value={200}>200 dòng</option>
              <option value={500}>500 dòng</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5 text-emerald-400">
            <ShieldCheck className="w-4 h-4" />
            <span>{filteredLogs.length} dòng log</span>
          </div>
        </div>
      </div>

      {/* Terminal Log Console */}
      <div className="glass-card rounded-2xl p-4 border border-white/10 bg-slate-950/90 font-mono text-xs overflow-hidden shadow-2xl">
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/10 text-[11px] text-slate-400">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-rose-500/80 inline-block" />
            <span className="w-3 h-3 rounded-full bg-amber-500/80 inline-block" />
            <span className="w-3 h-3 rounded-full bg-emerald-500/80 inline-block" />
            <span className="ml-2 font-bold text-slate-300">logs/app.log (Rotating Buffer)</span>
          </div>
          <span>Tổng số dòng: {totalLines}</span>
        </div>

        <div className="max-h-[550px] overflow-y-auto space-y-1 pr-2">
          {filteredLogs.length > 0 ? (
            filteredLogs.map((line, idx) => {
              const isError = line.includes('ERROR') || line.includes('Exception');
              const isWarning = line.includes('WARNING');
              const isInfo = line.includes('INFO');

              return (
                <div
                  key={idx}
                  className={`py-0.5 px-2 rounded leading-relaxed text-[11px] ${
                    isError
                      ? 'bg-rose-950/40 text-rose-300 border-l-2 border-rose-500'
                      : isWarning
                      ? 'bg-amber-950/30 text-amber-300 border-l-2 border-amber-500'
                      : isInfo
                      ? 'text-slate-300 hover:bg-white/5'
                      : 'text-slate-400'
                  }`}
                >
                  {line}
                </div>
              );
            })
          ) : (
            <div className="text-center py-12 text-slate-500">
              Không tìm thấy dòng log nào khớp với từ khóa tìm kiếm.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
