import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface DetectionResult {
  bbox: number[];
  area: number;
  severity: 'small' | 'medium' | 'large';
  workers: number;
  cost: number;
  time: number;
  confidence: number;
}

export interface DetectionResponse {
  detections: DetectionResult[];
  total_potholes: number;
  total_cost: number;
  severity_distribution: {
    small: number;
    medium: number;
    large: number;
  };
  image_url?: string;
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