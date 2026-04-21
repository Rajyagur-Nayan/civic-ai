import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
  report_url?: string;
  original_url?: string;
}

export interface VideoDetectionResponse {
  detections: DetectionResult[];
  total_potholes: number;
  total_cost: number;
  severity_distribution: {
    small: number;
    medium: number;
    large: number;
  };
  report_url: string;
  video_url: string;
  original_url?: string;
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
export const detectVideo = async (file: File): Promise<VideoDetectionResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await axios.post<VideoDetectionResponse>(
    `${API_BASE_URL}/detect/video`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 900000, // 15 minutes for video processing (increased for larger files)
    }
  );

  return response.data;
};

/** @deprecated Use persistent original_url from backend response instead */
export const createImageUrl = (file: File): string => {
  return URL.createObjectURL(file);
};

export const getFullReportUrl = (reportPath: string): string => {
  return `${API_BASE_URL}${reportPath}`;
};