import React, { useState } from 'react';
import { Play, CheckCircle, AlertTriangle, Clock, History, Loader2, Database } from 'lucide-react';
import { PipelineStatusResponse, PipelineHistoryResponse } from '../types/weather';
import { weatherApi } from '../services/api';

interface PipelineControlPageProps {
  status: PipelineStatusResponse | null;
  history: PipelineHistoryResponse | null;
  onRefresh: () => void;
}

export const PipelineControlPage: React.FC<PipelineControlPageProps> = ({
  status,
  history,
  onRefresh,
}) => {
  const [triggering, setTriggering] = useState(false);
  const [triggerMessage, setTriggerMessage] = useState<string | null>(null);

  const handleRunPipeline = async () => {
    try {
      setTriggering(true);
      setTriggerMessage('Đang gửi yêu cầu kích hoạt 6 Stage MLOps Pipeline...');
      const res = await weatherApi.triggerPipelineRun();
      setTriggerMessage(res.message);
      setTimeout(() => {
        onRefresh();
        setTriggering(false);
      }, 3000);
    } catch (err: any) {
      setTriggerMessage(`Lỗi: ${err.message || 'Không thể kích hoạt pipeline'}`);
      setTriggering(false);
    }
  };

  const stages = [
    { id: '01', name: 'Data Ingestion', desc: 'Tải dữ liệu Open-Meteo (Nhiệt độ, Độ ẩm, Mây, Mưa, UV)' },
    { id: '02', name: 'Data Validation', desc: 'Kiểm chuẩn Schema và cấu trúc dữ liệu theo schema.yaml' },
    { id: '03', name: 'Data Transformation', desc: 'Kỹ nghệ đặc trưng Lags/Rolling bằng Apache PySpark' },
    { id: '04', name: 'Model Trainer', desc: 'Huấn luyện 4 thuật toán Hồi quy + Bộ phân loại mưa' },
    { id: '05', name: 'Model Evaluation', desc: 'Đo lường MAE, RMSE, R² và tạo bảng so sánh metrics' },
    { id: '06', name: 'Online Prediction', desc: 'Xuất dự báo 16 ngày và đồng bộ vào SQLite DB' },
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header & Trigger Action */}
      <div className="glass-card rounded-2xl p-6 border border-white/10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Play className="w-6 h-6 text-sky-400" />
            Điều Khiển & Thực Thi Pipeline MLOps
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Kích hoạt toàn bộ quy trình tự động từ nạp dữ liệu, PySpark transform tới huấn luyện đa mô hình.
          </p>
        </div>

        <button
          onClick={handleRunPipeline}
          disabled={triggering || status?.status === 'RUNNING'}
          className="flex items-center gap-3 px-6 py-3.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-bold shadow-lg shadow-sky-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
        >
          {triggering || status?.status === 'RUNNING' ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Đang Thực Thi...
            </>
          ) : (
            <>
              <Play className="w-5 h-5 fill-current" />
              Run Full Pipeline
            </>
          )}
        </button>
      </div>

      {triggerMessage && (
        <div className="p-4 rounded-xl bg-sky-500/10 border border-sky-500/30 text-sky-300 text-sm flex items-center gap-2">
          <Clock className="w-4 h-4" />
          {triggerMessage}
        </div>
      )}

      {/* 6 Stages Architecture Diagram */}
      <div className="glass-card rounded-2xl p-6 border border-white/10">
        <h3 className="text-base font-bold text-white mb-6">
          ⚙️ Quy Trình 6 Giai Đoạn (MLOps Stages Architecture)
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {stages.map((stg) => (
            <div
              key={stg.id}
              className="p-4 rounded-xl bg-slate-900/40 border border-white/5 flex items-start gap-3.5 hover:border-sky-500/30 transition-all"
            >
              <div className="w-8 h-8 rounded-lg bg-sky-500/20 text-sky-400 font-extrabold flex items-center justify-center text-xs shrink-0 border border-sky-500/30">
                {stg.id}
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">{stg.name}</h4>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">{stg.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Pipeline Status & SQLite History */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Status Info Box */}
        <div className="glass-card rounded-2xl p-6 border border-white/10">
          <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-sky-400" />
            Trạng Thái Lần Chạy Gần Nhất
          </h3>

          <div className="space-y-4 text-xs">
            <div className="flex items-center justify-between pb-3 border-b border-white/5">
              <span className="text-slate-400">Trạng thái:</span>
              <span className={`px-2.5 py-1 rounded-full font-bold uppercase text-[10px] ${
                status?.status === 'SUCCESS'
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : status?.status === 'RUNNING'
                  ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30 animate-pulse'
                  : 'bg-slate-800 text-slate-400'
              }`}>
                {status?.status || 'IDLE'}
              </span>
            </div>

            <div className="flex items-center justify-between pb-3 border-b border-white/5">
              <span className="text-slate-400">Thời gian bắt đầu:</span>
              <span className="text-white font-mono">{status?.started_at || 'N/A'}</span>
            </div>

            <div className="flex items-center justify-between pb-3 border-b border-white/5">
              <span className="text-slate-400">Thời gian thực thi:</span>
              <span className="text-white font-semibold">{status?.duration_seconds?.toFixed(2) || 0}s</span>
            </div>

            <div className="pt-1">
              <span className="text-slate-400 block mb-1">Thông điệp:</span>
              <p className="p-3 rounded-lg bg-slate-900/60 text-slate-300 text-[11px] font-mono leading-relaxed border border-white/5">
                {status?.message || 'Chưa có thông tin thực thi.'}
              </p>
            </div>
          </div>
        </div>

        {/* SQLite Run History Table */}
        <div className="glass-card rounded-2xl p-6 border border-white/10 lg:col-span-2">
          <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
            <Database className="w-5 h-5 text-indigo-400" />
            Lịch Sử Các Lượt Chạy (SQLite DB)
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-white/10">
                <tr>
                  <th className="py-2.5 px-3">Run ID</th>
                  <th className="py-2.5 px-3">Trạng Thái</th>
                  <th className="py-2.5 px-3">Thời Lượng</th>
                  <th className="py-2.5 px-3">Kích Hoạt Bởi</th>
                  <th className="py-2.5 px-3">Thời Gian</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {history?.history && history.history.length > 0 ? (
                  history.history.map((h) => (
                    <tr key={h.id} className="hover:bg-white/5">
                      <td className="py-2.5 px-3 font-mono font-bold text-white">#{h.id}</td>
                      <td className="py-2.5 px-3">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                          h.status === 'SUCCESS' ? 'text-emerald-400 bg-emerald-500/10' : 'text-rose-400 bg-rose-500/10'
                        }`}>
                          {h.status}
                        </span>
                      </td>
                      <td className="py-2.5 px-3">{h.duration_seconds.toFixed(2)}s</td>
                      <td className="py-2.5 px-3 text-slate-400">{h.triggered_by}</td>
                      <td className="py-2.5 px-3 text-slate-400 font-mono text-[11px]">{h.created_at}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="text-center py-6 text-slate-500">
                      Chưa có lịch sử chạy nào được lưu trong database.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
