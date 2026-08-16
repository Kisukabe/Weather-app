import axios from 'axios';
import {
  HealthResponse,
  MetricsResponse,
  PredictionsResponse,
  ModelsCatalogResponse,
  PipelineStatusResponse,
  PipelineHistoryResponse,
  LogsResponse,
} from '../types/weather';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';
const API_KEY = import.meta.env.VITE_API_KEY || 'weather-mlops-dev-secret-key';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
  },
});

export const weatherApi = {
  /** Kiểm tra sức khỏe hệ thống Backend */
  getHealth: async (): Promise<HealthResponse> => {
    const response = await apiClient.get<HealthResponse>('/health');
    return response.data;
  },

  /** Lấy các chỉ số đánh giá mô hình MAE, RMSE, R2 */
  getMetrics: async (): Promise<MetricsResponse> => {
    const response = await apiClient.get<MetricsResponse>('/api/v1/metrics');
    return response.data;
  },

  /** Lấy danh sách dự báo thời tiết 16 ngày */
  getPredictions: async (model?: string): Promise<PredictionsResponse> => {
    const params = model ? { model } : {};
    const response = await apiClient.get<PredictionsResponse>('/api/v1/predictions', { params });
    return response.data;
  },

  /** Lấy danh mục các mô hình trong Model Registry */
  getModels: async (): Promise<ModelsCatalogResponse> => {
    const response = await apiClient.get<ModelsCatalogResponse>('/api/v1/models');
    return response.data;
  },

  /** Lấy trạng thái thực thi hiện tại của Pipeline */
  getPipelineStatus: async (): Promise<PipelineStatusResponse> => {
    const response = await apiClient.get<PipelineStatusResponse>('/api/v1/pipeline/status');
    return response.data;
  },

  /** Lấy lịch sử các lượt chạy từ SQLite DB */
  getPipelineHistory: async (limit: number = 10): Promise<PipelineHistoryResponse> => {
    const response = await apiClient.get<PipelineHistoryResponse>(`/api/v1/pipeline/history?limit=${limit}`);
    return response.data;
  },

  /** Lấy logs hệ thống thời gian thực */
  getLogs: async (lines: number = 100): Promise<LogsResponse> => {
    const response = await apiClient.get<LogsResponse>(`/api/v1/logs?lines=${lines}`);
    return response.data;
  },

  /** Kích hoạt chạy MLOps Pipeline */
  triggerPipelineRun: async (): Promise<{ status: string; message: string }> => {
    const response = await apiClient.post('/api/v1/pipeline/run');
    return response.data;
  },
};
