export interface ModelPrediction {
  predicted_bias: number;
  corrected_temp_max: number;
}

export interface PredictionItem {
  date: string;
  city: string;
  raw_forecast_temp_max: number;
  raw_forecast_temp_min: number;
  predicted_bias: number;
  corrected_temp_max: number;
  humidity: number;
  cloud_cover: number;
  rain_probability: number;
  sunshine_duration_hours: number;
  uv_index: number;
  will_rain: boolean;
  rain_status: string;
  models: Record<string, ModelPrediction>;
}

export interface PredictionsResponse {
  generated_at: string;
  city: string;
  total_forecast_days: number;
  default_model: string;
  available_models: string[];
  predictions: PredictionItem[];
}

export interface MetricValues {
  mae: number;
  rmse: number;
  r2: number;
  mae_reduction_percentage?: number;
}

export interface RainClassificationMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
}

export interface MetricsResponse {
  best_model: string;
  raw_forecast_metrics: MetricValues;
  corrected_forecast_metrics: MetricValues;
  improvement: {
    mae_reduction_percentage: number;
  };
  models_comparison: Record<string, MetricValues>;
  rain_classification_metrics?: RainClassificationMetrics;
}

export interface ModelInfo {
  id: string;
  name: string;
  type: string;
  description: string;
  is_default: boolean;
  status: 'trained' | 'not_trained';
  metrics?: MetricValues;
}

export interface ModelsCatalogResponse {
  total_models: number;
  default_model: string;
  models: ModelInfo[];
}

export interface SchedulerInfo {
  enabled: boolean;
  schedule: string;
  next_run?: string;
}

export interface PipelineStatusResponse {
  status: 'IDLE' | 'RUNNING' | 'SUCCESS' | 'FAILED';
  message: string;
  started_at?: string;
  finished_at?: string;
  duration_seconds: number;
  last_error?: string;
  scheduler?: SchedulerInfo;
}

export interface PipelineRunHistoryItem {
  id: number;
  status: string;
  duration_seconds: number;
  triggered_by: string;
  error_message?: string;
  created_at: string;
}

export interface PipelineHistoryResponse {
  total: number;
  history: PipelineRunHistoryItem[];
}

export interface HealthResponse {
  status: string;
  service: string;
  environment: string;
  database: string;
  scheduler: SchedulerInfo;
  python_version: string;
  timestamp: string;
}

export interface LogsResponse {
  total_lines: number;
  logs: string[];
}
