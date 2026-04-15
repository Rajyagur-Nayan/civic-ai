import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface PotholeDetection {
  pothole_id: number;
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
  confidence: number;
  area: number;
  severity: 'low' | 'medium' | 'high';
  estimated_cost: number;
  workers_needed: number;
}

export interface DetectionResponse {
  image_url: string;
  detections: PotholeDetection[];
  total_potholes: number;
  total_cost: number;
  severity_distribution: {
    low: number;
    medium: number;
    high: number;
  };
}

export const detectPotholes = async (file: File): Promise<DetectionResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await axios.post<DetectionResponse>(
    `${API_BASE_URL}/detect`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );

  return response.data;
};

export const createImageUrl = (file: File): string => {
  return URL.createObjectURL(file);
};